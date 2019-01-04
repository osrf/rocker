RUN mkdir -p /etc/pulse
RUN echo '\n\
# Connect to the hosts server using the mounted UNIX socket\n\
default-server = unix:/run/user/@(user_id)/pulse/native\n\
\n\
# Prevent a server running in the container\n\
autospawn = no\n\
daemon-binary = /bin/true\n\
\n\
# Prevent the use of shared memory\n\
enable-shm = false\n\
\n'\
> /etc/pulse/client.conf
