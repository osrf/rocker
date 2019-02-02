# Ubuntu 16.04 with nvidia-docker2 beta opengl support
FROM nvidia/opengl:1.0-glvnd-devel-@(image_distro_id.lower())@(image_distro_version) as glvnd
