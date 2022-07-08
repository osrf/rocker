# Installation instructions from NVIDIA:
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Debian&target_version=11&target_type=deb_network
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget software-properties-common gnupg2 \
    && apt-get dist-upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Enable contrib on debian to get required
# https://packages.debian.org/bullseye/glx-alternative-nvidia


RUN \
  @[if download_osstring == 'ubuntu']@
  wget https://developer.download.nvidia.com/compute/cuda/repos/@(download_osstring)@(download_verstring)/x86_64/cuda-@(download_osstring)@(download_verstring).pin \
  && mv cuda-@(download_osstring)@(download_verstring).pin /etc/apt/preferences.d/cuda-repository-pin-600 && \ 
  @[else]@  
  sed -i 's/main/main contrib/' /etc/apt/sources.list && \
  @[end if]@
  apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/@(download_osstring)@(download_verstring)/x86_64/@(download_keyid).pub \
  && add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/@(download_osstring)@(download_verstring)/x86_64/ /" \
  && apt-get update \
  && apt-get -y install cuda nvidia-cuda-dev \
  && rm -rf /var/lib/apt/lists/*

# File conflict problem with libnvidia-ml.so.1 and libcuda.so.1
# https://github.com/NVIDIA/nvidia-docker/issues/1551
RUN rm -rf /usr/lib/x86_64-linux-gnu/libnv*
RUN rm -rf /usr/lib/x86_64-linux-gnu/libcuda*

# TODO(tfoote) Add documentation of why these are required
ENV PATH /usr/local/cuda/bin${PATH:+:${PATH}}
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64/stubs:/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
