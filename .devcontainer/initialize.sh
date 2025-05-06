#!/usr/bin/env bash

ENV_FILE=".devcontainer/.env"

# shellcheck disable=SC1090
test -f $ENV_FILE && source $ENV_FILE

gen-random() {
    length="${1}"
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c $length
}

IDP_KEY_PATH=".devcontainer/pyidp/idp.key"
IDP_CERT_PATH=".devcontainer/pyidp/idp.crt"
if [ ! -f "${IDP_KEY_PATH}" ]; then
    echo "Generating pyIdP keypair..."
    mkdir -p ".devcontainer/pyidp"
    (cd ".devcontainer/pyidp" && openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout "idp.key" -out "idp.crt" -subj "/CN=pyidp.localtest.me" <<< "y")
fi

echo """
# Created by initialize.sh, edits may be lost.
_DJ_MYSQL_ROOT_PWD=${_DJ_MYSQL_ROOT_PWD:-$(gen-random 10)}
_DJ_REDIS_PWD=${_DJ_REDIS_PWD:-$(gen-random 10)}
_DJ_SECRET_KEY=${_DJ_SECRET_KEY:-$(gen-random 40)}
_PYIDP_SECRET_KEY=${_PYIDP_SECRET_KEY:-$(gen-random 10)}
_PYIDP_KEY=\"$(cat "$IDP_KEY_PATH")\"
_PYIDP_CERT=\"$(cat "$IDP_CERT_PATH")\"
""" > $ENV_FILE

echo """

 ██████╗███████╗██████╗ ████████╗██╗███████╗██╗ ██████╗ █████╗ ████████╗
██╔════╝██╔════╝██╔══██╗╚══██╔══╝██║██╔════╝██║██╔════╝██╔══██╗╚══██╔══╝
██║     █████╗  ██████╔╝   ██║   ██║█████╗  ██║██║     ███████║   ██║
██║     ██╔══╝  ██╔══██╗   ██║   ██║██╔══╝  ██║██║     ██╔══██║   ██║
╚██████╗███████╗██║  ██║   ██║   ██║██║     ██║╚██████╗██║  ██║   ██║
 ╚═════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝

Thanks for your involvement! Consult the README for a quickstart guide.
Additionally, the scripts/omnidev script contains a collection of useful development commands.

If you find any issues don't hesitate to reach out: https://github.com/RIT-ITS/CertifiCat/issues
We also accept pull requests: https://github.com/RIT-ITS/CertifiCat/pulls
"""