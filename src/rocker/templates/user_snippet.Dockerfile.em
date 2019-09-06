# make sure sudo is installed to be able to give user sudo access in docker
RUN apt-get update \
 && apt-get install -y \
    sudo \
 && apt-get clean

@[if name != 'root']@
RUN existing_user_by_uid=`getent passwd "@(uid)" | cut -f1 -d: || true` && \
    if [ -n "${existing_user_by_uid}" ]; then userdel -r "${existing_user_by_uid}"; fi && \
    existing_user_by_name=`getent passwd "@(name)" | cut -f1 -d: || true` && \
    if [ -n "${existing_user_by_name}" ]; then userdel -r "${existing_user_by_name}"; fi && \
    existing_group_by_gid=`getent group "@(gid)" | cut -f1 -d: || true` && \
    if [ -z "${existing_group_by_gid}" ]; then \
      groupadd -g "@(gid)" "@name"; \
    fi && \
    useradd --no-log-init --uid "@(uid)" -s "@(shell)" -c "@(gecos)" -g "@(gid)" -d "@(dir)" "@(name)" -m && \
    echo "@(name) ALL=NOPASSWD: ALL" >> /etc/sudoers.d/rocker

# Commands below run as the developer user
USER @(name)
@[else]@
# Detected user is root, which already exists so not creating new user.
@[end if]@
