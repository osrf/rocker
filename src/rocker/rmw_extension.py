# Copyright 2024 Open Source Robotics Foundation

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
import pkgutil

from .em import empy_expand
from rocker.extensions import RockerExtension
from rocker.extensions import name_to_argument


class RMW(RockerExtension):
    rmw_map = {
        'cyclonedds': ['ros-${ROS_DISTRO}-rmw-cyclonedds-cpp'],
        'fastrtps'  : ['ros-${ROS_DISTRO}-rmw-fastrtps-cpp'],
        # TODO(tfoote) Enable connext with license acceptance method
        # 'connextdds': ['ros-${ROS_DISTRO}-rmw-connextdds'],
    }

    @staticmethod
    def get_package_names(rmw_name):
        return RMW.rmw_map[rmw_name]

    @staticmethod
    def get_name():
        return 'rmw'

    def __init__(self):
        self._env_subs = None
        self.name = RMW.get_name()

    def get_docker_args(self, cli_args):
        rmw_config = cli_args.get('rmw')
        if not rmw_config:
            return '' # not active
        implementation = rmw_config[0]
        args = f' -e RMW_IMPLEMENTATION=rmw_{implementation}_cpp'
        return args #% self.get_environment_subs()

    def get_environment_subs(self):
        if not self._env_subs:
            self._env_subs = {}
        return self._env_subs

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % RMW.get_name()).decode('utf-8')
        data = self.get_environment_subs()
        # data['rosdistro'] = cliargs.get('rosdistro', 'rolling')
        rmw = cliargs.get('rmw', None)
        if rmw:
            rmw = rmw[0]
        else:
            return '' # rmw not active
        data['rmw'] = rmw
        data['packages'] = RMW.get_package_names(rmw)
        # data['rosdistro'] = 'rolling'
        return empy_expand(snippet, data)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(RMW.get_name()),
            default=defaults.get('rmw', None),
            nargs=1,
            choices=RMW.rmw_map.keys(),
            help="Set the default RMW implementation")

        # parser.add_argument('rosdistro',
        #     default=defaults.get('rosdistro', None),
        #     help="Set the default rosdistro, else autodetect")
