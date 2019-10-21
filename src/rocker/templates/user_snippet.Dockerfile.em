# make sure sudo is installed to be able to give user sudo access in docker
RUN apt-get update \
 && apt-get install -y \
    sudo \
 && apt-get clean

@[if name != 'root']@
RUN groupadd -g "@(gid)" "@name" \
 && useradd --uid "@(uid)" -s "@(shell)" -c "@(gecos)" -g "@(gid)" -d "@(dir)" "@(name)" \
 && echo "@(name):@(name)" | chpasswd \
 && adduser @(name) sudo \
 && echo "@(name) ALL=NOPASSWD: ALL" >> /etc/sudoers.d/rocker
# Commands below run as the developer user
USER @(name)
@[else]@
# Detected user is root, which already exists so not creating new user.
@[end if]@