# rocker

A tool to run docker images with local support injected for things like nvidia support. And user id specific files for cleaner mounting file permissions.

# Installation

To set things up in a virtual environment for isolation is a good way. If you don't already have it install python3's venv module.

    sudo apt-get install python3-venv

Create a venv

    mkdir -p ~/rocker_venv
    python3 -m venv ~/rocker_venv

Install rocker

    cd ~/rocker_venv
    . ~/rocker_venv/bin/activate
    pip install git+https://github.com/tfoote/rocker.git

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