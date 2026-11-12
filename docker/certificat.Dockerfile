FROM python:3.15.2-alpine AS base

FROM base AS builder

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
    clang \
    # clang needs gcc's linker and startup files (crtbeginS.o etc.) to link C extensions
    gcc

ENV CC=clang
COPY --from=src ./ /code/

WORKDIR /code/frontend

RUN yarn && \
    yarn build

WORKDIR /code/

# The shenanigans here are necessary for two reasons:
#  1. The dependencies installed should be exactly what exists in the lockfile
#  2. Some dependencies may be unresolvable because of packages incorrectly 
#     limiting packages ranges.
#
# So this installs exactly what we have in dev without tooling making any changes.
ARG CERTIFICAT_VERSION=0.0.0
ARG GUNICORN_VERSION=27.0.0
# Build the venv at its final path, venv scripts record the path they were built at
ENV UV_PROJECT_ENVIRONMENT=/srv/www/.venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
# Install the dependencies exactly as they are in uv.lock, then the certificat wheel
# on top of them. pip can't be used here because it resolves dependencies again and
# ignores uv's override-dependencies.
RUN pip3 install uv && \
    # Fail if uv.lock is out of date with pyproject.toml
    uv lock --check && \
    # Set the version without re-locking
    uv version --frozen "${CERTIFICAT_VERSION}" && \
    uv sync --frozen --no-dev --no-install-project && \
    uv build --wheel && \
    # The dependencies are already installed from the lockfile, so don't resolve them again
    uv pip install --python "${UV_PROJECT_ENVIRONMENT}" --no-deps dist/certificat-*.whl && \
    uv pip install --python "${UV_PROJECT_ENVIRONMENT}" "gunicorn==${GUNICORN_VERSION}"

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
COPY --from=builder /srv/www/.venv /srv/www/.venv

# Overlay static configuration and runtime files
COPY --from=dockerfiles /srv /srv/
COPY --from=dockerfiles /etc /etc/

RUN pip install supervisor --no-cache-dir && pip uninstall pip -y && \
    rm -rf /usr/lib/x86_64-linux-gnu/perl-base/

FROM scratch AS prod_flattened

COPY --from=prod / /

ENTRYPOINT [ "/srv/www/entrypoint.sh" ]
EXPOSE 80