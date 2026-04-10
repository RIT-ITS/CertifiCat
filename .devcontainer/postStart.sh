#!/usr/bin/env bash

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
ENV_FILE="${HERE}/.env"

# shellcheck disable=SC1090
test -f $ENV_FILE && source $ENV_FILE
sudo ln -sf "${HERE}/../scripts/omnidev" /usr/local/bin/omnidev

cat <<- EOF >/home/vscode/.bashrc
cat << EOD
 ██████╗███████╗██████╗ ████████╗██╗███████╗██╗ ██████╗ █████╗ ████████╗
██╔════╝██╔════╝██╔══██╗╚══██╔══╝██║██╔════╝██║██╔════╝██╔══██╗╚══██╔══╝
██║     █████╗  ██████╔╝   ██║   ██║█████╗  ██║██║     ███████║   ██║
██║     ██╔══╝  ██╔══██╗   ██║   ██║██╔══╝  ██║██║     ██╔══██║   ██║
╚██████╗███████╗██║  ██║   ██║   ██║██║     ██║╚██████╗██║  ██║   ██║
 ╚═════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝

1. Add databases:
MYSQL_PWD=${CERTIFICAT__DB__PASSWORD} mariadb -h mariadb. -uroot -e "CREATE DATABASE certificat;CREATE DATABASE test_certificat;"

2. Apply migrations and start services:
omnidev django migrate
omnidev start-services

3. Navigate to the service in your browser.
The standard way to expose the services is through Traefik. If you don't already have Traefik running, you can start it with the following command:

docker-compose -f .devcontainer/traefik.yml up --detach

Then navigate to https://certificat.dev.localhost

4. Enter secret pyIdP key when prompted
Secret Key: ${_PYIDP_SECRET_KEY}
EOD
EOF