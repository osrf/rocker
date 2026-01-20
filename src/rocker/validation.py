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

import os


def has_nvidia_driver():
    """
    Detect if NVIDIA drivers are installed on the host system.

    This checks for the presence of /dev/nvidia0 or /dev/nvidiactl, which indicate
    that NVIDIA drivers are installed and functional on the host.

    We check these device files rather than searching for libraries or executables
    because:
    - /dev/nvidia0 and /dev/nvidiactl are created by nvidia-modprobe or nvidia driver
    - Their presence indicates the kernel driver is loaded and ready
    - This avoids false positives from stale installations

    Returns:
        bool: True if NVIDIA driver devices are detected, False otherwise.
    """
    return os.path.exists('/dev/nvidia0') or os.path.exists('/dev/nvidiactl')
