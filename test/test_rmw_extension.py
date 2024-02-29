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

import em
import os
import unittest
import pytest


from rocker.core import DockerImageGenerator
from rocker.core import list_plugins

from test_extension import plugin_load_parser_correctly



class rmwExtensionTest(unittest.TestCase):

    def setUp(self):
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False

    def test_rmw_extension(self):
        plugins = list_plugins()
        rmw_plugin = plugins['rmw']
        self.assertEqual(rmw_plugin.get_name(), 'rmw')

        p = rmw_plugin()
        self.assertTrue(plugin_load_parser_correctly(rmw_plugin))
        

        mock_cliargs = {'rmw': ['cyclonedds']}
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertIn('-e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp', args)
        snippet = p.get_snippet(mock_cliargs)
        self.assertIn('rmw-cyclonedds-cpp', snippet)


        #without it set
        mock_cliargs = {'rmw': None}
        args = p.get_docker_args(mock_cliargs)
        snippet = p.get_snippet(mock_cliargs)
        self.assertNotIn('RMW_IMPLEMENTATION', args)
        self.assertNotIn('rmw-cyclonedds-cpp', snippet)


@pytest.mark.docker
class rmwRuntimeExtensionTest(unittest.TestCase):

    def setUp(self):
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False

    def test_rmw_extension(self):
        plugins = list_plugins()
        rmw_plugin = plugins['rmw']

        p = rmw_plugin()
        self.assertTrue(plugin_load_parser_correctly(rmw_plugin))

        mock_cliargs = {'rmw': ['cyclonedds']}
        dig = DockerImageGenerator([rmw_plugin()], mock_cliargs, 'ros:rolling')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run(command='dpkg -l ros-rolling-rmw-cyclonedds-cpp'), 0)
        self.assertIn('-e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp', dig.generate_docker_cmd('', mode='dry-run'))
