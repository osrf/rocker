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


class Mount(RockerExtension):

    name = 'mount'

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
        args = ['']

        # flatten cli_args['mount']
        mounts = [ x for sublist in cli_args['mount'] for x in sublist]

        for mount in mounts:
            elems = mount.split(':')
            host_dir = os.path.abspath(elems[0])
            if len(elems) == 1:
                args.append('-v {0}:{0}'.format(host_dir))
            elif len(elems) == 2:
                container_dir = elems[1]
                args.append('-v {0}:{1}'.format(host_dir, container_dir))
            elif len(elems) == 3:
                container_dir = elems[1]
                options = elems[2]
                args.append('-v {0}:{1}:{2}'.format(host_dir, container_dir, options))
            else:
                raise ArgumentTypeError('--mount expects arguments in format HOST-DIR[:CONTAINER-DIR[:OPTIONS]]')

        return ' '.join(args)

    @staticmethod
    def register_arguments(parser):
        parser.add_argument('--mount',
            metavar='HOST-DIR[:CONTAINER-DIR[:OPTIONS]]',
            type=str,
            nargs='+',
            action='append',
            help='mount volumes in container')
