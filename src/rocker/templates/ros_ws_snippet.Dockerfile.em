# Development-related required and optional utils
RUN export DEBIAN_FRONTEND=noninteractive; \
    apt-get update \
    && apt-get install -y python3-vcstool python3-wstool python3-catkin-tools python3-pip git openssh-client \
    # Clean
    && apt-get clean

@[if install_deps]
# Workspace apt dependencies
RUN export DEBIAN_FRONTEND=noninteractive; \
    export APT_DEPS="`rosdep resolve @[for rosdep in rosdeps]@rosdep @[end for]| grep '^#apt' -A1 --no-group-separator | grep -v '^#'`" \
    && if [ ! -z "$APT_DEPS" ]; then apt-get update && apt-get install -y $APT_DEPS && apt-get clean; fi
@[end if]