#!/usr/bin/env bash

# Build and test the docker image, not used in CI. All references to usernames and passwords
# are local.

set -euo pipefail

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE="$(realpath "${HERE}/../../")"

CONFIG_FILE="$(mktemp)"
cat >"$CONFIG_FILE" <<EOL
certificat:
  secret_key: "12345"
  debug: True
  url_root: "http://certificat.localtest.me"
  finalizer_module: "certificat.modules.acme.backends.local.LocalFinalizer"
  login_method: "local"

  db: 
    name: certificat
    user: root
    password: "root"
    host: tmpmariadb.

  redis:
    host: tmpredis.
    password: "password"

local_finalizer:
  key: |
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEAld0nGypEoP0EKuY1K7PA7auFw94EZy0l2KkbkOcgsdykDcka
    xAa1ST9n5VE96AMTObGWCZb5Fkwv/SPg/RduwcgBLG2y4DjAaR+LafNeRn4Nz7nZ
    85woRr5ojezgy5vzhxti0HqFT5VW1btl0XuPoDoviudJR7vW6koboVRberLJeaA1
    MiRPgxj5tAqlGxMVUEORZhwr5sBgxNNQFXmJzLBCSq2LWHyC75SQJ0AJ3RCNS1V/
    bLtxLj7T7qMji6zbQV3WmF1hQtmKACaCisrxxfg9EEZbTsRRntCOs4NGtRjU9H3n
    zrim9Sj3UjxgydIQ0UKF+DP1dIHbY6XrnowdFQIDAQABAoIBABDQtzYXmIq9yQ1t
    NjMYoMGqOMCg9TqEeNYmJ2crX+JFIQ1A7uVm4Ul+OVCkPH9/dNVI5U5fJ8TGOK49
    K94KFo3cvLD5ABSjmYdSGEkDmyTquO8BagCpGWXSsJWYKiL+dSVIP96nmLS0y4EA
    3WxTYmq2jKYXzIOlgnhYZ2BDQF50bCsjJhTX9+YcOGSkSB5iKPjJFWoj+uvUvKS5
    ar9otrbkNVhVC3PZl4yM3L1C3ubL8ZKPesAaZtGKsZ7Cgd59VVchzjWKrq39vBaU
    4EsxcLtyMlcGsxxPjnGZsj5GoayvAwl/URjslOl237HbpregbwFPdgor/32l0ImB
    Ot3FeIMCgYEAx7qRIgVs4q91SaEazRbV4QhIs7NvpZRq+b5iAOken1wo5xyRJ05q
    X1RFeNolE+pHeooJStemzLy8XSjfGj3e4UygORgca+AMM5xpw/pf3xEHgeQUzxyY
    ZgmXu2nBgBenKwdA+4zAS5Pmm3maI29gKNBN9pmnDpgseuw56d73xu8CgYEAwBYU
    y0kNhwnW80k0bzj9MABDM4FLevYtWb7G9+/ivFxFIghXnaRGajQFVC95rqUR7L0e
    Rphq3EBM7ssNjsLSmFcwEdXLPzOdlpMMxGkNuUIBrN+99mlCBJLMLaWrJh1OlOYt
    C3ErutGyRzYUAdAS8sCn/kexsaBAnyMGaJZC/DsCgYBsGn8TevxEddN11s061HFP
    K7yuByEW7g44vuMsuwDoIGnDLaMjMz4/+szfbLNE5DlsCeqdp7uQdVc+1TBsc7B/
    IYpXXMWFXe88wBw/BvV9NyppE5pvv3p9QBPwTH1/Z04D7BkwDi7GuXbIEDltlIrn
    jFemceQJ8jOhFNsDyrsx4QKBgQC+OyAM0yRagBwohG8xVzcnuprS/1FJTVRMdOuH
    0EK0WIz+z1Q2AuLZevtsDDhuBXxjAEhjkb8CsYt/UgjzQW5fALnSb/EBfpSq8qbK
    PWAiAIS4OD1hM4z2Cou7CT8eWBfizrH9iu7L7bCpZZ0azn51eubkpQwN5a8Z6w4F
    tgpQ0QKBgEiLRI5LxRrzek15RxIRO2QToxBqyXmNAgAPZvDBmQPWPGdF4Vsi16+D
    5KFSdaxo8ZLEDoAKtXbR+9THwRF9PzcvyducZp/dkUFr2x+PZ5yVTjQHwcAVd1Zu
    Wo7xleX2mpTnHQTjtv1NikkMkcIVMz0Y2pbLbhkYyQVG2v6lL4jB
    -----END RSA PRIVATE KEY-----
  cert: |
    -----BEGIN CERTIFICATE-----
    MIIC1DCCAbygAwIBAgIUQbnQ870aDubvty1Ph5DcCq92JnowDQYJKoZIhvcNAQEL
    BQAwFzEVMBMGA1UEAwwMYWNtZWNhLmxvY2FsMB4XDTI0MTAxNjE5Mzg0MVoXDTM0
    MTAxNDE5Mzg0MVowFzEVMBMGA1UEAwwMYWNtZWNhLmxvY2FsMIIBIjANBgkqhkiG
    9w0BAQEFAAOCAQ8AMIIBCgKCAQEAld0nGypEoP0EKuY1K7PA7auFw94EZy0l2Kkb
    kOcgsdykDckaxAa1ST9n5VE96AMTObGWCZb5Fkwv/SPg/RduwcgBLG2y4DjAaR+L
    afNeRn4Nz7nZ85woRr5ojezgy5vzhxti0HqFT5VW1btl0XuPoDoviudJR7vW6kob
    oVRberLJeaA1MiRPgxj5tAqlGxMVUEORZhwr5sBgxNNQFXmJzLBCSq2LWHyC75SQ
    J0AJ3RCNS1V/bLtxLj7T7qMji6zbQV3WmF1hQtmKACaCisrxxfg9EEZbTsRRntCO
    s4NGtRjU9H3nzrim9Sj3UjxgydIQ0UKF+DP1dIHbY6XrnowdFQIDAQABoxgwFjAU
    BgNVHREEDTALgglsb2NhbGhvc3QwDQYJKoZIhvcNAQELBQADggEBAE0ZJ8Kl9WzK
    lZFyNyz17fIYGzSej4XKhXk2IajzYaDCKS6pZabHnEuLdxoVqq2SY7Q6tic5vQFY
    20h+btoo/1rC80z328PfewDa98xJwd1v4TcKScBifHRw9KaRRPOHgYaeOeejZp3n
    PjtXes4kQEA6e6sgYFDqbG5RZPKCIbAJUbADPChJocYygrQBmido3tcxNN4PAy8R
    atZhtPs3UzZ4gYJY9wB+MeX5EpLPHQJpoLYQoJO+Q22JuFuPkTfIsQG/Fzvv+hzj
    0aRuPpTug5Kgc1VrD97fjbNVn5Q/v0d8eL+eB7jujTSSXg/iBTH9D/0MSTp0u2Mm
    qIQFqQ2WEBc=
    -----END CERTIFICATE-----
EOL

docker buildx build \
    --build-context "src=${WORKSPACE}/src/" \
    --build-context "dockerfiles=${WORKSPACE}/docker/certificat" \
    -f "${WORKSPACE}/docker/certificat.Dockerfile" "${WORKSPACE}" \
    #--tag ${CS_IMAGE} \
    #--tag ${IMAGE_TAG} \
    #--network host

LAST_IMAGE="$(docker images --format "{{.ID}} {{.CreatedAt}}" | sort -rk 2 | awk 'NR==1{print $1}')"
echo "Last image: ${LAST_IMAGE}"

docker rm -f tmpmariadb
docker rm -f tmpredis

docker run --name tmpmariadb -d --network docker_default -e MARIADB_DATABASE=certificat -e MARIADB_ROOT_PASSWORD=root mariadb:latest
docker run --name tmpredis -d --network docker_default redis:latest --requirepass password

docker run --network docker_default -e CERTIFICAT__CONFIG=/srv/www/config.yml -v"${WORKSPACE}/docker/certificat/srv/www/entrypoint.sh:/srv/www/entrypoint.sh" -v"${CONFIG_FILE}:/srv/www/config.yml" --entrypoint=/bin/sh -p8000:80 -it $LAST_IMAGE

#docker run -v"${CONFIG_FILE}:/srv/www/config.yml" -it -p8000:80 $LAST_IMAGE start_huey
