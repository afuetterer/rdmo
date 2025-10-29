FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

COPY packages.txt /tmp/packages.txt
RUN apt-get update \
  && xargs -a /tmp/packages.txt apt-get install -y --no-install-recommends \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/packages.txt
