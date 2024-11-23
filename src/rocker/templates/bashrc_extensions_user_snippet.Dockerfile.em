WORKDIR @home_dir
RUN echo "\n# Source custom bashrc extensions" >> @home_dir/.bashrc
@[for path, filename in bashrc_extension_files.items()]
COPY @path @filename
RUN echo ". ~/@filename" >> @home_dir/.bashrc
@[end for]
