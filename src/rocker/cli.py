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

import argparse
import os
import sys

from .core import DockerImageGenerator
from .core import get_rocker_version
from .core import RockerExtensionManager
from .core import DependencyMissing

from .os_detector import detect_os


def main():

    parser = argparse.ArgumentParser(
        description='A tool for running docker with extra options',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('image')
    parser.add_argument('command', nargs='*', default='')
    parser.add_argument('--noexecute', action='store_true', help='Deprecated')
    parser.add_argument('--nocache', action='store_true')
    parser.add_argument('--nocleanup', action='store_true', help='do not remove the docker container when stopped')
    parser.add_argument('--pull', action='store_true')
    parser.add_argument('-v', '--version', action='version',
        version='%(prog)s ' + get_rocker_version())

    try:
        extension_manager = RockerExtensionManager()
        default_args = {}
        extension_manager.extend_cli_parser(parser, default_args)
    except DependencyMissing as ex:
        # Catch errors if docker is missing or inaccessible.
        parser.error("DependencyMissing encountered: %s" % ex)

    args = parser.parse_args()
    args_dict = vars(args)

    if args.noexecute:
        from .core import OPERATIONS_DRY_RUN
        args_dict['mode'] = OPERATIONS_DRY_RUN
        print('DEPRECATION Warning: --noexecute is deprecated for --mode dry-run please switch your usage by December 2020')
    
    active_extensions = extension_manager.get_active_extensions(args_dict)
    # Force user to end if present otherwise it will break other extensions
    active_extensions.sort(key=lambda e:e.get_name().startswith('user'))
    print("Active extensions %s" % [e.get_name() for e in active_extensions])

    base_image = args.image

    dig = DockerImageGenerator(active_extensions, args_dict, base_image)
    exit_code = dig.build(**vars(args))
    if exit_code != 0:
        print("Build failed exiting")
        return exit_code
    # Convert command into string
    args.command = ' '.join(args.command)
    return dig.run(**args_dict)


def detect_image_os():
    parser = argparse.ArgumentParser(description='Detect the os in an image')
    parser.add_argument('image')
    parser.add_argument('--verbose', action='store_true',
        help='Display verbose output of the process')

    args = parser.parse_args()    

    results = detect_os(args.image, print if args.verbose else None)
    print(results)
    if results:
        return 0
    else:
        return 1
