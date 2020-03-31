# Copyright 2019 Open Source Robotics Foundation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentTypeError
import em
import os
import pkgutil
import shlex


from rocker.extensions import RockerExtension


class GHPages(RockerExtension):

    name = 'ghpages'

    @classmethod
    def get_name(cls):
        return cls.name

    def precondition_environment(self, cli_args):
        pass

    def validate_environment(self, cli_args):
        pass

    def get_preamble(self, cli_args):
        return ''

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, {})

    def get_docker_args(self, cli_args):
        args = ''
        args += ' -v ' + shlex.quote('{directory}:/tmp/jekyll'.format(**cli_args))
        if cli_args.get('network', None):
            args += ' -p ' + shlex.quote('0.0.0.0:{port}:{port}'.format(**cli_args))
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--ghpages',
            action='store_true',
            default=defaults.get('ghpages', False),
            help="Setup environment for ghpages render with jekyll")
