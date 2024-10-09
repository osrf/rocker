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
import re
from rocker.extensions import RockerExtension, name_to_argument


class Ulimit(RockerExtension):
    """
    A RockerExtension to handle ulimit settings for Docker containers.

    This extension allows specifying ulimit options in the format TYPE=SOFT_LIMIT[:HARD_LIMIT]
    and validates the format before passing them as Docker arguments.
    """
    EXPECTED_FORMAT = "TYPE=SOFT_LIMIT[:HARD_LIMIT]"

    @staticmethod
    def get_name():
        return 'ulimit'

    def get_docker_args(self, cliargs):
        args = ['']
        ulimits = [x for sublist in cliargs[Ulimit.get_name()] for x in sublist]
        for ulimit in ulimits:
            if self.arg_format_is_valid(ulimit):
                args.append(f"--ulimit {ulimit}")
            else:
                raise ArgumentTypeError(
                    f"Error processing {Ulimit.get_name()} flag '{ulimit}': expected format"
                    f" {Ulimit.EXPECTED_FORMAT}")
        return ' '.join(args)

    def arg_format_is_valid(self, arg: str):
        """
        Validate the format of the ulimit argument.

        Args:
            arg (str): The ulimit argument to validate.

        Returns:
            bool: True if the format is valid, False otherwise.
        """
        ulimit_format = r'(\w+)=(\w+)(:\w+)?$'
        match = re.match(ulimit_format, arg)
        return match is not None

    @staticmethod
    def register_arguments(parser, defaults):
        parser.add_argument(name_to_argument(Ulimit.get_name()),
                            type=str,
                            nargs='+',
                            action='append',
                            metavar=Ulimit.EXPECTED_FORMAT,
                            default=defaults.get(Ulimit.get_name(), None),
                            help='ulimit options to add into the container.')
