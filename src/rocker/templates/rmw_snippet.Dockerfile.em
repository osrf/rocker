# workspace development helpers


@[ if rmw ]@
RUN \
  if [ -z "${ROS_DISTRO}" ]; then echo "ROS_DISTRO is unset cannot override RMW" ; exit 1 ; fi ;\
  if dpkg -l @(' '.join(packages)) > /dev/null 2>&1; then \
   apt-get update \
   && DEBIAN_FRONTENT=non-interactive apt-get install -qy --no-install-recommends\
     @(' '.join(packages)) \
   && apt-get clean ;\
  else \
   echo "Found rmw packages @(' '.join(packages)) no need to install" ; \
  fi
@[ end if ]@

