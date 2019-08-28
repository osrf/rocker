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

from argparse import ArgumentTypeError
from nose.tools import assert_raises
import unittest

from rocker.utils import tag_image_name

class RockerTagImageNameTest(unittest.TestCase):

    def test_tag_image_name(self):
        # simple names without host or tags
        self.assertEqual(
            tag_image_name('image', prefix='rocker-', suffix='-tags'),
            'image:rocker-latest-tags')
        self.assertEqual(
            tag_image_name('user/image', prefix='rocker-', suffix='-tags'),
            'user/image:rocker-latest-tags')
        self.assertEqual(
            tag_image_name('more/than/two/components', prefix='rocker-', suffix='-tags'),
            'more/than/two/components:rocker-latest-tags')

        # with custom tag
        self.assertEqual(
            tag_image_name('image:custom-1.2.3', prefix='rocker-', suffix='-tags'),
            'image:rocker-custom-1.2.3-tags')
        self.assertEqual(
            tag_image_name('user/image:custom-1.2.3', prefix='rocker-', suffix='-tags'),
            'user/image:rocker-custom-1.2.3-tags')

        # with host localhost and port 5000 (default for https://docs.docker.com/registry/deploying/)
        self.assertEqual(
            tag_image_name('localhost:5000/user/image', prefix='rocker-', suffix='-tags'),
            'localhost:5000/user/image:rocker-latest-tags')
        self.assertEqual(
            tag_image_name('localhost:5000/user/image:custom-1.2.3', prefix='rocker-', suffix='-tags'),
            'localhost:5000/user/image:rocker-custom-1.2.3-tags')

        # with fully-qualified domain without port
        self.assertEqual(
            tag_image_name('my.private.registry/user/image', prefix='rocker-', suffix='-tags'),
            'my.private.registry/user/image:rocker-latest-tags')
        self.assertEqual(
            tag_image_name('my.private.registry/user/image:custom-1.2.3', prefix='rocker-', suffix='-tags'),
            'my.private.registry/user/image:rocker-custom-1.2.3-tags')

        # with fully-qualified domain and port
        self.assertEqual(
            tag_image_name('my.private.registry:5000/user/image', prefix='rocker-', suffix='-tags'),
            'my.private.registry:5000/user/image:rocker-latest-tags')
        self.assertEqual(
            tag_image_name('my.private.registry:5000/user/image:custom-1.2.3', prefix='rocker-', suffix='-tags'),
            'my.private.registry:5000/user/image:rocker-custom-1.2.3-tags')

        # test some invalid names
        assert_raises(ArgumentTypeError, tag_image_name,
            'image:tags_must_only_contain_alphanumeric_characters_dots_and_dashes')
        assert_raises(ArgumentTypeError, tag_image_name,
            'hostnames_cannot_have_undescores.example.com:5000/user/image')

        # You might think that this name is invalid, but docker interprets the
        # first item as a component part if there is no port:
        self.assertEqual(
            tag_image_name('hostnames_cannot_have_undescores.example.com/user/image'),
            'hostnames_cannot_have_undescores.example.com/user/image:latest')
        # ...while in this case it is a hostname:
        self.assertEqual(
            tag_image_name('hostnames-cannot-have-undescores.example.com/user/image'),
            'hostnames-cannot-have-undescores.example.com/user/image:latest')
