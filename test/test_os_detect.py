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


from rocker.os_detector import detect_os

class RockerOSDetectorTest(unittest.TestCase):

    def test_ubuntu(self):
        result = detect_os("ubuntu:xenial")
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '16.04')

        result = detect_os("ubuntu:bionic")
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '18.04')

        # Cover verbose codepath
        result = detect_os("ubuntu:bionic", output_callback=print)
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '18.04')

    def test_fedora(self):
        result = detect_os("fedora:29")
        self.assertEqual(result[0], 'Fedora')
        self.assertEqual(result[1], '29')

    def test_does_not_exist(self):
        result = detect_os("osrf/ros:does_not_exist")
        self.assertEqual(result, None)

    def test_cannot_detect_os(self):
        # Test with output callback too get coverage of error reporting
        result = detect_os("scratch", output_callback=print)
        self.assertEqual(result, None)
