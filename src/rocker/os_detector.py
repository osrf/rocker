# Copyright 2019-2022 Arm Ltd., Open Source Robotics Foundation
#
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

import io
import json
import os
import tarfile
import tempfile

from io import BytesIO as StringIO

import docker

from .core import base_image_exists, DependencyMissing, docker_build, get_docker_client


DETECTOR_IMAGE = "golang:1.19"
DISTRO_DETECT_COMMIT = "5f5b9c724b9d9a117732d2a4292e6288905734e1"
HELPER_BINARY_IN_IMAGE = "/go/distro-detect/distro-detect"
DETECT_OS_MOUNT = "/detect_os"

HELPER_TEMPLATE = """
FROM %(detector_image)s
RUN git clone -q https://github.com/dekobon/distro-detect.git && \\
    cd distro-detect && \\
    git checkout -q %(distro_detect_commit)s && \\
    CGO_ENABLED=0 go build .
"""

_detect_os_cache = dict()


def helper_image_tag(commit=None):
    commit = DISTRO_DETECT_COMMIT if commit is None else commit
    return 'rocker:distro-detect-builder-%s' % commit[:12]


def _temp_dir_for_binary():
    shm = '/dev/shm'
    if os.path.isdir(shm) and os.access(shm, os.W_OK):
        return shm
    return None


def _image_exists_locally(client, image):
    try:
        client.inspect_image(image)
        return True
    except docker.errors.APIError:
        return False


def _wait_status(result):
    if isinstance(result, dict):
        return result.get('StatusCode', 1)
    return result


def _decode_logs(logs):
    if logs is None:
        return ''
    if isinstance(logs, bytes):
        return logs.decode()
    return str(logs)


def _read_stream(stream):
    if hasattr(stream, 'read'):
        data = stream.read()
        if data:
            return data
    return b''.join(stream)


def _write_archive_file(stream, dest_path):
    data = _read_stream(stream)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r') as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        if not members:
            raise ValueError('helper image archive did not contain a file')
        extracted = tar.extractfile(members[0])
        with open(dest_path, 'wb') as fh:
            fh.write(extracted.read())
    os.chmod(dest_path, 0o755)


def _ensure_helper_image(client, output_callback=None, nocache=False):
    tag = helper_image_tag()
    if not nocache and _image_exists_locally(client, tag):
        return tag

    detector_image = DETECTOR_IMAGE
    distro_detect_commit = DISTRO_DETECT_COMMIT
    iof = StringIO((HELPER_TEMPLATE % locals()).encode())
    image_id = docker_build(
        fileobj=iof,
        output_callback=output_callback,
        nocache=nocache,
        forcerm=True,
        tag=tag,
    )
    if not image_id:
        return None
    return tag


def _extract_binary_to_tempfile(client, helper_tag):
    fd, path = tempfile.mkstemp(prefix='rocker-distro-detect-', dir=_temp_dir_for_binary())
    os.close(fd)
    container = None
    try:
        container = client.create_container(helper_tag)
        container_id = container.get('Id')
        stream, _stat = client.get_archive(container_id, HELPER_BINARY_IN_IMAGE)
        _write_archive_file(stream, path)
        return path
    except Exception:
        if os.path.exists(path):
            os.unlink(path)
        raise
    finally:
        if container is not None:
            try:
                client.remove_container(container.get('Id'), force=True)
            except docker.errors.APIError:
                pass


def _run_detect_os(client, image_name, host_binary, output_callback=None):
    host_config = client.create_host_config(
        binds={host_binary: {'bind': DETECT_OS_MOUNT, 'mode': 'ro'}},
    )
    container = client.create_container(
        image_name,
        command=['-format', 'json-one-line'],
        entrypoint=[DETECT_OS_MOUNT],
        volumes=[DETECT_OS_MOUNT],
        host_config=host_config,
        network_disabled=True,
    )
    container_id = container.get('Id')
    try:
        if output_callback:
            output_callback(
                "running, docker run --network=none -v %s:%s:ro --entrypoint %s %s -format json-one-line"
                % (host_binary, DETECT_OS_MOUNT, DETECT_OS_MOUNT, image_name)
            )
        client.start(container_id)
        status = _wait_status(client.wait(container_id))
        output = _decode_logs(client.logs(container_id))
        if output_callback:
            output_callback("output: ", output)
        return status, output
    finally:
        try:
            client.remove_container(container_id, force=True)
        except docker.errors.APIError:
            pass


def detect_os(image_name, output_callback=None, nocache=False):
    # Do not rerun OS detection if there is already a cached result for the given image
    if image_name in _detect_os_cache:
        return _detect_os_cache[image_name]

    host_binary = None
    if not base_image_exists(DETECTOR_IMAGE, output_callback=output_callback):
        raise DependencyMissing(
            f"OS detector helper image '{DETECTOR_IMAGE}' was not found in the container "
            f"registry. Verify the image name or try 'docker pull {DETECTOR_IMAGE}'."
        )

    try:
        image_ok = base_image_exists(image_name, output_callback=output_callback)
    except docker.errors.APIError as ex:
        if output_callback:
            output_callback("Failed to find image '%s': %s" % (image_name, ex))
        return None
    if not image_ok:
        if output_callback:
            output_callback("Failed to find image '%s'" % image_name)
        return None

    client = get_docker_client()
    helper_tag = _ensure_helper_image(
        client, output_callback=output_callback, nocache=nocache)
    if not helper_tag:
        if output_callback:
            output_callback('Failed to build detector helper image')
        return None
    host_binary = _extract_binary_to_tempfile(client, helper_tag)

    try:
        status, output = _run_detect_os(
            client, image_name, host_binary, output_callback=output_callback)
    except docker.errors.APIError as ex:
        if output_callback:
            output_callback("%s failed: %s" % (DETECT_OS_MOUNT, ex))
        return None
    finally:
        if host_binary and os.path.exists(host_binary):
            os.unlink(host_binary)

    if status == 0:
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

    if output_callback:
        output_callback("%s failed:" % DETECT_OS_MOUNT)
        for line in output.splitlines():
            output_callback("> %s" % line)
    return None
