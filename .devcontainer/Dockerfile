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

RUN pip install yq

# Install uv
USER 1000
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

EXPOSE 8000