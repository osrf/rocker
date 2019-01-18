# Package needed to backport for xenial to run

cd /tmp/

wget http://ftp.osuosl.org/pub/ubuntu/pool/universe/p/python-distro/python3-distro_1.0.1-2_all.deb
wget http://ftp.osuosl.org/pub/ubuntu/pool/universe/p/python-docker/python3-docker_2.5.1-1_all.deb
wget http://security.ubuntu.com/ubuntu/pool/main/r/requests/python3-requests_2.18.4-2ubuntu0.1_all.deb
wget http://ftp.osuosl.org/pub/ubuntu/pool/main/c/chardet/python3-chardet_3.0.4-1_all.deb
wget http://ftp.osuosl.org/pub/ubuntu/pool/main/p/python-urllib3/python3-urllib3_1.22-1_all.deb
wget http://ftp.osuosl.org/pub/ubuntu/pool/universe/w/websocket-client/python3-websocket_0.44.0-0ubuntu2_all.deb
wget http://ftp.osuosl.org/pub/ubuntu/pool/universe/d/docker-pycreds/python3-dockerpycreds_0.2.1-1_all.deb
# Note might need to change arch assuming amd64
wget http://ftp.osuosl.org/pub/ubuntu/pool/universe/g/golang-github-docker-docker-credential-helpers/golang-docker-credential-helpers_0.5.0-2_amd64.deb

# Ensure a few dependencies
sudo apt-get install -y libsecret-1-0 libsecret-common python3-idna python3-pkg-resources python3-six


sudo dpkg -i python3-distro_1.0.1-2_all.deb
sudo apt-get install python3-certifi
sudo dpkg -i golang-docker-credential-helpers_0.5.0-2_amd64.deb
sudo dpkg -i python3-dockerpycreds_0.2.1-1_all.deb
sudo dpkg -i python3-chardet_3.0.4-1_all.deb
sudo dpkg -i python3-urllib3_1.22-1_all.deb
sudo dpkg -i python3-websocket_0.44.0-0ubuntu2_all.deb
sudo dpkg -i python3-requests_2.18.4-2ubuntu0.1_all.deb
sudo dpkg -i python3-docker_2.5.1-1_all.deb

