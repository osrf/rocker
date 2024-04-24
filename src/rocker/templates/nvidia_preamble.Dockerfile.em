# Ubuntu 16.04 with nvidia-docker2 beta opengl support
@{suffix = image_distro_version if image_distro_version in ['16.04', '18.04', '20.04', '22.04'] else '22.04'}@
FROM nvidia/opengl:1.0-glvnd-devel-ubuntu@(suffix) as glvnd
