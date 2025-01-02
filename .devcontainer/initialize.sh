#!/usr/bin/env bash

ENV_FILE=".devcontainer/.env"

# shellcheck disable=SC1090
test -f $ENV_FILE && source $ENV_FILE

gen-random() {
    length="${1}"
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c $length
}

echo """
# Created by initialize.sh, edits may be lost.
_DJ_MYSQL_ROOT_PWD=${_DJ_MYSQL_ROOT_PWD:-$(gen-random 10)}
_DJ_REDIS_PWD=${_DJ_REDIS_PWD:-$(gen-random 10)}
_DJ_SECRET_KEY=${_DJ_SECRET_KEY:-$(gen-random 40)}""" > $ENV_FILE

CERT_PATH=".devcontainer/traefik/certs/cert.pem"
if [ ! -f "${CERT_PATH}" ]; then
    (cd ".devcontainer/traefik/certs" && openssl req -config traefik.cnf -new -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650 -nodes -extensions 'req_ext')
fi