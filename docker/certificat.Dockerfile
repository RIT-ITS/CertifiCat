FROM python:3.13.3-alpine AS base

FROM base AS builder

ARG NODE_PACKAGE_URL=https://unofficial-builds.nodejs.org/download/release/v22.9.0/node-v22.9.0-linux-x64-musl.tar.gz

RUN apk update && \
    apk add --no-cache \
    curl \
    libstdc++ \
    gcc \        
    musl-dev \
    libffi-dev \
    make \
    mariadb-dev \
    py3-virtualenv 

RUN wget $NODE_PACKAGE_URL && \
    mkdir -p /opt/nodejs && \
    tar -zxvf *.tar.gz --directory /opt/nodejs --strip-components=1 && \
    rm *.tar.gz && \
    ln -s /opt/nodejs/bin/node /usr/local/bin/node && \
    ln -s /opt/nodejs/bin/npm /usr/local/bin/npm && \
    npm install --global yarn

COPY --from=src ./ /code/

WORKDIR /code/frontend

RUN /opt/nodejs/lib/node_modules/yarn/bin/yarn && \
    ./node_modules/.bin/webpack --env production 

WORKDIR /code/

RUN pip3 install uv && \
    uv build && \
    uv export --no-emit-workspace --no-hashes -o requirements-frozen.txt

ARG GUNICORN_VERSION=21.2.0

RUN python3 -m venv /venv/ && \
    /venv/bin/pip install \
        --no-cache-dir \
        -c requirements-frozen.txt \
        /code/dist/certificat-*.whl gunicorn==$GUNICORN_VERSION

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