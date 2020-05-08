# Ubuntu 16.04 with nvidia-docker2 beta opengl support
@{suffix = '16.04' if image_distro_version == '16.04' else '18.04'}@
FROM nvidia/opengl:1.0-glvnd-devel-ubuntu@(suffix) as glvnd
