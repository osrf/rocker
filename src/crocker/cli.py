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
from collections import OrderedDict
import os
import sys

import pkg_resources
import pkgutil
import subprocess
import tempfile

import em

import docker
import requests
import pexpect


class DockerImageGenerator(object):
    def __init__(self, active_extensions, cliargs, base_image):
        self.built = False
        self.cliargs = cliargs
        self.active_extensions = active_extensions

        self.dockerfile = generate_dockerfile(active_extensions, self.cliargs, base_image)
        # print(df)
        self.image_name = "rocker_" + base_image
        if self.active_extensions:
            self.image_name += "_%s" % '_'.join([e.name for e in active_extensions])

    
    def build(self, **kwargs):
        with tempfile.TemporaryDirectory() as td:
            df = os.path.join(td, 'Dockerfile')
            print("Writing dockerfile to %s" % df)
            with open(df, 'w') as fh:
                fh.write(self.dockerfile)
            print('vvvvvv')
            print(self.dockerfile)
            print('^^^^^^')
            arguments = {}
            arguments['path'] = td
            arguments['rm'] = True
            arguments['decode'] = True
            arguments['nocache'] = kwargs.get('nocache', False)
            arguments['tag'] = self.image_name
            print("Building docker file with arguments: ", arguments)
            try:
                docker_client = docker.APIClient()
                success_detected = False
                for line in docker_client.build(**arguments):
                    output = line.get('stream', '').rstrip()
                    if not output:
                        # print("non stream data", line)
                        continue
                    print("building > %s" % output)
                    if output.startswith("Successfully tagged") and self.image_name in output:
                        success_detected = True
                if success_detected:
                        self.built = True
                        return True
 
            except docker.errors.APIError as ex:
                print("Docker build failed\n", ex)
                print(ex.output)
                return False
        # Unknown error 
        return False

    def run(self, command=[], **kwargs):
        if not self.built:
            print("Cannot run if build has not passed.")
            return False

        for e in self.active_extensions:
            try:
                e.precondition_environment(self.cliargs)
            except subprocess.CalledProcessError as ex:
                print("Failed to precondition for extension [%s] with error: %s\ndeactivating" % (e.get_name(), ex))
                # TODO(tfoote) remove the extension from the list


        docker_args = ''

        network = kwargs.get('network', False)
        if network:
            docker_args += ' --network %s ' % network

        devices = kwargs.get('devices', None)
        if devices:
            for device in devices:
                if not os.path.exists(device):
                    print("ERROR device %s doesn't exist. Skipping" % device)
                    continue
                docker_args += ' --device %s ' % device

        for e in self.active_extensions:
            docker_args += e.get_docker_args(self.cliargs)

        image = self.image_name
        cmd="docker run -it \
  --rm \
  %(docker_args)s \
  %(image)s %(command)s" % locals()
#   $DOCKER_OPTS \
        try:
            if kwargs.get('execute', False):
                print("Executing command: ")
                print(cmd)
                p = pexpect.spawn(cmd)
                p.interact()
            else:
                print("Run this command: \n\n\n")
                print(cmd)
        except subprocess.CalledProcessError as ex:
            print("Docker run failed\n", ex)
            print(ex.output)
            return False


def generate_dockerfile(extensions, args_dict, base_image):
    dockerfile_str = ''
    for el in extensions:
        dockerfile_str += '# Preamble from extension [%s]\n' % el.name
        dockerfile_str += el.get_preamble(args_dict) + '\n'
    dockerfile_str += '\nFROM %s\n' % base_image
    for el in extensions:
        dockerfile_str += '# Snippet from extension [%s]\n' % el.name
        dockerfile_str += el.get_snippet(args_dict) + '\n'
    return dockerfile_str


def main():

    parser = argparse.ArgumentParser(description='A tool for running docker with extra options')
    parser.add_argument('image', nargs='+')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--nocache', action='store_true')
    parser.add_argument('--pull', action='store_true')
    parser.add_argument('--network', choices=['bridge', 'host', 'overlay', 'none'])
    parser.add_argument('--devices', nargs='*')

    unordered_plugins = {
    entry_point.name: entry_point.load()
    for entry_point
    in pkg_resources.iter_entry_points('rocker.extensions')
    }
    # Order plugins by extension point name for consistent ordering below
    plugin_names = list(unordered_plugins.keys())
    plugin_names.sort()
    plugins = OrderedDict([(k, unordered_plugins[k]) for k in plugin_names])

    print("Plugins found: %s" % [p.get_name() for p in plugins.values()])
    for p in plugins.values():
        p.register_arguments(parser)

    args = parser.parse_args()
    args_dict = vars(args)
    
    active_extensions = [e() for e in plugins.values() if args_dict.get(e.get_name())]
    # Force user to end if present otherwise it will 
    active_extensions.sort(key=lambda e:e.get_name().startswith('user'))
    print("Active extensions %s" % [e.get_name() for e in active_extensions])

    base_image = args.image[0]

    if args.pull:
        docker_client = docker.APIClient()
        try:
            print("Pulling image %s" % base_image)
            for line in docker_client.pull(base_image, stream=True):
                print(line)
        except docker.errors.APIError as ex:
            print('Pull of %s failed: %s' % (base_image, ex))
            pass
    dig = DockerImageGenerator(active_extensions, args_dict, base_image)
    dig.build(**vars(args))
    dig.run(command=' '.join(args.image[1:]), **args_dict)
    return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
