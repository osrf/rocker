# Copyright 2019 Open Source Robotics Foundation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict
import io
import os
import pwd
import re
import sys

# importlib-metadata dependency can be removed when RHEL8 and other 3.6 based systems are not in support cycles
if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata


import pkgutil
from requests.exceptions import ConnectionError
import shlex
import subprocess
import tempfile

import docker
import pexpect

import fcntl
from pathlib import Path
import signal
import struct
import termios
import typing

SYS_STDOUT = sys.stdout

OPERATIONS_DRY_RUN = 'dry-run'
OPERATIONS_NON_INTERACTIVE = 'non-interactive'
OPERATIONS_INTERACTIVE = 'interactive'
OPERATION_MODES = [OPERATIONS_INTERACTIVE, OPERATIONS_NON_INTERACTIVE , OPERATIONS_DRY_RUN]


class DependencyMissing(RuntimeError):
    pass


class ExtensionError(RuntimeError):
    pass


class RockerExtension(object):
    """The base class for Rocker extension points"""

    def precondition_environment(self, cliargs):
        """Modify the local environment such as setup tempfiles"""
        pass

    def validate_environment(self, cliargs):
        """ Check that the environment is something that can be used.
        This will check that we're on the right base OS and that the 
        necessary resources are available, like hardware."""
        pass

    def invoke_after(self, cliargs) -> typing.Set[str]:
        """
        This extension should be loaded after the extensions in the returned
        set. These extensions are not required to be present, but if they are,
        they will be loaded before this extension.
        """
        return set()

    def required(self, cliargs) -> typing.Set[str]:
        """
        Ensures the specified extensions are present and combined with
        this extension. If the required extension should be loaded before
        this extension, it should also be added to the `invoke_after` set.
        """
        return set()

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        """ Get a dockerfile snippet to be executed as ROOT."""
        return ''

    def get_user_snippet(self, cliargs):
        """ Get a dockerfile snippet to be executed after switchingto the expected USER."""
        return ''

    def get_files(self, cliargs):
        """Get a dict of local filenames and content to write into them"""
        return {}

    @staticmethod
    def get_name():
        raise NotImplementedError

    def get_docker_args(self, cliargs):
        return ''

    @classmethod
    def check_args_for_activation(cls, cli_args):
        """ Returns true if the arguments indicate that this extension should be activated otherwise false.
        The default implementation looks for the extension name has any value.
        It is recommended to override this unless it's just a flag to enable the plugin."""
        return True if cli_args.get(cls.get_name()) else False

    @staticmethod
    def register_arguments(parser, defaults={}):
        raise NotImplementedError


class RockerExtensionManager:
    def __init__(self):
        self.available_plugins = list_plugins()
    
    def extend_cli_parser(self, parser, default_args={}):
        for p in self.available_plugins.values():
            try:
                p.register_arguments(parser, default_args)
            except TypeError as ex:
                print("Extension %s doesn't support default arguments. Please extend it." % p.get_name())
                p.register_arguments(parser)
        parser.add_argument('--mode', choices=OPERATION_MODES,
            default=OPERATIONS_INTERACTIVE,
            help="Choose mode of operation for rocker")
        parser.add_argument('--image-name', default=None,
            help='Tag the final image, useful with dry-run')
        parser.add_argument('--extension-blacklist', nargs='*',
            default=[],
            help='Prevent any of these extensions from being loaded.')
        parser.add_argument('--strict-extension-selection', action='store_true',
            help='When enabled, causes an error if required extensions are not explicitly '
            'called out on the command line. Otherwise, the required extensions will '
            'automatically be loaded if available.')


    def get_active_extensions(self, cli_args):
        """
        Checks for missing dependencies (specified by each extension's
        required() method) and additionally sorts them.
        """
        def sort_extensions(extensions, cli_args):

            def topological_sort(source: typing.Dict[str, typing.Set[str]]) -> typing.List[str]:
                """Perform a topological sort on names and dependencies and returns the sorted list of names."""
                names = set(source.keys())
                # prune optional dependencies if they are not present (at this point the required check has already occurred)
                pending = [(name, dependencies.intersection(names)) for name, dependencies in source.items()]
                emitted = []
                while pending:
                    next_pending = []
                    next_emitted = []
                    for entry in pending:
                        name, deps = entry
                        deps.difference_update(emitted)  # remove dependencies already emitted
                        if deps:  # still has dependencies? recheck during next pass
                            next_pending.append(entry)
                        else:  # no more dependencies? time to emit
                            yield name
                            next_emitted.append(name)  # remember what was emitted for difference_update()
                    if not next_emitted:
                        raise ExtensionError("Cyclic dependancy detected: %r" % (next_pending,))
                    pending = next_pending
                    emitted = next_emitted

            extension_graph = {name: cls.invoke_after(cli_args) for name, cls in sorted(extensions.items())}
            active_extension_list = [extensions[name] for name in topological_sort(extension_graph)]
            return active_extension_list

        active_extensions = {}
        find_reqs = set([name for name, cls in self.available_plugins.items() if cls.check_args_for_activation(cli_args)])
        while find_reqs:
            name = find_reqs.pop()

            if name in self.available_plugins.keys():
                if name not in cli_args['extension_blacklist']:
                    ext = self.available_plugins[name]()
                    active_extensions[name] = ext
                else:
                    raise ExtensionError(f"Extension '{name}' is blacklisted.")
            else:
                raise ExtensionError(f"Extension '{name}' not found. Is it installed?")

            # add additional reqs for processing not already known about
            known_reqs = set(active_extensions.keys()).union(find_reqs)
            missing_reqs = ext.required(cli_args).difference(known_reqs)
            if missing_reqs:
                if cli_args['strict_extension_selection']:
                    raise ExtensionError(f"Extension '{name}' is missing required extension(s) {list(missing_reqs)}")
                else:
                    print(f"Adding implicilty required extension(s) {list(missing_reqs)} required by extension '{name}'")
                    find_reqs = find_reqs.union(missing_reqs)

        return sort_extensions(active_extensions, cli_args)

def get_docker_client():
    """Simple helper function for pre 2.0 imports"""
    try:
        try:
            docker_client = docker.from_env().api
        except AttributeError:
            # docker-py pre 2.0
            docker_client = docker.Client()
        # Validate that the server is available
        docker_client.ping()
        return docker_client
    except (docker.errors.DockerException, docker.errors.APIError, ConnectionError) as ex:
        raise DependencyMissing('Docker Client failed to connect to docker daemon.'
            ' Please verify that docker is installed and running.'
            ' As well as that you have permission to access the docker daemon.'
            ' This is usually by being a member of the docker group.'
            ' The underlying error was:\n"""\n%s\n"""\n' % ex)

def get_user_name():
    userinfo = pwd.getpwuid(os.getuid())
    return getattr(userinfo, 'pw_' + 'name')

def docker_build(docker_client = None, output_callback = None, **kwargs):
    image_id = None

    if not docker_client:
        docker_client = get_docker_client()
    kwargs['decode'] = True
    for line in docker_client.build(**kwargs):
        output = line.get('stream', '').rstrip()
        if not output:
            # print("non stream data", line)
            continue
        if output_callback is not None:
            output_callback(output)

        match = re.match(r'Successfully built ([a-z0-9]{12})', output)
        if match:
            image_id = match.group(1)

    if image_id:
        return image_id
    else:
        print("no more output and success not detected")
        return None


class SIGWINCHPassthrough(object):
    def __init__ (self, process):
        self.process = process
        self.active = os.isatty(sys.__stdout__.fileno())

    def set_window_size(self):
        s = struct.pack("HHHH", 0, 0, 0, 0)
        try:
            a = struct.unpack('hhhh', fcntl.ioctl(SYS_STDOUT.fileno(),
                termios.TIOCGWINSZ , s))
        except (io.UnsupportedOperation, AttributeError) as ex:
            # We're not interacting with a real stdout, don't do the resize
            # This happens when we're in something like unit tests.
            return
        if not self.process.closed:
            self.process.setwinsize(a[0],a[1])


    def __enter__(self):
        # Short circuit if not a tty
        if not self.active:
            return self
        # Expected function prototype for signal handling
        # ignoring unused arguments
        def sigwinch_passthrough (sig, data):
            self.set_window_size()
    
        signal.signal(signal.SIGWINCH, sigwinch_passthrough)
 
        # Initially set the window size since it may not be default sized
        self.set_window_size()
        return self

    # Clean up signal handler before returning.
    def __exit__(self, exc_type, exc_value, traceback):
        if not self.active:
            return
        # This was causing hangs and resolved as referenced 
        # here: https://github.com/pexpect/pexpect/issues/465
        signal.signal(signal.SIGWINCH, signal.SIG_DFL)

class DockerImageGenerator(object):
    def __init__(self, active_extensions, cliargs, base_image):
        self.built = False
        self.cliargs = cliargs
        self.cliargs['base_image'] = base_image # inject base image into arguments for use
        self.active_extensions = active_extensions

        self.dockerfile = generate_dockerfile(active_extensions, self.cliargs, base_image)
        self.image_id = None

    def build(self, **kwargs):
        with tempfile.TemporaryDirectory() as td:
            df = os.path.join(td, 'Dockerfile')
            print("Writing dockerfile to %s" % df)
            with open(df, 'w') as fh:
                fh.write(self.dockerfile)
            print('vvvvvv')
            print(self.dockerfile)
            print('^^^^^^')
            write_files(self.active_extensions, self.cliargs, td)
            arguments = {}
            arguments['path'] = td
            arguments['rm'] = True
            arguments['nocache'] = kwargs.get('nocache', False)
            arguments['pull'] = kwargs.get('pull', False)
            image_name = kwargs.get('image_name', None)
            if image_name:
                print(f"Running docker tag {self.image_id} {image_name}")
                arguments['tag'] = image_name
            print("Building docker file with arguments: ", arguments)
            try:
                self.image_id = docker_build(
                    **arguments,
                    output_callback=lambda output: print("building > %s" % output)
                )
                if self.image_id:
                    self.built = True
                    return 0
                else:
                    return 2

            except docker.errors.APIError as ex:
                print("Docker build failed\n", ex)
                return 1

    def get_operating_mode(self, args):
        operating_mode = args.get('mode')
        # Default to non-interactive if unset
        if operating_mode not in OPERATION_MODES:
            operating_mode = OPERATIONS_NON_INTERACTIVE
        if operating_mode == OPERATIONS_INTERACTIVE and not os.isatty(sys.__stdin__.fileno()):
            operating_mode = OPERATIONS_NON_INTERACTIVE
            print("No tty detected for stdin forcing non-interactive")
        return operating_mode

    def generate_docker_cmd(self, command='', **kwargs):
        docker_args = ''

        for e in self.active_extensions:
            docker_args += e.get_docker_args(self.cliargs)

        image_name = kwargs.get('image_name', None)
        if image_name:
            image = image_name
        else:
            image = self.image_id
        cmd = "docker run"
        if(not kwargs.get('nocleanup')):
            # remove container only if --nocleanup is not present
            cmd += " --rm"

        operating_mode = self.get_operating_mode(kwargs)
        if operating_mode != OPERATIONS_NON_INTERACTIVE:
            # only disable for OPERATIONS_NON_INTERACTIVE
            cmd += " -it"
        cmd += "%(docker_args)s %(image)s %(command)s" % locals()
        return cmd

    def run(self, command='', **kwargs):
        if not self.built:
            print("Cannot run if build has not passed.")
            return 1

        for e in self.active_extensions:
            try:
                e.precondition_environment(self.cliargs)
            except subprocess.CalledProcessError as ex:
                print("ERROR! Failed to precondition for extension [%s] with error: %s\ndeactivating" % (e.get_name(), ex))
                return 1

        cmd = self.generate_docker_cmd(command, **kwargs)
        operating_mode = self.get_operating_mode(kwargs)

        #   $DOCKER_OPTS \
        if operating_mode == OPERATIONS_DRY_RUN:
            print("Run this command: \n\n\n")
            print(cmd)
            return 0
        elif operating_mode == OPERATIONS_NON_INTERACTIVE:
            try:
                print("Executing command: ")
                print(cmd)
                p = subprocess.run(shlex.split(cmd), check=True, stderr=subprocess.STDOUT)
                return p.returncode
            except subprocess.CalledProcessError as ex:
                print("Non-interactive Docker run failed\n", ex)
                return ex.returncode
        else:
            try:
                print("Executing command: ")
                print(cmd)
                p = pexpect.spawn(cmd)
                with SIGWINCHPassthrough(p):
                    p.interact()
                p.close(force=True)
                return p.exitstatus
            except pexpect.ExceptionPexpect as ex:
                print("Docker run failed\n", ex)
                return ex.returncode


def write_files(extensions, args_dict, target_directory):
    all_files = {}
    for active_extension in extensions:
        for file_path, contents in active_extension.get_files(args_dict).items():
            if os.path.isabs(file_path):
                print('WARNING!! Path %s from extension %s is absolute'
                      'and cannot be written out, skipping' % (file_path, active_extension.get_name()))
                continue
            full_path = os.path.join(target_directory, file_path)
            if Path(target_directory).resolve() not in Path(full_path).resolve().parents:
                print('WARNING!! Path %s from extension %s is outside target directory'
                      'and cannot be written out, skipping' % (file_path, active_extension.get_name()))
                continue
            Path(os.path.dirname(full_path)).mkdir(exist_ok=True, parents=True)
            mode = 'wb' if isinstance(contents, bytes) else 'w' # check to see if contents should be written as binary
            with open(full_path, mode) as fh:
                print('Writing to file %s' % full_path)
                fh.write(contents)
    return all_files


def generate_dockerfile(extensions, args_dict, base_image):
    dockerfile_str = ''
    # Preamble snippets
    for el in extensions:
        dockerfile_str += '# Preamble from extension [%s]\n' % el.get_name()
        dockerfile_str += el.get_preamble(args_dict) + '\n'
    dockerfile_str += '\nFROM %s\n' % base_image
    # ROOT snippets
    dockerfile_str += 'USER root\n'
    for el in extensions:
        dockerfile_str += '# Snippet from extension [%s]\n' % el.get_name()
        dockerfile_str += el.get_snippet(args_dict) + '\n'
    # Set USER if user extension activated
    if 'user' in args_dict and args_dict['user']:
        if 'user_override_name' in args_dict and args_dict['user_override_name']:
            username = args_dict['user_override_name']
        else:
            username = get_user_name()
        dockerfile_str += f'USER {username}\n'
    # USER snippets
    for el in extensions:
        dockerfile_str += '# User Snippet from extension [%s]\n' % el.get_name()
        dockerfile_str += el.get_user_snippet(args_dict) + '\n'
    return dockerfile_str


def list_entry_points():
    entry_points = importlib_metadata.entry_points()
    if hasattr(entry_points, 'select'):
        styles_groups = entry_points.select(group='flake8_import_order.styles')
    else:
        styles_groups = entry_points.get('flake8_import_order.styles', [])

    return styles_groups

def list_plugins(extension_point='rocker.extensions'):

    all_entry_points = importlib_metadata.entry_points()
    if hasattr(all_entry_points, 'select'):
        rocker_extensions = all_entry_points.select(group=extension_point)
    else:
        rocker_extensions = all_entry_points.get(extension_point, [])

    unordered_plugins = {
    entry_point.name: entry_point.load()
    for entry_point in rocker_extensions
    }
    # Order plugins by extension point name for consistent ordering below
    plugin_names = list(unordered_plugins.keys())
    plugin_names.sort()
    return OrderedDict([(k, unordered_plugins[k]) for k in plugin_names])


def get_rocker_version():
    return importlib_metadata.version('rocker')
