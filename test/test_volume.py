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

import os
import unittest

from rocker.core import list_plugins
from rocker.volume_extension import Volume


class VolumeTest(unittest.TestCase):
    def setUp(self):
        self._instance = Volume()
        self._curr_path = os.path.abspath(os.path.curdir)
        self._virtual_path = "/path/in/container"

    def _test_equals_args(self, mock_cliargs, expected):
        """
        @type mock_cliargs: { str: [[str]] }
        @type expected: [[str]]
        """
        print("DEBUG: 'mock_cliargs' {}\n\t'expected': {}".format(mock_cliargs, expected))
        docker_args = self._instance.get_docker_args(mock_cliargs)
        print("DEBUG: Resulted docker_args: {}".format(docker_args))
        for arg_expected in expected:
            # Whitespace at the beginning is needed.
            complete_expected = " {} {}".format(Volume.ARG_DOCKER_VOLUME, arg_expected[0])
            self.assertTrue(complete_expected in docker_args)

    def test_args_single(self):
        """Passing source path"""
        arg = [[self._curr_path]]
        expected = [['{}:{}'.format(self._curr_path, self._curr_path)]]
        mock_cliargs = {Volume.name: arg}
        self._test_equals_args(mock_cliargs, expected)

    def test_args_twopaths(self):
        """Passing source path, dest path"""
        arg = ["{}:{}".format(self._curr_path, self._virtual_path)]
        mock_cliargs = {Volume.name: [arg]}
        self._test_equals_args(mock_cliargs, arg)

    def test_args_twopaths_opt(self):
        """Passing source path, dest path, and Docker's volume option"""
        arg = ["{}:{}:ro".format(self._curr_path, self._virtual_path)]
        mock_cliargs = {Volume.name: [arg]}
        self._test_equals_args(mock_cliargs, arg)

    def test_args_two_volumes(self):
        """Multiple volume points"""
        arg_first = ["{}:{}:ro".format(self._curr_path, self._virtual_path)]
        arg_second = ["/tmp:{}".format(os.path.join(self._virtual_path, "tmp"))]
        args = [arg_first, arg_second]
        mock_cliargs = {Volume.name: args}
        self._test_equals_args(mock_cliargs, args)
