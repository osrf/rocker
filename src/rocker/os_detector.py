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

import docker
from io import BytesIO as StringIO

from .core import base_image_exists, DependencyMissing, docker_build, get_docker_client


DETECTOR_IMAGE = "golang:1.19"
DETECTOR_TAG = "rocker:distro-detect"
DETECTOR_MOUNT = "/detect_os"

DETECTOR_TEMPLATE = """
FROM %(detector_image)s as detector

# For reliability, pin a distro-detect commit instead of targeting a branch.
RUN git clone -q https://github.com/dekobon/distro-detect.git && \\
    cd distro-detect && \\
    git checkout -q 5f5b9c724b9d9a117732d2a4292e6288905734e1 && \\
    CGO_ENABLED=0 go build -o /distro-detect .

FROM scratch
COPY --from=detector /distro-detect /distro-detect
"""

_detect_os_cache = dict()


def ensure_detector_image(client, output_callback=None, nocache=False):
    if not nocache:
        try:
            client.inspect_image(DETECTOR_TAG)
            return DETECTOR_TAG
        except docker.errors.APIError:
            pass

    detector_image = DETECTOR_IMAGE
    if not base_image_exists(detector_image, output_callback=output_callback):
        raise DependencyMissing(
            f"OS detector helper image '{detector_image}' was not found in the container "
            f"registry. Verify the image name or try 'docker pull {detector_image}'."
        )

    iof = StringIO((DETECTOR_TEMPLATE % locals()).encode())
    image_id = docker_build(
        fileobj=iof,
        output_callback=output_callback,
        nocache=nocache,
        forcerm=True,
        tag=DETECTOR_TAG
    )
    if not image_id:
        if output_callback:
            output_callback(f"Failed to build detector image '{DETECTOR_TAG}'")
        raise DependencyMissing(
            f"Failed to build OS detector helper image '{DETECTOR_TAG}'."
        )
    return DETECTOR_TAG


def detect_os(image_name, output_callback=None, nocache=False):
    # Do not rerun OS detection if there is already a cached result for the given image
    if image_name in _detect_os_cache:
        return _detect_os_cache[image_name]

    client = get_docker_client()
    detector_tag = ensure_detector_image(client, output_callback=output_callback, nocache=nocache)
    if not detector_tag:
        raise DependencyMissing(
            f"Failed to build or locate OS detector helper image '{DETECTOR_TAG}'."
        )

    cmd = (
        f"docker run -it --rm --network=none "
        f"--mount type=image,source={detector_tag},target={DETECTOR_MOUNT} "
        f"--entrypoint {DETECTOR_MOUNT}/distro-detect "
        f"{image_name} -format json-one-line"
    )
    if output_callback:
        output_callback("running, ", cmd)
    p = pexpect.spawn(cmd)
    output = p.read().decode()
    if output_callback:
        output_callback("output: ", output)
    p.close()

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
            output_callback(f"{DETECTOR_MOUNT}/distro-detect failed:")
            for l in output.splitlines():
                output_callback("> %s" % l)
        return None
