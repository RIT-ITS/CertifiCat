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