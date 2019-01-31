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

from .core import get_docker_client


DETECTOR_DOCKERFILE="""
FROM python:3

RUN mkdir -p /tmp/distrovenv
RUN python3 -m venv /tmp/distrovenv
RUN . /tmp/distrovenv/bin/activate && pip install distro pyinstaller

RUN echo 'import distro; print(distro.linux_distribution())' > /tmp/distrovenv/detect_os.py
RUN . /tmp/distrovenv/bin/activate && pyinstaller --onefile /tmp/distrovenv/detect_os.py

"""

DETECTION_TEMPLATE="""
FROM rocker__detector as detector

FROM %(image_name)s

COPY --from=detector /dist/detect_os /tmp/detect_os
CMD /tmp/detect_os
"""


def build_detector_image():
    client = get_docker_client()
    """Build the image to use to detect the OS"""
    dockerfile_tag = 'rocker__detector'
    iof = StringIO(DETECTOR_DOCKERFILE.encode())
    im = client.build(fileobj = iof, tag=dockerfile_tag)
    for l in im:
        pass
        #print(l)


def detect_os(image_name):
    client = get_docker_client()
    dockerfile_tag = 'rocker__detection_%s' % image_name
    iof = StringIO((DETECTION_TEMPLATE % locals()).encode())
    im = client.build(fileobj = iof, tag=dockerfile_tag)
    for l in im:
        pass
        #print(l)
    

    cmd="docker run -it --rm %s" % dockerfile_tag
    try:
        p = pexpect.spawn(cmd)
        output = p.read()
        p.terminate()
        return literal_eval(output.decode().strip())
    except subprocess.CalledProcessError as ex:
        print("Docker run failed\n", ex)
        print(ex.output)
        return None
