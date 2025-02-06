# workspace development helpers

# TODO(tfoote) This could be optimized to skip repeated apt updates.
@[ if rmw ]@
RUN \
  if [ -z "${ROS_DISTRO}" ]; then echo "ROS_DISTRO is unset cannot override RMW" ; exit 1 ; fi ;\
@[for package in packages]@
  if ! dpkg -l @(packages) | grep -q ^ii ; then \
  apt-get update && \
  DEBIAN_FRONTENT=non-interactive apt-get install -qy --no-install-recommends\
    @(package) ;\
  else \
  echo "Found rmw package @(package) no need to install" ; \
  fi ; \
@[end for]@
  apt-get clean ;\
echo "Done detecting packages for rmw"
@[ end if ]@

