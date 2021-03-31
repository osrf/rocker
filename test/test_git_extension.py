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

import argparse
import em
import getpass
import os
import unittest
from pathlib import Path
import pwd
import tempfile


from rocker.core import list_plugins
from rocker.extensions import name_to_argument

from test_extension import plugin_load_parser_correctly

class ExtensionsTest(unittest.TestCase):
    def test_name_to_argument(self):
        self.assertEqual(name_to_argument('asdf'), '--asdf')
        self.assertEqual(name_to_argument('as_df'), '--as-df')
        self.assertEqual(name_to_argument('as-df'), '--as-df')


class GitExtensionTest(unittest.TestCase):

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

    def test_git_extension(self):
        plugins = list_plugins()
        git_plugin = plugins['git']
        self.assertEqual(git_plugin.get_name(), 'git')

        p = git_plugin()
        self.assertTrue(plugin_load_parser_correctly(git_plugin))
        

        mock_cliargs = {}
        mock_config_file = tempfile.NamedTemporaryFile()
        mock_system_config_file = tempfile.NamedTemporaryFile()
        mock_cliargs['git_config_path'] = mock_config_file.name
        mock_cliargs['git_config_path_system'] = mock_system_config_file.name
        args = p.get_docker_args(mock_cliargs)
        system_gitconfig = mock_system_config_file.name
        system_gitconfig_target = '/etc/gitconfig'
        user_gitconfig = mock_config_file.name
        user_gitconfig_target = '/root/.gitconfig'
        self.assertIn('-v %s:%s' % (system_gitconfig, system_gitconfig_target), args)
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), args)

        # Test with user "enabled"
        mock_cliargs = {'user': True}
        mock_cliargs['git_config_path'] = mock_config_file.name
        user_args = p.get_docker_args(mock_cliargs)
        user_gitconfig_target = os.path.expanduser('~/.gitconfig')
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), user_args)

        # Test with overridden user
        mock_cliargs['user_override_name'] = 'testusername'
        user_args = p.get_docker_args(mock_cliargs)
        user_gitconfig_target = '/home/testusername/.gitconfig'
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), user_args)

        # Test non-extant files no generation
        mock_cliargs['git_config_path'] = '/path-does-not-exist'
        mock_cliargs['git_config_path_system'] = '/path-does-not-exist-either'
        user_args = p.get_docker_args(mock_cliargs)
        self.assertNotIn('-v', user_args)
