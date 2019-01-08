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
import pexpect


from io import BytesIO as StringIO

from rocker.cli import DockerImageGenerator, list_plugins

class NvidiaTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        client = docker.from_env()
        dockerfile = """
FROM ubuntu:xenial

RUN apt-get update && apt-get install glmark2 -y && apt-get clean

CMD glmark2 --validate
"""
        self.dockerfile_tag = 'rocker_test_glmark2'
        iof = StringIO(dockerfile.encode())
        im = client.images.build(fileobj = iof, tag=self.dockerfile_tag)
        
    
    def test_no_nvidia_glmark2(self):
        dig = DockerImageGenerator([], [], self.dockerfile_tag)
        self.assertEqual(dig.build(), 0)
        self.assertNotEqual(dig.run(), 0)

    def test_nvidia_glmark2(self):
        plugins = list_plugins()
        desired_plugins = ['nvidia', 'user']
        active_extensions = [e() for e in plugins.values() if e.get_name() in desired_plugins]
        dig = DockerImageGenerator(active_extensions, '', self.dockerfile_tag)
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run(), 0)
