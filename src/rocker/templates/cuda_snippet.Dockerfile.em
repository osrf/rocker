# Installation instructions from NVIDIA:
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Debian&target_version=11&target_type=deb_network
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network


# Prerequisites
RUN DEBIAN_FRONTEND=noninteractive apt-get update -q && \
    DEBIAN_FRONTEND=noninteractive apt-get install -qy --no-install-recommends \
    wget software-properties-common gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Enable contrib on debian to get required
# https://packages.debian.org/bullseye/glx-alternative-nvidia

RUN \
  wget -q https://developer.download.nvidia.com/compute/cuda/repos/@(download_osstring)@(download_verstring)/x86_64/cuda-keyring_1.1-1_all.deb && \
  dpkg -i cuda-keyring_1.1-1_all.deb && \
  rm cuda-keyring_1.1-1_all.deb && \
  \@[if download_osstring == 'debian']@
  add-apt-repository contrib && \
  \@[end if]@
  DEBIAN_FRONTEND=noninteractive apt-get update -q && \
  DEBIAN_FRONTEND=noninteractive apt-get -qy install cuda-toolkit  --no-install-recommends && \
  rm -rf /var/lib/apt/lists/* && \
  echo "Successfully installed cuda-toolkit"

# File conflict problem with libnvidia-ml.so.1 and libcuda.so.1
# https://github.com/NVIDIA/nvidia-docker/issues/1551
RUN rm -rf /usr/lib/x86_64-linux-gnu/libnv*
RUN rm -rf /usr/lib/x86_64-linux-gnu/libcuda*

# TODO(tfoote) Add documentation of why these are required
ENV PATH /usr/local/cuda/bin${PATH:+:${PATH}}
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64/stubs:/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

RUN echo "Completed cuda snippet" && env | grep PATH && dpkg -s cuda-toolkit