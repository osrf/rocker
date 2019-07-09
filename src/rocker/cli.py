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
import requests.exceptions
import sys

from .core import DockerImageGenerator
from .core import get_docker_client
from .core import list_plugins
from .core import pull_image

from .os_detector import build_detector_image
from .os_detector import detect_os


def main():

    parser = argparse.ArgumentParser(description='A tool for running docker with extra options')
    parser.add_argument('image')
    parser.add_argument('command', nargs='*', default='')
    parser.add_argument('--noexecute', action='store_true')
    parser.add_argument('--nocache', action='store_true')
    parser.add_argument('--pull', action='store_true')
    parser.add_argument('--network', choices=['bridge', 'host', 'overlay', 'none'])
    parser.add_argument('--devices', nargs='*')

    # Check for docker access
    client = get_docker_client()
    try:
        client.containers()
    except requests.exceptions.ConnectionError as ex:
        print('Aborting: Could not talk to the docker daemon.')
        print(ex)
        print('Do you have permissions to run docker such as being in the docker group?')
        return 1

    plugins = list_plugins()
    print("Plugins found: %s" % [p.get_name() for p in plugins.values()])
    for p in plugins.values():
        p.register_arguments(parser)

    args = parser.parse_args()
    args_dict = vars(args)
    
    active_extensions = [e() for e in plugins.values() if args_dict.get(e.get_name())]
    # Force user to end if present otherwise it will 
    active_extensions.sort(key=lambda e:e.get_name().startswith('user'))
    print("Active extensions %s" % [e.get_name() for e in active_extensions])

    base_image = args.image

    if args.pull:
        pull_image(base_image)

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

    args = parser.parse_args()    

    build_detector_image()
    results = detect_os(args.image)
    print(results)
    if results:
        return 0
    else:
        return 1