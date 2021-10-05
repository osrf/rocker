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

import pexpect

from ast import literal_eval 
from io import BytesIO as StringIO

from .core import docker_build


DETECTION_TEMPLATE="""
FROM python:3-slim-stretch as detector
# Force the older version of debian for detector.
# GLIBC is forwards compatible but not necessarily backwards compatible for pyinstaller
# https://github.com/pyinstaller/pyinstaller/wiki/FAQ#gnulinux
# StaticX is supposed to take care of this but there appears to be an issue when using subprocess

RUN mkdir -p /tmp/distrovenv
RUN python3 -m venv /tmp/distrovenv
# patchelf needed for staticx
# binutils provides objdump needed by pyinstaller
RUN apt-get update && apt-get install -qy patchelf binutils
RUN . /tmp/distrovenv/bin/activate && pip install distro pyinstaller==4.0 staticx==0.12.3

RUN echo 'import distro; import sys; output = (distro.name(), distro.version(), distro.codename()); print(output) if distro.name() else sys.exit(1)' > /tmp/distrovenv/detect_os.py
RUN . /tmp/distrovenv/bin/activate && pyinstaller --onefile /tmp/distrovenv/detect_os.py

RUN . /tmp/distrovenv/bin/activate && staticx /dist/detect_os /dist/detect_os_static && chmod go+xr /dist/detect_os_static

FROM %(image_name)s

COPY --from=detector /dist/detect_os_static /tmp/detect_os
ENTRYPOINT [ "/tmp/detect_os" ]
CMD [ "" ]
"""

_detect_os_cache = dict()

def detect_os(image_name, output_callback=None, nocache=False):
    # Do not rerun OS detection if there is already a cached result for the given image
    if image_name in _detect_os_cache:
        return _detect_os_cache[image_name]

    iof = StringIO((DETECTION_TEMPLATE % locals()).encode())
    image_id = docker_build(
        fileobj=iof,
        output_callback=output_callback,
        nocache=nocache,
        forcerm=True,  # Remove intermediate containers from RUN commands in DETECTION_TEMPLATE
        tag="rocker:" + f"os_detect_{image_name}".replace(':', '_').replace('/', '_')
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
    if p.exitstatus == 0:
        _detect_os_cache[image_name] = literal_eval(output.strip())
        return _detect_os_cache[image_name]
    else:
        if output_callback:
            output_callback("/tmp/detect_os failed:")
            for l in output.splitlines():
                output_callback("> %s" % l)
        return None
