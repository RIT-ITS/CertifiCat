FROM python:3.13.0-slim-bookworm AS base

RUN cat <<EOF > /etc/apt/sources.list
deb http://mirrors.rit.edu/debian bookworm-updates main
deb http://mirrors.rit.edu/debian bookworm main
EOF

FROM base AS builder

RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    curl \
    gcc \        
    musl-dev \
    libffi-dev \
    npm \
    make && \
    npm install --global yarn

COPY --from=src ./ /code/

WORKDIR /code/frontend

RUN yarn && \
    ./node_modules/.bin/webpack --env production 

WORKDIR /code/

RUN pip3 install uv && \
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
    libmariadb-dev \
    nginx \
    xz-utils

# Remove default nginx config
RUN rm /etc/nginx/sites-enabled/default

ARG GUNICORN_VERSION=21.2.0

# Django runs as the certificat user and it needs to own
# the directory where gunicorn creates its socket
RUN useradd -ms /bin/bash certificat && \
    mkdir /run/certificat && \
    chown certificat /run/certificat
    
# TODO: Look at permissions of gunicorn socket file
# TODO: Look at making nginx run as non-root user

# Install certificat and any other copied dependencies
RUN pip3 install ./deps/* && \
    pip3 install \
    gunicorn==${GUNICORN_VERSION}

# Overlay static configuration and runtime files
COPY --from=dockerfiles /srv /srv/
COPY --from=dockerfiles /etc /etc/

RUN pip install supervisor && pip uninstall pip -y && \
    apt install ncdu redis -y && \
    apt purge -y gcc && apt clean -y && apt autoremove -y && \
    rm -rf /var/lib/apt && rm -rf /var/lib/dpkg && \
    rm -rf /var/cache/ && \
    rm -rf /root/.cache && \
    find /usr/local | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

FROM scratch AS prod_flattened

COPY --from=prod / /

ENTRYPOINT [ "/srv/www/entrypoint.sh" ]
EXPOSE 80