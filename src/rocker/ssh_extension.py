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
import shlex

from rocker.extensions import RockerExtension


class Ssh(RockerExtension):

    name = 'ssh'

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
        if 'SSH_AUTH_SOCK' in os.environ:
            args += ' -e SSH_AUTH_SOCK -v ' + shlex.quote('{SSH_AUTH_SOCK}:{SSH_AUTH_SOCK}'.format(**os.environ))
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--ssh',
            action='store_true',
            default=defaults.get(Ssh.get_name(), None),
            help="Forward SSH agent into the container")
