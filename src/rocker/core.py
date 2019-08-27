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

from collections import OrderedDict
import os
import sys

import pkg_resources
import pkgutil
import subprocess
import tempfile

import em

import docker
import pexpect

from .utils import tag_image_name

class RockerExtension(object):
    """The base class for Rocker extension points"""

    def precondition_environment(self, cliargs):
        """Modify the local environment such as setup tempfiles"""
        pass

    def validate_environment(self, cliargs):
        """ Check that the environment is something that can be used.
        This will check that we're on the right base OS and that the 
        necessary resources are available, like hardware."""
        pass

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        return ''

    def get_name(self, cliargs):
        raise NotImplementedError
    
    def get_docker_args(self, cliargs):
        return ''

    @staticmethod
    def register_arguments(parser):
        raise NotImplementedError


def get_docker_client():
    """Simple helper function for pre 2.0 imports"""
    try:
        docker_client = docker.APIClient()
    except AttributeError:
        # docker-py pre 2.0
        docker_client = docker.Client()
    return docker_client

class DockerImageGenerator(object):
    def __init__(self, active_extensions, cliargs, base_image):
        self.built = False
        self.cliargs = cliargs
        self.cliargs['base_image'] = base_image # inject base image into arguments for use
        self.active_extensions = active_extensions

        self.dockerfile = generate_dockerfile(active_extensions, self.cliargs, base_image)
        # print(df)
        self.image_name = tag_image_name(base_image, prefix="rocker-")
        if self.active_extensions:
            self.image_name += "-%s" % '-'.join([e.name for e in active_extensions])

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
                docker_client = get_docker_client()
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
                        return 0
                else:
                    print("no more output and success not detected")
                    return 2
 
            except docker.errors.APIError as ex:
                print("Docker build failed\n", ex)
                print(ex.output)
                return 1

    def run(self, command='', **kwargs):
        if not self.built:
            print("Cannot run if build has not passed.")
            return 1

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
        if kwargs.get('noexecute', False):
            print("Run this command: \n\n\n")
            print(cmd)
            return 0
        else:
            try:
                print("Executing command: ")
                print(cmd)
                p = pexpect.spawn(cmd)
                p.interact()
                p.terminate()
                return p.exitstatus
            except pexpect.ExceptionPexpect as ex:
                print("Docker run failed\n", ex)
                return 1


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


def list_plugins(extension_point='rocker.extensions'):
    unordered_plugins = {
    entry_point.name: entry_point.load()
    for entry_point
    in pkg_resources.iter_entry_points(extension_point)
    }
    # Order plugins by extension point name for consistent ordering below
    plugin_names = list(unordered_plugins.keys())
    plugin_names.sort()
    return OrderedDict([(k, unordered_plugins[k]) for k in plugin_names])


def pull_image(image_name):
    docker_client = get_docker_client()
    try:
        print("Pulling image %s" % image_name)
        for line in docker_client.pull(image_name, stream=True):
            print(line)
        return True
    except docker.errors.APIError as ex:
        print('Pull of %s failed: %s' % (image_name, ex))
        return False
