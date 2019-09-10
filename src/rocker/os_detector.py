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
FROM python:3 as detector

RUN mkdir -p /tmp/distrovenv
RUN python3 -m venv /tmp/distrovenv
RUN . /tmp/distrovenv/bin/activate && pip install distro pyinstaller staticx
RUN apt-get update && apt-get install patchelf #needed for staticx

RUN echo 'import distro; print(distro.linux_distribution())' > /tmp/distrovenv/detect_os.py
RUN . /tmp/distrovenv/bin/activate && pyinstaller --onefile /tmp/distrovenv/detect_os.py

RUN . /tmp/distrovenv/bin/activate && staticx /dist/detect_os /dist/detect_os_static

FROM %(image_name)s

COPY --from=detector /dist/detect_os_static /tmp/detect_os
ENTRYPOINT [ "/tmp/detect_os" ]
CMD [ "" ]
"""


def detect_os(image_name):
    iof = StringIO((DETECTION_TEMPLATE % locals()).encode())
    image_id = docker_build(fileobj = iof)
    if not image_id:
        return None

    cmd="docker run -it --rm %s" % image_id
    p = pexpect.spawn(cmd)
    output = p.read()
    p.terminate()
    if p.exitstatus == 0:
        return literal_eval(output.decode().strip())
    else:
        return None
