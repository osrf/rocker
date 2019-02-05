# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import docker
import unittest

from itertools import chain

from rocker.cli import DockerImageGenerator, list_plugins
from rocker.core import pull_image
from rocker.core import get_docker_client

class RockerCoreTest(unittest.TestCase):
    
    def test_list_plugins(self):
        plugins_found = list_plugins()
        plugin_names = plugins_found.keys()
        self.assertTrue('nvidia' in plugin_names )
        self.assertTrue('pulse' in plugin_names )
        self.assertTrue('user' in plugin_names )
        self.assertTrue('home' in plugin_names )

    def test_pull_image(self):
        TEST_IMAGE='alpine:latest'
        docker_client = get_docker_client()

        l = docker_client.images()
        tags = set(chain.from_iterable([i['RepoTags'] for i in l if i['RepoTags']]))
        print(tags)
        if TEST_IMAGE in tags:
            docker_client.remove_image(TEST_IMAGE)
            print('removed image %s' % TEST_IMAGE)
        self.assertTrue(pull_image(TEST_IMAGE))

    def test_failed_pull_image(self):
        self.assertFalse(pull_image("osrf/ros:does_not_exist"))

    def test_run_before_build(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.run('true'), 1)
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true'), 0)

    def test_return_code_no_extensions(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true'), 0)
        self.assertEqual(dig.run('false'), 1)

    def test_return_code_multiple_extensions(self):
        plugins = list_plugins()
        desired_plugins = ['home', 'user']
        active_extensions = [e() for e in plugins.values() if e.get_name() in desired_plugins]
        dig = DockerImageGenerator(active_extensions, {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true'), 0)
        self.assertEqual(dig.run('false'), 1)
