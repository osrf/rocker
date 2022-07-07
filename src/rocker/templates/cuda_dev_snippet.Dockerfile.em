RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates && \
    apt-key del 7fa2af80 && \
    curl -L -O https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb && \
    sudo sed -i '/developer\.download\.nvidia\.com\/compute\/cuda\/repos/d' /etc/apt/sources.list && \
    apt-get purge --autoremove -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda nvidia-cuda-dev \
    && rm -rf /var/lib/apt/lists/*

# File conflict problem with libnvidia-ml.so.1 and libcuda.so.1
# https://github.com/NVIDIA/nvidia-docker/issues/1551
RUN rm -rf /usr/lib/x86_64-linux-gnu/libnv*
RUN rm -rf /usr/lib/x86_64-linux-gnu/libcuda*

ENV PATH /usr/local/cuda/bin${PATH:+:${PATH}}
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64/stubs:/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}compute,utility
