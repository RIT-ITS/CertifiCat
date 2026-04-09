FROM python:3.13.3-alpine AS base

FROM base AS builder

ARG NODE_PACKAGE_URL=https://unofficial-builds.nodejs.org/download/release/v24.14.0/node-v24.14.0-linux-x64-musl.tar.gz

RUN apk update && \
    apk add --no-cache \
    curl \
    libstdc++ \
    musl-dev \
    libffi-dev \
    make \
    mariadb-dev \
    py3-virtualenv \
    nodejs \
    yarn \
    compiler-rt \
    clang

ENV CC=clang
COPY --from=src ./ /code/

WORKDIR /code/frontend

RUN yarn && \
    yarn build

WORKDIR /code/

ARG CERTIFICAT_VERSION
RUN pip3 install uv && \
    uv version ${CERTIFICAT_VERSION} && \
    uv build && \
    uv export --no-emit-workspace --no-hashes -o requirements-frozen.txt

ARG GUNICORN_VERSION=25.1.0
RUN python3 -m venv /venv/ && \
    /venv/bin/pip install \
        --no-cache-dir \
        -c requirements-frozen.txt \
        /code/dist/certificat-*.whl gunicorn==$GUNICORN_VERSION

FROM base AS prod

WORKDIR /srv/www

RUN apk update && \
     apk add --no-cache \
     bash \
     xmlsec \
     pkgconf \
     mariadb-dev \
     nginx \
     redis \
     yq \
     envsubst

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
    rm -rf /usr/lib/x86_64-linux-gnu/perl-base/

FROM scratch AS prod_flattened

COPY --from=prod / /

ENTRYPOINT [ "/srv/www/entrypoint.sh" ]
EXPOSE 80