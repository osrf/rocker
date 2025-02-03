# workspace development helpers


@[ if rmw ]@
RUN \
  if [ -z "${ROS_DISTRO}" ]; then echo "ROS_DISTRO is unset cannot override RMW" ; exit 1 ; fi ;\
@[for package in packages]@
  apt-get update ;\
  if ! dpkg -l @(packages) | grep -q ^ii ; then \
  DEBIAN_FRONTENT=non-interactive apt-get install -qy --no-install-recommends\
    @(package) \
  && apt-get clean ;\
  else \
  echo "Found rmw package @(package) no need to install" ; \
  fi ; \
@[end for]@
echo "Done detecting packages for rmw"
@[ end if ]@

