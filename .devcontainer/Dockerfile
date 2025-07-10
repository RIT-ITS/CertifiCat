FROM mcr.microsoft.com/devcontainers/python:1-3.13-bullseye

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    mariadb-client \
    certbot \
    xmlsec1 \
    iputils-ping \
    jq \
    software-properties-common \
    clang 
    
RUN wget -c https://go.dev/dl/go1.24.2.linux-amd64.tar.gz && \
    tar -C /usr/local/ -xzf go1.24.2.linux-amd64.tar.gz

RUN cd /opt && \
    git clone https://github.com/letsencrypt/pebble/ && \
    cd pebble && \
    cp /opt/pebble/test/certs/pebble.minica.pem /usr/local/share/ca-certificates/pebble.minica.crt && \
    update-ca-certificates

RUN pip install yq

USER 1000

# Install pebble test ACME server
RUN cd /opt/pebble && \
    /usr/local/go/bin/go install -buildvcs=false ./cmd/pebble
# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

EXPOSE 8000