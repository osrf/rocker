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

from argparse import ArgumentTypeError
import os
from rocker.extensions import RockerExtension


class Git(RockerExtension):

    name = 'git'

    @classmethod
    def get_name(cls):
        return cls.name

    def precondition_environment(self, cli_args):
        pass

    def validate_environment(self, cli_args):
        pass

    def get_preamble(self, cli_args):
        return ''

    def get_snippet(self, cli_args):
        return ''

    def get_docker_args(self, cli_args):
        args = ''
        system_gitconfig = '/etc/gitconfig'
        user_gitconfig = os.path.expanduser('~/.gitconfig')
        user_gitconfig_target = '/root/.gitconfig'
        if 'user' in cli_args and cli_args['user']:
            user_gitconfig_target = user_gitconfig
        if os.path.exists(system_gitconfig):
            args += ' -v {system_gitconfig}:{system_gitconfig}:ro'.format(**locals())
        if os.path.exists(user_gitconfig):
            args += ' -v {user_gitconfig}:{user_gitconfig_target}:ro'.format(**locals())
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--git',
            action='store_true',
            default=defaults.get(Git.get_name(), None),
            help="Use the global Git settings from the host (/etc/gitconfig and ~/.gitconfig)")
