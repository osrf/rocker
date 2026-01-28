# Installation instructions from NVIDIA:
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Debian&target_version=11&target_type=deb_network
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network

# Detect if NVIDIA is already installed in the container at build time.
# If present, skip CUDA installation to avoid reinstalling.
# This addresses issue #316 where CUDA was being unnecessarily reinstalled.
RUN if ldconfig -p | grep -q libcuda.so || [ -f /proc/driver/nvidia/version ]; then \
      echo "NVIDIA detected inside container, skipping CUDA install"; \
    else \
      echo "NVIDIA not detected inside container, installing CUDA"; \
      export DEBIAN_FRONTEND=noninteractive; \
      apt-get update && apt-get install -y --no-install-recommends \
        wget software-properties-common gnupg2 && \
      wget -q https://developer.download.nvidia.com/compute/cuda/repos/@(download_osstring)@(download_verstring)/x86_64/cuda-keyring_1.1-1_all.deb && \
      dpkg -i cuda-keyring_1.1-1_all.deb && \
      rm cuda-keyring_1.1-1_all.deb && \
@[if download_osstring == 'debian']@ \
      add-apt-repository contrib && \
@[end if]@ \
      apt-get update && \
      apt-get -y install cuda-toolkit && \
      rm -rf /var/lib/apt/lists/* && \
      rm -rf /usr/lib/x86_64-linux-gnu/libnv* && \
      rm -rf /usr/lib/x86_64-linux-gnu/libcuda*; \
    fi

@# TODO(tfoote) Add documentation of why these are required
ENV PATH /usr/local/cuda/bin${PATH:+:${PATH}}
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64/stubs:/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
