# workspace development helpers


@[ if rmw ]@
RUN if [ -z "${ROS_DISTRO}" ]; then echo "ROS_DISTRO is unset cannot override RMW" ; exit 1 ; fi \
 && apt-get update \
 && apt-get install -y \
    ros-${ROS_DISTRO}-rmw-@(rmw)-cpp \
    ros-${ROS_DISTRO}-rmw-dds-common \
 && apt-get clean
@[ end if ]@

# working around recent upgrade of dds-common from 2.x to 3.x which is out of date in the image
