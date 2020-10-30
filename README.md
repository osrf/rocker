# rocker

A tool to run docker images with customized local support injected for things like nvidia support. And user id specific files for cleaner mounting file permissions.

## Know extensions

Rocker supports extensions via entry points there are some built in but you can add your own. Here's a list of public repositories with extensions.

- Off-your-rocker: https://github.com/sloretz/off-your-rocker

# Prerequisites

This should work on most systems using with a recent docker version available.

Docker installation instructions: https://docs.docker.com/install/

## NVIDIA settings

For the NVIDIA option this has been demonstrated using Ubuntu 16.04.5 running Kernel 4.15 and nvidia docker2 and the nvidia 384 driver.
It did not work using the nvidia 340 driver.

It's also been tested on Ubuntu 18.04 with the 390 Nvidia driver.

Install nvidia-docker 2: https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0)

## Intel integrated graphics support

For intel integrated graphics support you will need to mount through a specific device

```
--devices /dev/dri/card0
```


# Installation

## Debians (Recommended)
Debian packages are available from the ROS repositories. You can set them up in step one [here](http://wiki.ros.org/kinetic/Installation/Ubuntu) then come back.

Then you can `sudo apt-get install python3-rocker`

## PIP

If you're not on a Ubuntu or Debian platform.

Rocker is available via pip you can install it via pip using

`pip install rocker`



## Development
To set things up in a virtual environment for isolation is a good way. If you don't already have it install python3's venv module.

    sudo apt-get install python3-venv

Create a venv

    mkdir -p ~/rocker_venv
    python3 -m venv ~/rocker_venv

Install rocker

    cd ~/rocker_venv
    . ~/rocker_venv/bin/activate
    pip install git+https://github.com/osrf/rocker.git

For any new terminal re activate the venv before trying to use it.

    . ~/rocker_venv/bin/activate

### Testing

To run tests install nose and coverage in the venv

    . ~/rocker_venv/bin/activate
    pip install nose
    pip install coverage

Then you can run nosetests.

    nosetests-3.4 --with-coverage --cover-package rocker

Notes:

- Make sure to use the python3 instance of nosetest from inside the environment.
- The tests include an nvidia test which assumes you're using a machine with an nvidia gpu.


# Example usage


## Fly a drone

Example usage with an iris

    rocker --nvidia --x11 --user --home --pull --pulse tfoote/drone_demo

After the ekf converges, 

You can send a takeoff command and then click to command the vehicle to fly to a point on the map.


## Fly a plane

Example usage with a plane 

    rocker --nvidia --x11 --user --home --pull --pulse tfoote/drone_demo roslaunch sitl_launcher plane_demo.launch world_name:=worlds/plane.world gui:=false

In QGroundControl go ahead and make a mission, upload it, and then start the mission.

## ROS 2 rviz

    rocker --nvidia osrf/ros:crystal-desktop rviz2


## Generic gazebo

On Xenial

    rocker --nvidia osrf/ros:kinetic-desktop-full gazebo

On Bionic

    rocker --nvidia osrf/ros:melodic-desktop-full gazebo
