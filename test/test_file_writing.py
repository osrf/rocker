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
import shlex
from tempfile import TemporaryDirectory

from rocker.core import list_plugins
from rocker.core import write_files
from rocker.extensions import name_to_argument
from rocker.extensions import RockerExtension

from test_extension import plugin_load_parser_correctly

class ExtensionsTest(unittest.TestCase):
    def test_name_to_argument(self):
        self.assertEqual(name_to_argument('asdf'), '--asdf')
        self.assertEqual(name_to_argument('as_df'), '--as-df')
        self.assertEqual(name_to_argument('as-df'), '--as-df')

class TestFileInjection(RockerExtension):

    name = 'test_file_injection'

    @classmethod
    def get_name(cls):
        return cls.name

    def get_files(self, cliargs):
        all_files = {}
        all_files['test_file.txt'] = """The quick brown fox jumped over the lazy dog.
%s""" % cliargs
        all_files['/absolute.txt'] = """Absolute file path should be skipped"""
        return all_files



    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--test-file-injection',
            action='store_true',
            default=defaults.get('test_file_injection', False),
            help="Enable test_file_injection extension")


class FileInjectionExtensionTest(unittest.TestCase):

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

    def test_file_injection(self):
        extensions = [TestFileInjection()]
        mock_cliargs = {'test_key': 'test_value'}

        with TemporaryDirectory() as td:
            write_files(extensions, mock_cliargs, td)

            with open(os.path.join(td, 'test_file.txt'), 'r') as fh:
                content = fh.read()
                self.assertIn('quick brown', content)
                self.assertIn('test_key', content)
                self.assertIn('test_value', content)

            self.assertFalse(os.path.exists('/absolute.txt'))
