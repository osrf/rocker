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


class Volume(RockerExtension):

    ARG_DOCKER_VOLUME = "-v"
    ARG_ROCKER_VOLUME = "--volume"
    name = 'volume'

    @classmethod
    def get_name(cls):
        return cls.name

    def get_docker_args(self, cli_args):
        """
        @param cli_args: {'volume': [[%arg%]]}
            - 'volume' is fixed.
            - %arg% can be:
               - %path_host%: a path on the host. Same path will be populated in
                   the container.
               - %path_host%:%path_cont%
               - %path_host%:%path_cont%:%option%
        """
        args = ['']

        # flatten cli_args['volume']
        volumes = [ x for sublist in cli_args[self.name] for x in sublist]

        for volume in volumes:
            elems = volume.split(':')
            host_dir = os.path.abspath(elems[0])
            if len(elems) == 1:
                args.append('{0} {1}:{1}'.format(self.ARG_DOCKER_VOLUME, host_dir))
            elif len(elems) == 2:
                container_dir = elems[1]
                args.append('{0} {1}:{2}'.format(self.ARG_DOCKER_VOLUME, host_dir, container_dir))
            elif len(elems) == 3:
                container_dir = elems[1]
                options = elems[2]
                args.append('{0} {1}:{2}:{3}'.format(self.ARG_DOCKER_VOLUME, host_dir, container_dir, options))
            else:
                raise ArgumentTypeError(
                    '{} expects arguments in format HOST-DIR[:CONTAINER-DIR[:OPTIONS]]'.format(self.ARG_ROCKER_VOLUME))

        return ' '.join(args)

    @staticmethod
    def register_arguments(parser):
        parser.add_argument(Volume.ARG_ROCKER_VOLUME,
            metavar='HOST-DIR[:CONTAINER-DIR[:OPTIONS]]',
            type=str,
            nargs='+',
            action='append',
            help='volume(s) to map into the container. The last path must be followed by two dashes "--"')
