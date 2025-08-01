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
from .core import ExtensionError
from .core import OPERATIONS_DRY_RUN
from .core import OPERATIONS_INTERACTIVE
from .core import OPERATIONS_NON_INTERACTIVE
from .core import OPERATION_MODES

from .os_detector import detect_os


def main():

    parser = argparse.ArgumentParser(
        description='A tool for running docker with extra options',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('image')
    parser.add_argument('command', nargs='*', default='')
    parser.add_argument('--noexecute', action='store_true', help='Deprecated') # TODO(tfoote) add when 3.13 is minimum supported, deprecated=True 
    parser.add_argument('--nocache', action='store_true')
    parser.add_argument('--nocleanup', action='store_true', help='do not remove the docker container when stopped')
    parser.add_argument('--persist-image', action='store_true', help='do not remove the docker image when stopped', default=False) #TODO(tfoote) Add a name to it if persisting
    parser.add_argument('--pull', action='store_true')
    parser.add_argument('--version', action='version',
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
    
    # validate_operating_mode
    operating_mode = args_dict.get('mode')
    # Don't try to be interactive if there's no tty
    if not os.isatty(sys.__stdin__.fileno()):
        if operating_mode == OPERATIONS_INTERACTIVE:
            parser.error("No tty detected cannot operate in interactive mode")
        elif not operating_mode:
            print("No tty detected for stdin defaulting mode to non-interactive")
            args_dict['mode'] = OPERATIONS_NON_INTERACTIVE
    
    # Check if detach extension is active and deconflict with interactive
    detach_active = args_dict.get('detach')
    operating_mode = args_dict.get('mode')
    if detach_active:
        if operating_mode == OPERATIONS_INTERACTIVE:
            parser.error("Command line option --mode=interactive and --detach are mutually exclusive")
        elif not operating_mode:
            print(f"Detach extension active, defaulting mode to {OPERATIONS_NON_INTERACTIVE}")
            args_dict['mode'] = OPERATIONS_NON_INTERACTIVE
    # TODO(tfoote) Deal with the case of dry-run + detach
    # Right now the printed results will include '-it'
    # But based on testing the --detach overrides -it in docker so it's ok.

    # Default to non-interactive if unset
    if args_dict.get('mode') not in OPERATION_MODES:
        print("Mode unset, defaulting to interactive")
        args_dict['mode'] = OPERATIONS_NON_INTERACTIVE

    try:
        active_extensions = extension_manager.get_active_extensions(args_dict)
    except ExtensionError as e:
        print(f"ERROR! {str(e)}")
        return 1
    print("Active extensions %s" % [e.get_name() for e in active_extensions])

    base_image = args.image

    dig = DockerImageGenerator(active_extensions, args_dict, base_image)
    exit_code = dig.build(**vars(args))
    if exit_code != 0:
        print("Build failed exiting")
        if not (args_dict['persist_image'] or args_dict.get('image_name')):
            dig.clear_image()
        return exit_code
    # Convert command into string
    args.command = ' '.join(args.command)
    result = dig.run(**args_dict)
    if not (args_dict['persist_image'] or args_dict.get('image_name')):
        print(f'Clearing Image: {dig.image_id}s\nTo not clean up use --persist-image')
        dig.clear_image()
    return result


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
