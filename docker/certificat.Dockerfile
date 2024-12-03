FROM python:3.13.0-alpine3.20 AS base

FROM base AS builder

ARG NVM_URL=https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh

RUN apk update && \
    apk add --no-cache \
    curl \
    libstdc++ \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    make \
    mariadb-dev \
    py3-virtualenv \
    bash

RUN curl -o- $NVM_URL | bash 

RUN export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    nvm install 23 && \
    npm install --global yarn

COPY --from=src ./ /code/

WORKDIR /code/frontend

RUN /opt/nodejs/lib/node_modules/yarn/bin/yarn && \
    ./node_modules/.bin/webpack --env production 

WORKDIR /code/

RUN pip3 install uv && \
    uv build

ARG GUNICORN_VERSION=21.2.0

ADD https://www-staging.rit.edu/test/clay/acme/UFUgUENQVSBXSEFUIGNhY2l0cyB0dHkyIEZyaTA3IDIyZGF5cyAzOjA4bSAw/acmev2-0.0.2.tar.gz /code/dist/acmev2-0.0.2.tar.gz
RUN python3 -m venv /venv/ && \
    /venv/bin/pip install --no-cache-dir /code/dist/certificat-*.whl /code/dist/acmev2* gunicorn==$GUNICORN_VERSION

# Bytecode will be generated on first run
RUN find /venv | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

FROM base AS prod

WORKDIR /srv/www

RUN apk update && \
     apk add --no-cache \
     bash \
     xmlsec \
     pkgconf \
     mariadb-dev \
     nginx \
     redis

# Django runs as the certificat user and it needs to own
# the directory where gunicorn creates its socket
RUN adduser -S certificat && \
     mkdir /run/certificat && \
     chown certificat:nginx /run/certificat && \
     chmod 0750 /run/certificat

# Add venv built in previous step
COPY --from=builder /venv /srv/www/.venv

# Overlay static configuration and runtime files
COPY --from=dockerfiles /srv /srv/
COPY --from=dockerfiles /etc /etc/

RUN pip install supervisor --no-cache-dir && pip uninstall pip -y && \
    find /usr/local | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf && \
    rm -rf /usr/lib/x86_64-linux-gnu/perl-base/

FROM scratch AS prod_flattened

COPY --from=prod / /

ENTRYPOINT [ "/srv/www/entrypoint.sh" ]
EXPOSE 80