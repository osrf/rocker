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
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        # self.assertFalse(args)
        system_gitconfig = '/etc/gitconfig'
        user_gitconfig = os.path.expanduser('~/.gitconfig')
        user_gitconfig_target = '/root/.gitconfig'
        if os.path.exists(system_gitconfig):
            # TODO(tfoote) This isn't exercised on most systems, it would need to be mocked
            self.assertIn('-v %s:%s' % (system_gitconfig, system_gitconfig), args)
        if os.path.exists(user_gitconfig):
            self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), args)

        # Test with user "enabled"
        mock_cliargs = {'user': True}
        user_args = p.get_docker_args(mock_cliargs)
        if os.path.exists(user_gitconfig):
            self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig), user_args)
