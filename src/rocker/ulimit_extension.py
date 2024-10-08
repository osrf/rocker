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


class Ulimit(RockerExtension):

    ARG_DOCKER_ULIMIT = "--ulimit"
    ARG_ROCKER_VOLUME = "--ulimit"

    @staticmethod
    def get_name():
        return 'ulimit'

    def get_docker_args(self, cliargs):
        return ''

    @staticmethod
    def register_arguments(parser, defaults):
        parser.add_argument(Ulimit.ARG_ROCKER_VOLUME,
                            type=str,
                            nargs='+',
                            action='append',
                            help='ulimit options to add into the container.')
