# rocker

A tool to run docker images with customized local support injected for things like nvidia support. And user id specific files for cleaner mounting file permissions.

## Difference from docker-compose

A common question about rocker is how is it different than `docker-compose`.
`rocker` is designed to solve a similar but different problem than `docker-compose`.
The primary goal of `rocker` is to support the use of Docker in use cases where the containers will be effected by the local environment.
A primary example of this is setting up file permissions inside the container to match the users outside of the container so that mounted files inside the container have the same UID as the host.
Doing this enables quickly going in and out of different containrs while leverating the same workspace on your host for testing on different platforms etc.
This is done by dynamically generating overlays on the same core image after detecting the local conditions required.

The secondary feature that `rocker` provides that docker-compose does not address is the ability to inject extra use case specific capabilities into a container before running.
A common example is the ability to use NVIDIA drivers on a standard published image.
`rocker` will take that standard published image and both inject the necessary drivers into the container which will match your host driver and simultaneously set the correct runtime flags.
This is possible to do with docker-compose or straight docker.
But the drawbacks are that you have to build and publish the combinatoric images of all possible drivers, and in addition you need to manually make sure to pass all the correct runtime arguments.
This is especially true if you want to combine multiple possible additional features, such that the number of images starts scaling in a polynomic manner and maintenance of the number of images becomes unmanagable quickly.
Whereas with `rocker` you can invoke your specific plugins and it will use multi-stage builds of docker images to customize the container for your specific use case, which lets you use official upstream docker images without requiring you to maintain a plethora of parallel built images.



## Know extensions

Rocker supports extensions via entry points there are some built in but you can add your own.

### Integrated Extensions

There are a number of integrated extensions here's some of the highlights.
You can get full details on the extensions from the main `rocker --help` command.

- x11 -- Enable the use of X11 inside the container via the host X instance.
- nvidia -- Enable NVIDIA graphics cards for rendering
- cuda -- Enable NVIDIA CUDA in the container
- user -- Create a user inside the container with the same settings as the host and run commands inside the container as that user.
- home -- Mount the user's home directory into the container
- pulse -- Mount pulse audio into the container
- ssh -- Pass through ssh access to the container.

As well as access to many of the docker arguments as well such as `device`, `env`, `volume`, `name`, `network`, and `privileged`.

### Externally maintained extensions

Here's a list of public repositories with extensions.

- Off-your-rocker: https://github.com/sloretz/off-your-rocker



# Prerequisites

This should work on most systems using with a recent docker version available.

Docker installation instructions: https://docs.docker.com/install/

## NVIDIA settings

For the NVIDIA option this has been tested on the following systems using nvidia docker2:

| Ubuntu distribution | Linux Kernel | Nvidia drivers                                    |
| ------------------- | ------------ | ------------------------------------------------- |
| 16.04               | 4.15         | nvidia-384 (works) <br> nvidia-340 (doesn't work) |
| 18.04               |              | nvidia-390 (works)                                |
| 20.04               | 5.4.0        | nvidia-driver-460 (works)                         |
| 22.04               | 5.13.0        | nvidia-driver-470 (works)                         |

Install nvidia-docker 2: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker

### Additional Configuration for rootless mode
For executing Docker as a non-root user, separate installation instructions are provided here: https://docs.docker.com/engine/security/rootless/

After installing Rootless Docker, the nvidia-docker2 package can be installed as usual from the website above.
Currently, [cgroups are not supported in rootless mode](https://github.com/moby/moby/issues/38729) so we need to change `no-cgroups` in */etc/nvidia-container-runtime/config.toml*

```shell
[nvidia-container-cli]
no-cgroups = true
```

Note, that changing this setting will lead to a `Failed to initialize NVML: Unknown Error` if Docker is executed as root (noted [here](https://github.com/NVIDIA/nvidia-container-runtime/issues/85)).

## Intel integrated graphics support

For [Intel integrated graphics support](https://www.intel.com/content/www/us/en/develop/documentation/get-started-with-ai-linux/top/using-containers/using-containers-with-the-command-line.html) you will need to mount the `/dev/dri` directory as follows:

```
--devices /dev/dri
```

# Installation

## Debians (Recommended)
Debian packages are available from the ROS repositories. You can set them up in step one [here](http://wiki.ros.org/kinetic/Installation/Ubuntu) then come back.

Then you can `sudo apt-get install python3-rocker`

## PIP

If you're not on a Ubuntu or Debian platform.

Rocker is available via pip you can install it via pip using

`pip install rocker`

## Archlinux ([AUR](https://aur.archlinux.org/))

Using any AUR helper, for example, with `paru`

```bash
paru -S python-rocker
```

or 

```bash
paru -S python-rocker-git
```

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

To run tests install the 'test' extra and pytest-cov in the venv

    . ~/rocker_venv/bin/activate
    pip install -e .[test] pytest-cov

Then you can run pytest.

    python3 -m pytest --cov=rocker

Notes:

- Make sure to use the python3 instance of pytest from inside the environment.
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

    rocker --nvidia --x11 osrf/ros:crystal-desktop rviz2


## Generic gazebo

On Xenial

    rocker --nvidia --x11 osrf/ros:kinetic-desktop-full gazebo

On Bionic

    rocker --nvidia --x11 osrf/ros:melodic-desktop-full gazebo

## Volume mount

### For arguments with one element not colon separated

`--volume` adds paths as docker volumes.

**The last path must be terminated with two dashes `--`**.

    rocker --volume ~/.vimrc ~/.bashrc -- ubuntu:18.04

The above example of the volume option will be expanded via absolute paths for `docker run` as follows:

    --volume /home/<USERNAME>/.vimrc:/home/<USERNAME>/.vimrc --volume /home/<USERNAME>/.bashrc:/home/<USERNAME>/.bashrc  

### For arguments with colon separation

It will process the same as `docker`'s `--volume` option, `rocker --volume` takes 3 fields.
- 1st field: the path to the file or directory on the host machine.
- 2nd field: (optional) the path where the file or directory is mounted in the container.
   - If only the 1st field is supplied, same value as the 1st field will be populated as the 2nd field.
- 3rd field: (optional) bind propagation as `ro`, `z`, and `Z`. See [docs.docker.com](https://docs.docker.com/storage/bind-mounts/) for further detail.
