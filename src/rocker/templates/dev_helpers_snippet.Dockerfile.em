# workspace development helpers
RUN apt-get update \
 && apt-get install -y \
    byobu \
    emacs \
 && apt-get clean
