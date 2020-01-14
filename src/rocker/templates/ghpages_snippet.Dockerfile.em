ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -q -y curl net-tools python python-yaml build-essential nodejs ruby-full autoconf automake libtool pkg-config zlib1g-dev
RUN echo "gem: --no-ri --no-rdoc" > ~/.gemrc
RUN gem install bundler
RUN gem install jekyll
RUN gem install github-pages

EXPOSE 4000
VOLUME /tmp/jekyll
WORKDIR /tmp/jekyll
