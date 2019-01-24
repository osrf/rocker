# Package needed to backport for xenial to run

cd /tmp/
# a simple way backport python3-distro for xenial fron bionic
wget http://ftp.osuosl.org/pub/ubuntu/pool/universe/p/python-distro/python3-distro_1.0.1-2_all.deb
sudo dpkg -i python3-distro_1.0.1-2_all.deb
