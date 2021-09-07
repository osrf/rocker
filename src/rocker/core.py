#!/usr/bin/env python3

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
import re
import sys

import pkg_resources
import pkgutil
from requests.exceptions import ConnectionError
import shlex
import subprocess
import tempfile

import docker
import pexpect

import fcntl
import signal
import struct
import termios

SYS_STDOUT = sys.stdout

OPERATIONS_DRY_RUN = 'dry-run'
OPERATIONS_NON_INTERACTIVE = 'non-interactive'
OPERATIONS_INTERACTIVE = 'interactive'
OPERATION_MODES = [OPERATIONS_INTERACTIVE, OPERATIONS_NON_INTERACTIVE , OPERATIONS_DRY_RUN]


class DependencyMissing(RuntimeError):
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

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
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


    def get_active_extensions(self, cli_args):
        active_extensions = [e() for e in self.available_plugins.values() if e.check_args_for_activation(cli_args) and e.get_name() not in cli_args['extension_blacklist']]
        active_extensions.sort(key=lambda e:e.get_name().startswith('user'))
        return active_extensions


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
    except (docker.errors.APIError, ConnectionError) as ex:
        raise DependencyMissing('Docker Client failed to connect to docker daemon.'
            ' Please verify that docker is installed and running.'
            ' As well as that you have permission to access the docker daemon.'
            ' This is usually by being a member of the docker group.')


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
        for file_name, contents in active_extension.get_files(args_dict).items():
            if os.path.isabs(file_name):
                print('WARNING!! Path %s from extension %s is absolute'
                      'and cannot be written out, skipping' % (file_name, active_extension.get_name()))
                continue
            full_path = os.path.join(target_directory, file_name)
            with open(full_path, 'w') as fh:
                print('Writing to file %s' % full_path)
                fh.write(contents)
    return all_files


def generate_dockerfile(extensions, args_dict, base_image):
    dockerfile_str = ''
    for el in extensions:
        dockerfile_str += '# Preamble from extension [%s]\n' % el.name
        dockerfile_str += el.get_preamble(args_dict) + '\n'
    dockerfile_str += '\nFROM %s\n' % base_image
    dockerfile_str += 'USER root\n'
    for el in extensions:
        dockerfile_str += '# Snippet from extension [%s]\n' % el.name
        dockerfile_str += el.get_snippet(args_dict) + '\n'
    return dockerfile_str


def list_plugins(extension_point='rocker.extensions'):
    unordered_plugins = {
    entry_point.name: entry_point.load()
    for entry_point
    in pkg_resources.iter_entry_points(extension_point)
    }
    # Order plugins by extension point name for consistent ordering below
    plugin_names = list(unordered_plugins.keys())
    plugin_names.sort()
    return OrderedDict([(k, unordered_plugins[k]) for k in plugin_names])


def get_rocker_version():
    return pkg_resources.require('rocker')[0].version
