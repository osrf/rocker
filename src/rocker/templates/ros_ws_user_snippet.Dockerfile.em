# This snippet exists because "rosdep install ..." is very slow.  It
# iterates through every package in a workspace and installs their
# dependencies one at a time; this can instead be used to aggregate
# all of the deps for an entire workspace and install them all at
# once, which is much faster.

@[if install_deps]
# pip deps
RUN rosdep update \
  && export PIP_DEPS="`rosdep resolve @[for rosdep in rosdeps]@rosdep @[end for]| grep '^#pip' -A1 --no-group-separator | grep -v '^#'`" \
  && if [ ! -z "$PIP_DEPS" ]; then pip install $PIP_DEPS; fi
@[end if]

RUN echo "\n# Source ROS environment" >> @home_dir/.bashrc
RUN echo ". /opt/ros/$ROS_DISTRO/setup.bash" >> @home_dir/.bashrc

RUN mkdir -p @home_dir/ros_ws/src
WORKDIR @home_dir/ros_ws

WORKDIR @home_dir/ros_ws/src
COPY ros_ws_src .

WORKDIR @home_dir/ros_ws
RUN catkin init
RUN catkin config --extend /opt/ros/$ROS_DISTRO
@[for build_tool_arg in build_tool_args]
RUN catkin config @build_tool_arg
@[end for]
@[if install_deps and build_source]
# If the build, devel, install, or log spaces are located in a root directory
# they'll need to be created and re-assigned ownership to the user
#RUN for SPACE_TYPE in 'build' 'devel' 'install' 'log'; \
#  do \
#    export SPACE_DIR=$(awk "/^${SPACE_TYPE}_space:/{print \$2}" .catkin_tools/profiles/default/config.yaml); \
#    case $SPACE_DIR in \
#      /*) mkdir -p $SPACE_DIR && chown user $SPACE_DIR ;; \
#    esac \
#  done
RUN catkin build -cs; exit 0 # todo this returns success even if build fails

RUN export INSTALL=$(awk '/^install:/{print $2}' .catkin_tools/profiles/default/config.yaml) \
  && if [ $INSTALL = 'true' ]; \
    then \
      export INSTALL_SPACE=$(awk '/^install_space:/{print $2}' .catkin_tools/profiles/default/config.yaml); \
      case $INSTALL_SPACE in \
        /*) echo ". $INSTALL_SPACE/setup.bash" >> @home_dir/.bashrc ;; \
        *) echo ". $(pwd)/$INSTALL_SPACE/setup.bash" >> @home_dir/.bashrc ;; \
      esac \
    else \
      export DEVEL_SPACE=$(awk '/^devel_space:/{print $2}' .catkin_tools/profiles/default/config.yaml); \
      case $DEVEL_SPACE in \
        /*) echo ". $DEVEL_SPACE/setup.bash" >> @home_dir/.bashrc ;; \
        *) echo ". $(pwd)/$DEVEL_SPACE/setup.bash" >> @home_dir/.bashrc ;; \
      esac \
  fi
@[end if]

#RUN rm -fr @home_dir/ros_ws/src

@[if ros_master_uri]
RUN echo 'export ROS_MASTER_URI="@ros_master_uri"' >> @home_dir/.bashrc
@[end if]
