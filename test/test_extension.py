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

import getpass
import os
import unittest
from pathlib import Path


from rocker.cli import list_plugins


class HomeExtensionTest(unittest.TestCase):
    def test_user_extension(self):
        plugins = list_plugins()
        home_plugin = plugins['home']
        self.assertEqual(home_plugin.get_name(), 'home')

        p = home_plugin()
        
        mock_cliargs = {}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('-v %s:%s' % (Path.home(), Path.home()) in args)


class UserExtensionTest(unittest.TestCase):
    def test_user_extension(self):
        plugins = list_plugins()
        user_plugin = plugins['user']
        self.assertEqual(user_plugin.get_name(), 'user')

        p = user_plugin()

        env_subs = p.get_environment_subs()
        self.assertEqual(env_subs['user_id'], os.getuid())
        self.assertEqual(env_subs['username'],  getpass.getuser())

        mock_cliargs = {}
        snippet = p.get_snippet(mock_cliargs).splitlines()

        passwd_line = [l for l in snippet if 'chpasswd' in l][0]
        self.assertTrue(getpass.getuser() in passwd_line)

        uid_line = [l for l in snippet if '--uid' in l][0]
        self.assertTrue(str(os.getuid()) in uid_line)

        self.assertEqual(p.get_preamble(mock_cliargs), '')
        self.assertEqual(p.get_docker_args(mock_cliargs), '')
