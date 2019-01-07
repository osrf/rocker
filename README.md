# rocker

A tool to run docker images with customized local support injected for things like nvidia support. And user id specific files for cleaner mounting file permissions.

# Prerequisites

This should work on most systems using with a recent docker version available. 

## NVIDIA settings

For the NVIDIA option this has been demonstrated using Ubuntu 16.04.5 running Kernel 4.15 and nvidia docker2 and the nvidia 384 driver.
It did not work using the nvidia 340 driver.

It's also expected to work with 18.04 and a recent nvidia driver as well.


# Installation

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
    

# Example usage


## Fly a iris

Example usage with an iris

    rocker --nvidia --user --exec --pull --pulse tfoote/drone_demo roslaunch sitl_launcher demo.launch mavros:=true gui:=false

After the ekf converges, 

You can send a takeoff command and then click to command the vehicle to fly to a point on the map.


## Fly a plane

Example usage with a plane 

    rocker --nvidia --user --exec --pull --pulse tfoote/drone_demo roslaunch sitl_launcher plane_demo.launch world_name:=worlds/plane.world gui:=false

In QGroundControl go ahead and make a mission, upload it, and then start the mission.