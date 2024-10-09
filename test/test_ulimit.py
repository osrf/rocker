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

from rocker.ulimit_extension import Ulimit


class UlimitTest(unittest.TestCase):
    """Unit tests for the Ulimit class."""

    def setUp(self):
        self._instance = Ulimit()
        self._curr_path = os.path.abspath(os.path.curdir)
        self._virtual_path = "/path/in/container"

    def _is_arg_translation_ok(self, mock_cliargs, expected):
        docker_args = self._instance.get_docker_args({self._instance.get_name(): [mock_cliargs]})
        print(f"DEBUG: Expected docker_args: {expected}")
        print(f"DEBUG: Resulted docker_args: {docker_args}")
        self.assertTrue(docker_args == expected)

    def test_args_single_soft(self):
        """Test single soft limit argument."""
        mock_cliargs = ["rtprio=99"]
        expected = " --ulimit rtprio=99"
        self._is_arg_translation_ok(mock_cliargs, expected)

    def test_args_multiple_soft(self):
        """Test multiple soft limit arguments."""
        mock_cliargs = ["rtprio=99", "memlock=102400"]
        expected = " --ulimit rtprio=99 --ulimit memlock=102400"
        self._is_arg_translation_ok(mock_cliargs, expected)

    def test_args_single_hard(self):
        """Test single hard limit argument."""
        mock_cliargs = ["nofile=1024:524288"]
        expected = " --ulimit nofile=1024:524288"
        self._is_arg_translation_ok(mock_cliargs, expected)

    def test_args_multiple_hard(self):
        """Test multiple hard limit arguments."""
        mock_cliargs = ["nofile=1024:524288", "rtprio=90:99"]
        expected = " --ulimit nofile=1024:524288 --ulimit rtprio=90:99"
        self._is_arg_translation_ok(mock_cliargs, expected)

    def test_args_multiple_mix(self):
        """Test multiple mixed limit arguments."""
        mock_cliargs = ["rtprio=99", "memlock=102400", "nofile=1024:524288"]
        expected = " --ulimit rtprio=99 --ulimit memlock=102400 --ulimit nofile=1024:524288"
        self._is_arg_translation_ok(mock_cliargs, expected)
