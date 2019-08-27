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

import re
from argparse import ArgumentTypeError

def tag_image_name(image_name, prefix=None, suffix=None):
    # from https://github.com/docker/distribution/blob/master/reference/reference.go, with some simplifications:
    parsed_image_name = re.fullmatch(
        r'((?P<hostname>([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))+)(:(?P<port>[0-9]+))?/)?'
        r'(?P<components>[a-zA-Z0-9_\.-]+(/[a-zA-Z0-9_\.-]+)*)'
        r'(:(?P<tag>[a-zA-Z0-9\.-]+))?',
        image_name)
    if not parsed_image_name:
        raise ArgumentTypeError('image name is not a valid Docker image reference')

    # convert matched groups to a dictionary and remove None elements
    parsed_image_name = {k: v for k, v in parsed_image_name.groupdict().items() if v is not None}

    tagged_name = ''
    if 'hostname' in parsed_image_name:
        tagged_name += parsed_image_name['hostname']
        if 'port' in parsed_image_name:
            tagged_name += ':{}'.format(parsed_image_name['port'])
        tagged_name += '/'
    tagged_name += parsed_image_name['components']

    tag = parsed_image_name.get('tag', 'latest')
    tagged_name += ':{prefix}{tag}{suffix}'.format(
        prefix=(prefix or ''),
        tag=(tag or ''),
        suffix=(suffix or ''))

    return tagged_name