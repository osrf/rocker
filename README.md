# rocker

A tool to run docker images with customized local support injected for things like nvidia support. And user id specific files for cleaner mounting file permissions.

## Know extensions

Rocker supports extensions via entry points there are some built in but you can add your own. Here's a list of public repositories with extensions.

- Off-your-rocker: https://github.com/sloretz/off-your-rocker

# Prerequisites

This should work on most systems using with a recent docker version available. 

## NVIDIA settings

For the NVIDIA option this has been demonstrated using Ubuntu 16.04.5 running Kernel 4.15 and nvidia docker2 and the nvidia 384 driver.
It did not work using the nvidia 340 driver.

It's also expected to work with 18.04 and a recent nvidia driver as well.


# Installation

## Debians
Debian packages are available from the ROS repositories. You can set them up in step one [here](http://wiki.ros.org/kinetic/Installation/Ubuntu) then come back.

Then you can `sudo apt-get install python3-rocker`

On Ubuntu older than bionic you will need to install python3-distro manually first. Pulled from [here](https://packages.ubuntu.com/bionic/all/python3-distro/download)

    cd /tmp
    wget http://ftp.osuosl.org/pub/ubuntu/pool/universe/p/python-distro/python3-distro_1.0.1-2_all.deb
    sudo dpkg -i python3-distro_1.0.1-2_all.deb


## PIP

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

    nosetests-3.4 --with-coverage --cover-package rocker -s test/

NOtes: 

- Make sure to use the python3 one from inside the environment.
- You also must run with the console output due to [#9](https://github.com/osrf/rocker/issues/9)
- The tests include an nvidia test which assumes you're using a machine with an nvidia gpu.


# Example usage


## Fly a iris

Example usage with an iris

    rocker --nvidia --user --pull --pulse tfoote/drone_demo roslaunch sitl_launcher demo.launch mavros:=true gui:=false

After the ekf converges, 

You can send a takeoff command and then click to command the vehicle to fly to a point on the map.


## Fly a plane

Example usage with a plane 

    rocker --nvidia --user --pull --pulse tfoote/drone_demo roslaunch sitl_launcher plane_demo.launch world_name:=worlds/plane.world gui:=false

In QGroundControl go ahead and make a mission, upload it, and then start the mission.
