# Installation instructions from NVIDIA:
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Debian&target_version=11&target_type=deb_network
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network

# Keep the dockerfile non-interactive
# TODO(tfoote) make this more generic/shared across instances
ARG DEBIAN_FRONTEND=noninteractive

# Prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
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
  apt-get update && \
  apt-get -y install cuda-toolkit && \
  rm -rf /var/lib/apt/lists/*

# File conflict problem with libnvidia-ml.so.1 and libcuda.so.1
# https://github.com/NVIDIA/nvidia-docker/issues/1551
RUN rm -rf /usr/lib/x86_64-linux-gnu/libnv*
RUN rm -rf /usr/lib/x86_64-linux-gnu/libcuda*

# TODO(tfoote) Add documentation of why these are required
ENV PATH /usr/local/cuda/bin${PATH:+:${PATH}}
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64/stubs:/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}