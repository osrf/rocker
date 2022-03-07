@[if image_distro_version == '20.04']@
# Commands from NVIDIA
# Base : https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/11.2.1/ubuntu20.04-x86_64/base/Dockerfile
# Runtime : https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/11.2.1/ubuntu20.04-x86_64/runtime/Dockerfile
# Dev : https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/11.2.1/ubuntu20.04-x86_64/dev/Dockerfile

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates && \
    apt-key del 7fa2af80 && \
    curl -L -O https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu2004/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get purge --autoremove -y curl \
    && rm -rf /var/lib/apt/lists/*

ENV CUDA_VERSION 11.2.1

ENV NV_CUDA_LIB_VERSION "11.2.1-1"
ENV NV_CUDA_CUDART_DEV_VERSION 11.2.146-1
ENV NV_NVML_DEV_VERSION 11.2.67-1
ENV NV_LIBNPP_DEV_VERSION 11.3.2.139-1
ENV NV_LIBCUSPARSE_DEV_VERSION 11.4.0.135-1
ENV NV_LIBCUBLAS_DEV_PACKAGE_NAME libcublas-dev-11-2
ENV NV_LIBCUBLAS_DEV_VERSION 11.4.1.1026-1
ENV NV_LIBCUBLAS_DEV_PACKAGE ${NV_LIBCUBLAS_DEV_PACKAGE_NAME}=${NV_LIBCUBLAS_DEV_VERSION}
ENV NV_LIBNCCL_DEV_PACKAGE_NAME libnccl-dev
ENV NV_LIBNCCL_DEV_PACKAGE_VERSION 2.8.4-1
ENV NCCL_VERSION 2.8.4-1
ENV NV_LIBNCCL_DEV_PACKAGE ${NV_LIBNCCL_DEV_PACKAGE_NAME}=${NV_LIBNCCL_DEV_PACKAGE_VERSION}+cuda11.2
ENV NV_LIBNCCL_PACKAGE libnccl2=${NV_LIBNCCL_DEV_PACKAGE_VERSION}+cuda11.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    libtinfo5 libncursesw5 \
    cuda-cudart-dev-11-2=${NV_CUDA_CUDART_DEV_VERSION} \
    cuda-command-line-tools-11-2=${NV_CUDA_LIB_VERSION} \
    cuda-minimal-build-11-2=${NV_CUDA_LIB_VERSION} \
    cuda-libraries-dev-11-2=${NV_CUDA_LIB_VERSION} \
    cuda-nvml-dev-11-2=${NV_NVML_DEV_VERSION} \
    libnpp-dev-11-2=${NV_LIBNPP_DEV_VERSION} \
    libcusparse-dev-11-2=${NV_LIBCUSPARSE_DEV_VERSION} \
    ${NV_LIBCUBLAS_DEV_PACKAGE} \
    ${NV_LIBNCCL_DEV_PACKAGE} \
    ${NV_LIBNCCL_PACKAGE} \
    && ln -s cuda-11.2 /usr/local/cuda \
    && rm -rf /var/lib/apt/lists/*

# Keep apt from auto upgrading the cublas and nccl packages. See https://gitlab.com/nvidia/container-images/cuda/-/issues/88
RUN apt-mark hold ${NV_LIBCUBLAS_DEV_PACKAGE_NAME} ${NV_LIBNCCL_DEV_PACKAGE_NAME}

## Required for nvidia-docker v1
#RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf \
#    && echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64${LD_LIBRARY_PATH}

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}compute,utility
ENV NVIDIA_REQUIRE_CUDA "cuda>=11.2 brand=tesla,driver>=418,driver<419 brand=tesla,driver>=440,driver<441 driver>=450,driver<451"

@[end if]@
