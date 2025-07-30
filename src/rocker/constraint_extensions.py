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

import re
from .core import RockerExtension


def validate_memory_format(value):
    """Validate memory format supporting Docker byte-value specification.
    
    Supports formats like: 2b, 1024kb, 300m, 1gb, etc.
    """
    if not re.match(r'^\d+(b|kb|mb|gb|k|m|g|K|M|G)?$', value):
        from argparse import ArgumentTypeError
        raise ArgumentTypeError(f"Invalid memory format: {value}. Expected format: number[b|kb|mb|gb|k|m|g]")
    return value


class ShmSize(RockerExtension):
    @staticmethod
    def get_name():
        return 'shm_size'

    def __init__(self):
        self.name = ShmSize.get_name()

    def get_preamble(self, cliargs):
        return ''

    def get_docker_args(self, cliargs):
        args = ''
        shm_size = cliargs.get('shm_size', None)
        if shm_size:
            args += f' --shm-size {shm_size} '
        return args

    def get_build_args(self, cliargs):
        """Add shm-size build argument if shm_size_build is specified"""
        build_args = {}
        shm_size_build = cliargs.get('shm_size_build', None)
        if shm_size_build:
            build_args['shm_size'] = shm_size_build
        return build_args

    @classmethod
    def check_args_for_activation(cls, cli_args):
        """Returns true if the arguments indicate that this extension should be activated otherwise false."""
        return True if cli_args.get('shm_size') or cli_args.get('shm_size_build') else False

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--shm-size',
                            type=validate_memory_format,
                            default=defaults.get('shm_size', None),
                            help="Set the size of the shared memory for the container (e.g., 512m, 1g).")
        parser.add_argument('--shm-size-build',
                            dest='shm_size_build',
                            type=validate_memory_format,
                            default=defaults.get('shm_size_build', None),
                            help="Set the size of the shared memory for build containers (e.g., 512m, 1g).")


class CpuLimits(RockerExtension):
    @staticmethod
    def get_name():
        return 'cpu_limits'

    def __init__(self):
        self.name = CpuLimits.get_name()

    def get_preamble(self, cliargs):
        return ''

    def get_docker_args(self, cliargs):
        args = ''
        cpus = cliargs.get('cpus', None)
        if cpus:
            args += f' --cpus {cpus} '
        return args

    @staticmethod
    def _validate_cpu_format(value):
        """Validate CPU format (e.g., '1.5', '2')."""
        try:
            float(value)
            return value
        except ValueError:
            from argparse import ArgumentTypeError
            raise ArgumentTypeError("Expected a floating point number (e.g., '1.5')")

    @classmethod
    def check_args_for_activation(cls, cli_args):
        """Returns true if the arguments indicate that this extension should be activated otherwise false."""
        return True if cli_args.get('cpus') else False

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--cpus',
                            type=CpuLimits._validate_cpu_format,
                            default=defaults.get('cpus', None),
                            help="Number of CPUs for runtime (e.g., 1.5).")


class MemoryLimits(RockerExtension):
    @staticmethod
    def get_name():
        return 'memory_limits'

    def __init__(self):
        self.name = MemoryLimits.get_name()

    def get_preamble(self, cliargs):
        return ''

    def get_docker_args(self, cliargs):
        args = ''
        memory = cliargs.get('memory', None)
        if memory:
            args += f' --memory {memory} '
        return args

    @classmethod
    def check_args_for_activation(cls, cli_args):
        """Returns true if the arguments indicate that this extension should be activated otherwise false."""
        return True if cli_args.get('memory') else False

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--memory', '-m',
                            type=validate_memory_format,
                            default=defaults.get('memory', None),
                            help="Memory limit for runtime (e.g., 512m, 2g).")