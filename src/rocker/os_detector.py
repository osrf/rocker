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
from packaging.version import Version

from .core import base_image_exists, DependencyMissing, docker_build, get_docker_client, ImageNotFound


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

# --- BEGIN DOCKER < 28.0 BACKWARDS COMPATIBILITY ---
# `docker run --mount type=image` was introduced in Docker Engine 28.0.0 (API 1.48).
# While older Docker versions (< 28.0.0) are still supported, fall back to the
# legacy mechanism that builds and removes a temporary layered image per target.
#
# TODO: Once Docker Engine >= 28.0.0 is the minimum supported version, remove:
#   1. This entire compatibility block (MIN_DOCKER_VERSION_IMAGE_MOUNT,
#      LEGACY_DETECTION_TEMPLATE, _get_docker_version, _run_legacy_detect_os)
#   2. The `from packaging.version import Version` import above
#   3. The `if _get_docker_version(client) < MIN_DOCKER_VERSION_IMAGE_MOUNT:`
#      branch in detect_os() below.
MIN_DOCKER_VERSION_IMAGE_MOUNT = Version("28.0")

LEGACY_DETECTION_TEMPLATE = """
FROM %(detector_tag)s as detector

FROM %(image_name)s

COPY --from=detector /distro-detect /tmp/detect_os
ENTRYPOINT [ "/tmp/detect_os", "-format", "json-one-line" ]
CMD [ "" ]
"""


def _get_docker_version(client):
    docker_version_raw = client.version()['Version']
    return Version(docker_version_raw.split('-')[0])


def _run_legacy_detect_os(client, image_name, detector_tag, output_callback=None, nocache=False):
    iof = StringIO((LEGACY_DETECTION_TEMPLATE % locals()).encode())
    tag_name = "rocker:" + f"os_detect_{image_name}".replace(':', '_').replace('/', '_')
    image_id = docker_build(
        docker_client=client,
        fileobj=iof,
        output_callback=output_callback,
        nocache=nocache,
        forcerm=True,
        tag=tag_name
    )
    if not image_id:
        if output_callback:
            output_callback('Failed to build detector image')
        return None, None

    cmd = "docker run -it --rm %s" % image_id
    if output_callback:
        output_callback("running, ", cmd)
    p = pexpect.spawn(cmd)
    output = p.read().decode()
    if output_callback:
        output_callback("output: ", output)
    p.close()

    # Clean up the temporary image
    client.remove_image(image=tag_name)
    return output, p.exitstatus
# --- END DOCKER < 28.0 BACKWARDS COMPATIBILITY ---

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


def detect_os(image_name, output_callback=None, nocache=False, auto_pull=True):
    """Detect the operating system of a docker image.

    Returns a (distribution, version, codename) tuple, or None if the OS could
    not be determined. Raises ImageNotFound if the image is not available
    locally (it is pulled automatically unless auto_pull is False) and
    DependencyMissing if the detector tooling is unavailable.
    """
    # Do not rerun OS detection if there is already a cached result for the given image
    if image_name in _detect_os_cache:
        return _detect_os_cache[image_name]

    client = get_docker_client()

    # The image must be present before `docker run` below: if docker pulled it
    # there, the pull progress would be interleaved with the detector's output.
    if not base_image_exists(image_name, docker_client=client, output_callback=output_callback, pull=auto_pull):
        if auto_pull:
            raise ImageNotFound(
                f"Image '{image_name}' not found locally and could not be pulled. "
                f"Verify the image name or try 'docker pull {image_name}' manually."
            )
        raise ImageNotFound(
            f"Image '{image_name}' not found locally and auto-pull is disabled. "
            f"Run 'docker pull {image_name}' first or enable auto-pull."
        )

    detector_tag = ensure_detector_image(client, output_callback=output_callback, nocache=nocache)
    if not detector_tag:
        raise DependencyMissing(
            f"Failed to build or locate OS detector helper image '{DETECTOR_TAG}'."
        )

    # TODO: Remove this branch once Docker Engine >= 28.0.0 is the minimum supported version.
    if _get_docker_version(client) < MIN_DOCKER_VERSION_IMAGE_MOUNT:
        output, exitstatus = _run_legacy_detect_os(
            client, image_name, detector_tag,
            output_callback=output_callback, nocache=nocache
        )
        if output is None:
            return None
    else:
        cmd = (
            f"docker run -it --rm --network=none --pull=never "
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
        exitstatus = p.exitstatus

    if exitstatus == 0:
        # Filter out Docker CLI daemon warnings: Docker Engine 28.0 - 29.6 emits
        # "WARNING: Image mount is an experimental feature" when `--mount type=image`
        # is used.
        # TODO: Remove this warning filter once Docker Engine >= 29.7.0 is the
        # minimum supported version.
        json_output = "\n".join(
            line for line in output.splitlines()
            if not line.startswith("WARNING:")
        ).strip()
        try:
            detect_dict = json.loads(json_output)
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
