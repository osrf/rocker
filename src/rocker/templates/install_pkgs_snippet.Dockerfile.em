# User specified additional packages
RUN export DEBIAN_FRONTEND=noninteractive; \
    apt-get update \
    @# List each package specified in packages list
    && apt-get install -y @[for package in packages] @package @[end for] \
    # Clean
    && apt-get clean
