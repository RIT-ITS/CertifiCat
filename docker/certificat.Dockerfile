FROM python:3.11.7-slim-bookworm AS base

FROM base AS builder

RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    curl \
    gcc \        
    musl-dev \
    libffi-dev \
    npm \
    make

COPY --from=src ./ /code/

WORKDIR /code/frontend

RUN npm install && \
    ./node_modules/.bin/webpack --env production 

WORKDIR /code/
 
RUN ls -al && curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.local/bin/env && \
    uv build

FROM base AS prod

RUN mkdir -p /srv/www/deps/
WORKDIR /srv/www

COPY --from=builder /code/dist/certificat*.whl /srv/www/deps/
# TODO: Fix this! Push acmev2 to pypi
ADD https://www-staging.rit.edu/test/clay/acme/UFUgUENQVSBXSEFUIGNhY2l0cyB0dHkyIEZyaTA3IDIyZGF5cyAzOjA4bSAw/acmev2-0.0.2.tar.gz /srv/www/deps/acmev2-0.0.2.tar.gz

RUN apt-get update && \
    apt-get -y install --no-install-recommends \    
    xmlsec1 \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    nginx \
    supervisor

# Remove default nginx config
RUN rm /etc/nginx/sites-enabled/default

ARG GUNICORN_VERSION=21.2.0

# Django runs as the certificat user and it needs to own
# the directory where gunicorn creates its socket
RUN useradd -ms /bin/bash certificat && \
    mkdir /run/certificat && \
    chown certificat /run/certificat

# Install certificat and any other copied dependencies
RUN pip3 install ./deps/* && \
    pip3 install \
    gunicorn==${GUNICORN_VERSION}

# Overlay static configuration and runtime files
COPY --from=dockerfiles /srv /srv/
COPY --from=dockerfiles /etc /etc/

ENTRYPOINT [ "/srv/www/entrypoint.sh" ]
EXPOSE 80