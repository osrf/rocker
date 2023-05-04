# make sure sudo is installed to be able to give user sudo access in docker
RUN if ! command -v sudo >/dev/null; then \
      apt-get update \
      && apt-get install -y sudo \
      && apt-get clean; \
    fi

@[if name != 'root']@
RUN existing_user_by_uid=`getent passwd "@(uid)" | cut -f1 -d: || true` && \
    if [ -n "${existing_user_by_uid}" ]; then userdel @('' if user_preserve_home else '-r') "${existing_user_by_uid}"; fi && \
    existing_user_by_name=`getent passwd "@(name)" | cut -f1 -d: || true` && \
    existing_user_uid=`getent passwd "@(name)" | cut -f3 -d: || true` && \
    if [ -n "${existing_user_by_name}" ]; then find / -uid ${existing_user_uid} -exec chown -h @(uid) {} + || true ; find / -gid ${existing_user_uid} -exec chgrp -h @(uid) {} + || true ; fi && \
    if [ -n "${existing_user_by_name}" ]; then userdel @('' if user_preserve_home else '-r') "${existing_user_by_name}"; fi && \
    existing_group_by_gid=`getent group "@(gid)" | cut -f1 -d: || true` && \
    if [ -z "${existing_group_by_gid}" ]; then \
      groupadd -g "@(gid)" "@name"; \
    fi && \
    useradd --no-log-init --no-create-home --uid "@(uid)" @(str('-s ' + shell) if shell else '') -c "@(gecos)" -g "@(gid)" -d "@(dir)" "@(name)" && \
@[if user_groups != '']@
    user_groups="@(user_groups)" && \
    for groupinfo in ${user_groups}; do \
      existing_group_by_name=`getent group ${groupinfo%;*} || true`; \
      existing_group_by_gid=`getent group ${groupinfo#*;} || true`; \
      if [ -z "${existing_group_by_name}" ] && [ -z "${existing_group_by_gid}" ]; then \
        groupadd -g "${groupinfo#*;}" "${groupinfo%;*}" && usermod -aG "${groupinfo%;*}" "@(name)" @(('|| (true && echo "user-preserve-group-permissive Enabled, continuing without processing group $groupinfo" )') if user_preserve_groups_permissive else '') || (echo "Failed to add group ${groupinfo%;*}, consider option --user-preserve-group-permissive" && exit 2); \
      elif [ "${existing_group_by_name}" = "${existing_group_by_gid}" ]; then \
        usermod -aG "${groupinfo%;*}" "@(name)" @(('|| (true && echo "user-preserve-group-permissive Enabled, continuing without processing group $groupinfo" )') if user_preserve_groups_permissive else '') || (echo "Failed to adjust group ${groupinfo%;*}, consider option --user-preserve-group-permissive" && exit 2); \
      fi; \
    done && \
@[end if]@
    echo "@(name) ALL=NOPASSWD: ALL" >> /etc/sudoers.d/rocker

@[if not home_extension_active ]@
# Making sure a home directory exists if we haven't mounted the user's home directory explicitly
RUN mkdir -p "$(dirname "@(dir)")" && mkhomedir_helper @(name)
@[end if]@
# Commands below run as the developer user
USER @(name)
WORKDIR @(dir)
@[else]@
# Detected user is root, which already exists so not creating new user.
@[end if]@
