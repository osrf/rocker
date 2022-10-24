# Copyright 2019-2022 Arm Ltd., Open Source Robotics Foundation

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

import json
import pexpect

from io import BytesIO as StringIO

from .core import docker_build, get_docker_client


DETECTION_TEMPLATE="""
FROM golang:1.19 as detector

# For reliability, pin a distro-detect commit instead of targeting a branch.
RUN git clone -q https://github.com/dekobon/distro-detect.git && \
    cd distro-detect && \
    git checkout -q 5f5b9c724b9d9a117732d2a4292e6288905734e1 && \
    CGO_ENABLED=0 go build .

FROM %(image_name)s

COPY --from=detector /go/distro-detect/distro-detect /tmp/detect_os
ENTRYPOINT [ "/tmp/detect_os", "-format", "json-one-line" ]
CMD [ "" ]
"""

_detect_os_cache = dict()

def detect_os(image_name, output_callback=None, nocache=False):
    # Do not rerun OS detection if there is already a cached result for the given image
    if image_name in _detect_os_cache:
        return _detect_os_cache[image_name]

    iof = StringIO((DETECTION_TEMPLATE % locals()).encode())
    tag_name = "rocker:" + f"os_detect_{image_name}".replace(':', '_').replace('/', '_')
    image_id = docker_build(
        fileobj=iof,
        output_callback=output_callback,
        nocache=nocache,
        forcerm=True,  # Remove intermediate containers from RUN commands in DETECTION_TEMPLATE
        tag=tag_name
    )
    if not image_id:
        if output_callback:
            output_callback('Failed to build detector image')
        return None

    cmd="docker run -it --rm %s" % image_id
    if output_callback:
        output_callback("running, ", cmd)
    p = pexpect.spawn(cmd)
    output = p.read().decode()
    if output_callback:
        output_callback("output: ", output)
    p.terminate()

    # Clean up the image
    client = get_docker_client()
    client.remove_image(image=tag_name)

    if p.exitstatus == 0:
        try:
            detect_dict = json.loads(output.strip())
        except ValueError:
            if output_callback:
                output_callback('Failed to parse JSON')
            return None

        dist = detect_dict.get('name', '')
        os_release = detect_dict.get('os_release', {})
        ver = os_release.get('VERSION_ID', '')
        codename = os_release.get('VERSION_CODENAME', '')

        _detect_os_cache[image_name] = (dist, ver, codename)
        return _detect_os_cache[image_name]
    else:
        if output_callback:
            output_callback("/tmp/detect_os failed:")
            for l in output.splitlines():
                output_callback("> %s" % l)
        return None
