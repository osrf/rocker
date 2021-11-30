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

import grp
import os
import docker
import em
import getpass
import pwd
import pkgutil
from pathlib import Path
from shlex import quote
import subprocess
import sys

from .core import get_docker_client


def name_to_argument(name):
    return '--%s' % name.replace('_', '-')

from .core import RockerExtension

class Devices(RockerExtension):
    @staticmethod
    def get_name():
        return 'devices'

    def __init__(self):
        self.name = Devices.get_name()

    def get_preamble(self, cliargs):
        return ''

    def get_docker_args(self, cliargs):
        args = ''
        devices = cliargs.get('devices', None)
        for device in devices:
            if not os.path.exists(device):
                print("ERROR device %s doesn't exist. Skipping" % device)
                continue
            args += ' --device %s ' % device
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--devices',
            default=defaults.get('devices', None),
            nargs='*',
            help="Mount devices into the container.")


class DevHelpers(RockerExtension):
    @staticmethod
    def get_name():
        return 'dev_helpers'

    def __init__(self):
        self._env_subs = None
        self.name = DevHelpers.get_name()


    def get_environment_subs(self):
        if not self._env_subs:
            self._env_subs = {}
        return self._env_subs

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self.get_environment_subs())

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(DevHelpers.get_name()),
            action='store_true',
            default=defaults.get('dev_helpers', None),
            help="add development tools emacs and byobu to your environment")


class Name(RockerExtension):
    @staticmethod
    def get_name():
        return 'name'

    def __init__(self):
        self.name = Name.get_name()

    def get_preamble(self, cliargs):
        return ''

    def get_docker_args(self, cliargs):
        args = ''
        name = cliargs.get('name', None)
        if name:
            args += ' --name %s ' % name
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--name', default=defaults.get('name', ''),
                            help='Name of the container.')


class Network(RockerExtension):
    @staticmethod
    def get_name():
        return 'network'

    def __init__(self):
        self.name = Network.get_name()

    def get_preamble(self, cliargs):
        return ''

    def get_docker_args(self, cliargs):
        args = ''
        network = cliargs.get('network', None)
        args += ' --network %s ' % network
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        client = get_docker_client()
        parser.add_argument('--network', choices=[n['Name'] for n in client.networks()],
            default=defaults.get('network', None),
            help="What network configuration to use.")

class PulseAudio(RockerExtension):
    @staticmethod
    def get_name():
        return 'pulse'

    def __init__(self):
        self._env_subs = None
        self.name = PulseAudio.get_name()


    def get_environment_subs(self):
        if not self._env_subs:
            self._env_subs = {}
            self._env_subs['user_id'] = os.getuid()
            self._env_subs['XDG_RUNTIME_DIR'] = os.getenv('XDG_RUNTIME_DIR')
            self._env_subs['audio_group_id'] = grp.getgrnam('audio').gr_gid
        return self._env_subs

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self.get_environment_subs())

    def get_docker_args(self, cliargs):
        args = ' -v /run/user/%(user_id)s/pulse:/run/user/%(user_id)s/pulse --device /dev/snd '\
        ' -e PULSE_SERVER=unix:%(XDG_RUNTIME_DIR)s/pulse/native -v %(XDG_RUNTIME_DIR)s/pulse/native:%(XDG_RUNTIME_DIR)s/pulse/native --group-add %(audio_group_id)s '
        return args % self.get_environment_subs()

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(PulseAudio.get_name()),
            action='store_true',
            default=defaults.get(PulseAudio.get_name(), None),
            help="mount pulse audio devices")


class HomeDir(RockerExtension):
    @staticmethod
    def get_name():
        return 'home'

    def __init__(self):
        self.name = HomeDir.get_name()

    def get_docker_args(self, cliargs):
        return ' -v %s:%s ' % (Path.home(), Path.home())

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(HomeDir.get_name()),
            action='store_true',
            default=defaults.get(HomeDir.get_name(), None),
            help="mount the users home directory")


class User(RockerExtension):
    @staticmethod
    def get_name():
        return 'user'

    def get_environment_subs(self):
        if not self._env_subs:
            user_vars = ['name', 'uid', 'gid', 'gecos','dir', 'shell']
            userinfo = pwd.getpwuid(os.getuid())
            self._env_subs = {
                k: getattr(userinfo, 'pw_' + k)
                for k in user_vars }
        return self._env_subs

    def __init__(self):
        self._env_subs = None
        self.name = User.get_name()

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        substitutions = self.get_environment_subs()
        if 'user_override_name' in cliargs and cliargs['user_override_name']:
            substitutions['name'] = cliargs['user_override_name']
            substitutions['dir'] = os.path.join('/home/', cliargs['user_override_name'])
        substitutions['user_preserve_home'] = True if 'user_preserve_home' in cliargs and cliargs['user_preserve_home'] else False
        substitutions['home_extension_active'] = True if 'home' in cliargs and cliargs['home'] else False
        return em.expand(snippet, substitutions)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(User.get_name()),
            action='store_true',
            default=defaults.get('user', None),
            help="mount the current user's id and run as that user")
        parser.add_argument('--user-override-name',
            action='store',
            default=defaults.get('user-override-name', None),
            help="override the current user's name")
        parser.add_argument('--user-preserve-home',
            action='store_true',
            default=defaults.get('user-preserve-home', False),
            help="Do not delete home directory if it exists when making a new user.")


class Environment(RockerExtension):
    @staticmethod
    def get_name():
        return 'env'

    def __init__(self):
        self.name = Environment.get_name()

    def get_snippet(self, cli_args):
        return ''

    def get_docker_args(self, cli_args):
        args = ['']

        if cli_args.get('env'):
            envs = [ x for sublist in cli_args['env'] for x in sublist]
            for env in envs:
                args.append('-e {0}'.format(quote(env)))

        if cli_args.get('env_file'):
            env_files = [ x for sublist in cli_args['env_file'] for x in sublist]
            for env_file in env_files:
                args.append('--env-file {0}'.format(quote(env_file)))

        return ' '.join(args)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--env', '-e',
            metavar='NAME[=VALUE]',
            type=str,
            nargs='+',
            action='append',
            default=defaults.get(Environment.get_name(), []),
            help='set environment variables')
        parser.add_argument('--env-file',
            type=str,
            nargs=1,
            action='append',
            help='set environment variable via env-file')

    @classmethod
    def check_args_for_activation(cls, cli_args):
        """ Returns true if the arguments indicate that this extension should be activated otherwise false."""
        return True if cli_args.get('env') or cli_args.get('env_file') else False


class Privileged(RockerExtension):
    """Add --privileged to docker arguments."""
    @staticmethod
    def get_name():
        return 'privileged'

    def __init__(self):
        self.name = Privileged.get_name()

    def get_snippet(self, cli_args):
        return ''

    def get_docker_args(self, cli_args):
        return ' --privileged'

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(Privileged.get_name()),
                            action='store_true',
                            default=defaults.get(Privileged.get_name(), None),
                            help="give extended privileges to the container")
