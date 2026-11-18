#!/usr/bin/env bash
# End-to-end test for examples/evaluation/quickstart.sh.
#
# Builds the CertifiCat image from docker/certificat.Dockerfile, runs
# quickstart.sh in a temporary directory and then goes through what an
# evaluator would do:
#
#   1. CertifiCat comes up from a fresh install
#   2. The admin user can log in to the web interface
#   3. The user can create an account binding through the web interface
#   4. An ACME client (certbot) can register against that binding
#   5. A certificate can be ordered, and it chains to the generated CA
#   6. Rerunning quickstart.sh keeps the existing config and data
#   7. A broken startup is reported instead of hanging
#
# Nothing is written to examples/evaluation, and every container, network and
# volume the test creates is removed at the end (set KEEP=true to keep them for
# debugging).
#
# Requirements: docker with buildx, curl and openssl.
#
# Environment overrides:
#   TEST_IMAGE     Tag for the image built from the Dockerfile (default: certificat:quickstart-test)
#   SKIP_BUILD     Reuse an existing TEST_IMAGE instead of building it (default: false)
#   TEST_PORT      Host port for the CertifiCat under test (default: 18000)
#   TEST_NAME      Prefix for the test's containers, network and volumes (default: certificat-evaltest)
#   CERTBOT_IMAGE  Certbot image (default: certbot/certbot:latest)
#   SOCAT_IMAGE    socat image for the challenge sidecar (default: alpine/socat:latest)
#   KEEP           Keep containers and the temp directory afterwards (default: false)

set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
WORKSPACE=$(realpath "${HERE}/..")
QUICKSTART="${WORKSPACE}/examples/evaluation/quickstart.sh"

TEST_IMAGE="${TEST_IMAGE:-certificat:quickstart-test}"
SKIP_BUILD="${SKIP_BUILD:-false}"
TEST_PORT="${TEST_PORT:-18000}"
TEST_NAME="${TEST_NAME:-certificat-evaltest}"
CERTBOT_IMAGE="${CERTBOT_IMAGE:-certbot/certbot:latest}"
SOCAT_IMAGE="${SOCAT_IMAGE:-alpine/socat:latest}"
KEEP="${KEEP:-false}"

BASE_URL="http://localhost:${TEST_PORT}"
DIRECTORY_URL="${BASE_URL}/directory"
# The HTTP-01 challenge is answered by certbot inside the test network under
# this name, so the test doesn't need port 80 on the host.
DOMAIN="certbot.eval.test"
SIDECAR="${TEST_NAME}-certbot-ns"
CERTBOT_VOLUME="${TEST_NAME}-certbot"
CERTBOT_VOLUME_2="${TEST_NAME}-certbot-2"
BROKEN_NAME="${TEST_NAME}-broken"

WORK=$(mktemp -d)
COOKIES="${WORK}/cookies.txt"
CURRENT_PHASE="setup"

# ---------------------------------------------------------------------------
# Output and assertions
# ---------------------------------------------------------------------------

log() {
  echo "$(date "+%H:%M:%S") $*"
}

phase() {
  CURRENT_PHASE="$1"
  echo
  log "=== $1"
}

pass() {
  log "  ok   $1"
}

fail() {
  log "  FAIL $1" >&2
  if docker container inspect "${TEST_NAME}" &>/dev/null; then
    echo "--- last 60 lines of ${TEST_NAME} logs ---" >&2
    docker logs --tail 60 "${TEST_NAME}" >&2 2>&1 || true
    echo "---" >&2
  fi
  log "Test failed in phase: ${CURRENT_PHASE}" >&2
  exit 1
}

# expect "description" command [args...]
# The command's stdout is discarded so only the result line is printed.
expect() {
  local desc="$1"
  shift
  if "$@" >/dev/null; then
    pass "${desc}"
  else
    fail "${desc}"
  fi
}

require() {
  command -v "$1" &>/dev/null || fail "'$1' is required but was not found on PATH."
}

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

remove_resources() {
  docker rm -f "${SIDECAR}" "${TEST_NAME}" "${TEST_NAME}-redis" \
    "${BROKEN_NAME}" "${BROKEN_NAME}-redis" &>/dev/null || true
  docker volume rm "${TEST_NAME}-data" "${BROKEN_NAME}-data" \
    "${CERTBOT_VOLUME}" "${CERTBOT_VOLUME_2}" &>/dev/null || true
  docker network rm "${TEST_NAME}" "${BROKEN_NAME}" &>/dev/null || true
}

cleanup() {
  local status=$?
  if [ "${KEEP}" = true ]; then
    log "KEEP=true, leaving containers running and files in ${WORK}"
  else
    remove_resources
    rm -rf "${WORK}"
  fi
  exit "${status}"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

run_quickstart() {
  local dir="$1" name="$2" port="$3"
  CERTIFICAT_IMAGE="${TEST_IMAGE}" \
    CERTIFICAT_PULL=false \
    CERTIFICAT_PORT="${port}" \
    CERTIFICAT_EVAL_NAME="${name}" \
    "${dir}/quickstart.sh"
}

# Read a value from the generated config with the yq shipped in the image.
config_value() {
  docker run --rm --entrypoint yq \
    -v "${WORK}/run/config.yaml:/config.yaml:ro,z" \
    "${TEST_IMAGE}" -r "$1" /config.yaml
}

container_state() {
  docker container inspect -f '{{.State.Status}}/{{.RestartCount}}' "$1" 2>/dev/null
}

# grep reads the whole stream instead of using -q: with pipefail, grep -q
# exiting on the first match kills docker logs with SIGPIPE and fails the pipe.
logs_contain() {
  docker logs "${TEST_NAME}" 2>&1 | grep -E "$1" >/dev/null
}

logs_clean() {
  local errors
  errors=$(docker logs "${TEST_NAME}" 2>&1 | grep -cE "Traceback|database is locked|Permission denied|OperationalError" || true)
  [ "${errors}" -eq 0 ]
}

# Wait up to $2 seconds for a pattern to appear in the logs.
wait_for_log() {
  local pattern="$1" timeout="$2"
  for _ in $(seq 1 "${timeout}"); do
    logs_contain "${pattern}" && return 0
    sleep 1
  done
  return 1
}

cookie() {
  # Netscape cookie jar: the name is field 6 and the value field 7. HttpOnly
  # cookies get a "#HttpOnly_" prefix on the first field, which doesn't matter.
  awk -v name="$1" '$6 == name { print $7 }' "${COOKIES}" 2>/dev/null
}

http() {
  curl -sS -b "${COOKIES}" -c "${COOKIES}" "$@"
}

# Print the CSRF token from the form on the given page.
form_csrf_token() {
  http "${BASE_URL}$1" \
    | grep -o -m1 'name="csrfmiddlewaretoken" value="[^"]*"' \
    | sed -E 's/.*value="([^"]*)"/\1/'
}

# Log in with a fresh cookie jar. Prints "<status> <redirect>".
login() {
  local password="$1" token
  rm -f "${COOKIES}"
  token=$(form_csrf_token /login/)
  [ -n "${token}" ] || return 1
  http -o /dev/null -w '%{http_code} %{redirect_url}' \
    --data-urlencode "csrfmiddlewaretoken=${token}" \
    --data-urlencode "username=admin" \
    --data-urlencode "password=${password}" \
    "${BASE_URL}/login/"
}

# Fetch a page and collapse whitespace so template output is easy to match.
page() {
  http "${BASE_URL}$1" | tr -s ' \n\t' ' '
}

certbot() {
  local volume="$1"
  shift
  docker run --rm \
    --network "container:${SIDECAR}" \
    -v "${volume}:/etc/letsencrypt" \
    "${CERTBOT_IMAGE}" "$@"
}

certbot_file() {
  docker run --rm -v "${CERTBOT_VOLUME}:/etc/letsencrypt:ro" \
    --entrypoint cat "${CERTBOT_IMAGE}" "/etc/letsencrypt/live/${DOMAIN}/$1"
}

order_listed_as_valid() {
  local html
  html=$(page "/orders/?filter=${DOMAIN}")
  grep -q "${DOMAIN}" <<<"${html}" && grep -qE 'badge--success ?"> ?valid ?<' <<<"${html}"
}

# ---------------------------------------------------------------------------
# Phase 0: build the image from the current Dockerfile
# ---------------------------------------------------------------------------

require docker
require curl
require openssl

remove_resources

phase "Build ${TEST_IMAGE} from docker/certificat.Dockerfile"
if [ "${SKIP_BUILD}" = true ]; then
  expect "SKIP_BUILD set, reusing existing ${TEST_IMAGE}" docker image inspect "${TEST_IMAGE}"
else
  docker buildx build \
    --build-context "src=${WORKSPACE}/src/" \
    --build-context "dockerfiles=${WORKSPACE}/docker/certificat" \
    -f "${WORKSPACE}/docker/certificat.Dockerfile" \
    --network host \
    --load \
    --tag "${TEST_IMAGE}" \
    "${WORKSPACE}" || fail "docker build failed"
  pass "built ${TEST_IMAGE}"
fi

docker pull -q "${CERTBOT_IMAGE}" >/dev/null || fail "could not pull ${CERTBOT_IMAGE}"
docker pull -q "${SOCAT_IMAGE}" >/dev/null || fail "could not pull ${SOCAT_IMAGE}"

# ---------------------------------------------------------------------------
# Phase 1: fresh install
# ---------------------------------------------------------------------------

phase "1. CertifiCat comes up from a fresh install"

mkdir -p "${WORK}/run"
cp "${QUICKSTART}" "${WORK}/run/"

if run_quickstart "${WORK}/run" "${TEST_NAME}" "${TEST_PORT}" >"${WORK}/quickstart-1.log" 2>&1; then
  pass "quickstart.sh exited 0"
else
  cat "${WORK}/quickstart-1.log" >&2
  fail "quickstart.sh exited non-zero"
fi
expect "quickstart.sh generated a new config" grep -q "No config.yaml found" "${WORK}/quickstart-1.log"

CONFIG="${WORK}/run/config.yaml"
expect "config.yaml exists" test -f "${CONFIG}"
expect "config.yaml is mode 644" test "$(stat -c %a "${CONFIG}")" = 644
expect "database is sqlite" test "$(config_value .certificat.db.type)" = sqlite

# Checked through indirect expansion below.
# shellcheck disable=SC2034
SECRET_KEY=$(config_value .certificat.secret_key)
# shellcheck disable=SC2034
REDIS_PASSWORD=$(config_value .certificat.redis.password)
ADMIN_PASSWORD=$(config_value .certificat.authentication.admin.password)
for value in SECRET_KEY REDIS_PASSWORD ADMIN_PASSWORD; do
  expect "${value} is set" test -n "${!value}" -a "${!value}" != null
done
expect "admin password is printed for the user" grep -q "admin / ${ADMIN_PASSWORD}" "${WORK}/quickstart-1.log"

config_value .certificat.finalizer.cert >"${WORK}/ca.crt"
config_value .certificat.finalizer.key >"${WORK}/ca.key"
CA_TEXT=$(openssl x509 -in "${WORK}/ca.crt" -noout -text)
expect "CA certificate has CA:TRUE" grep -q "CA:TRUE" <<<"${CA_TEXT}"
expect "CA certificate can sign certificates" grep -q "Certificate Sign" <<<"${CA_TEXT}"
expect "CA key matches the CA certificate" test \
  "$(openssl x509 -in "${WORK}/ca.crt" -noout -pubkey)" = "$(openssl pkey -in "${WORK}/ca.key" -pubout)"

expect "CertifiCat container is running without restarts" test "$(container_state "${TEST_NAME}")" = running/0
expect "Redis container is running without restarts" test "$(container_state "${TEST_NAME}-redis")" = running/0

DIRECTORY=$(curl -fsS "${DIRECTORY_URL}") || fail "GET /directory failed"
pass "GET /directory returned 200"
expect "directory lists newAccount" grep -q '"newAccount"' <<<"${DIRECTORY}"
expect "directory requires external account binding" grep -qE '"externalAccountRequired": *true' <<<"${DIRECTORY}"

expect "huey consumer started" wait_for_log "Huey consumer started" 30
expect "default finalizer was registered" logs_contain "Registered new settings for finalizer default"
expect "no errors in the logs" logs_clean

# Migrations run as root, so a root-owned database, -wal or -shm file left
# behind would stop the web interface and task runner from writing.
expect "every file in the data directory is owned by certificat" test \
  -z "$(docker exec "${TEST_NAME}" find /var/lib/certificat ! -user certificat)"
expect "task stats share the main database" grep -q \
  "^sqlite:////var/lib/certificat/certificat.sqlite3" <<<"$(config_value .certificat.task_queue.stats_database)"
expect "database is in WAL mode" test "$(docker exec -u certificat "${TEST_NAME}" \
  /srv/www/.venv/bin/python -c "import sqlite3; print(sqlite3.connect('/var/lib/certificat/certificat.sqlite3').execute('PRAGMA journal_mode').fetchone()[0])")" = wal

# ---------------------------------------------------------------------------
# Phase 2: authentication
# ---------------------------------------------------------------------------

phase "2. The user can authenticate"

rm -f "${COOKIES}"
RESULT=$(http -o /dev/null -w '%{http_code} %{redirect_url}' "${BASE_URL}/accounts/")
expect "anonymous /accounts/ redirects to the login page" \
  grep -qE '^302 .*/login/\?next=/accounts/$' <<<"${RESULT}"

TOKEN=$(form_csrf_token /login/)
expect "login page has a CSRF token" test -n "${TOKEN}"
expect "login page sets a CSRF cookie" test -n "$(cookie csrftoken)"

RESULT=$(login "not-the-password")
expect "wrong password is rejected" grep -q '^200' <<<"${RESULT}"
expect "wrong password doesn't create a session" test -z "$(cookie sessionid)"

RESULT=$(login "${ADMIN_PASSWORD}")
expect "correct password logs in (302)" grep -q '^302' <<<"${RESULT}"
expect "login creates a session" test -n "$(cookie sessionid)"

RESULT=$(http -o /dev/null -w '%{http_code}' "${BASE_URL}/accounts/")
expect "logged-in /accounts/ returns 200" test "${RESULT}" = 200

# ---------------------------------------------------------------------------
# Phase 3: create an account binding through the web interface
# ---------------------------------------------------------------------------

phase "3. The user can create an account"

TOKEN=$(form_csrf_token /accounts/)
expect "accounts page has a form" test -n "${TOKEN}"

RESULT=$(http -o /dev/null -w '%{http_code} %{redirect_url}' \
  --data-urlencode "csrfmiddlewaretoken=${TOKEN}" \
  --data-urlencode "scope=1" \
  --data-urlencode "name=evaltest" \
  --data-urlencode "note=Created by run-blackbox-tests.sh" \
  "${BASE_URL}/accounts/")
expect "creating a binding redirects to the account page" \
  grep -qE '^302 .*/account/[0-9]+/$' <<<"${RESULT}"
ACCOUNT_PATH=$(sed -E 's#^302 https?://[^/]+##' <<<"${RESULT}")

mapfile -t EAB < <(http "${BASE_URL}${ACCOUNT_PATH}" \
  | grep -o '<dd class="monospaced">[^<]*</dd>' \
  | sed -E 's#<dd class="monospaced">([^<]*)</dd>#\1#')
EAB_KID="${EAB[0]:-}"
EAB_HMAC="${EAB[1]:-}"
expect "account page shows a 40 character HMAC ID" test "${#EAB_KID}" -eq 40
# hmac_key_length (90) counts random bytes, which are shown base64url encoded.
expect "account page shows a 90 byte HMAC key (120 base64url characters)" \
  grep -qE '^[A-Za-z0-9_-]{120}$' <<<"${EAB_HMAC}"

# ---------------------------------------------------------------------------
# Phase 4: bind an ACME client
# ---------------------------------------------------------------------------

phase "4. An ACME client can bind to the account"

# The sidecar shares its network namespace with certbot. It forwards
# localhost:${TEST_PORT} to CertifiCat so certbot can use url_root, and its
# network alias lets CertifiCat reach certbot's standalone challenge server.
docker run -d --name "${SIDECAR}" \
  --network "${TEST_NAME}" --network-alias "${DOMAIN}" \
  "${SOCAT_IMAGE}" \
  "TCP-LISTEN:${TEST_PORT},fork,reuseaddr" "TCP:${TEST_NAME}:80" >/dev/null \
  || fail "could not start the challenge sidecar"
sleep 1

if certbot "${CERTBOT_VOLUME}" register --non-interactive --agree-tos \
  -m test@example.com --server "${DIRECTORY_URL}" \
  --eab-kid "${EAB_KID}" --eab-hmac-key "${EAB_HMAC}" >"${WORK}/certbot-register.log" 2>&1 \
  && grep -q "Account registered" "${WORK}/certbot-register.log"; then
  pass "certbot registered with the account binding"
else
  cat "${WORK}/certbot-register.log" >&2
  fail "certbot registered with the account binding"
fi

if certbot "${CERTBOT_VOLUME_2}" register --non-interactive --agree-tos \
  -m test@example.com --server "${DIRECTORY_URL}" \
  --eab-kid "${EAB_KID}" --eab-hmac-key "${EAB_HMAC}" >"${WORK}/certbot-rebind.log" 2>&1; then
  fail "a second ACME account can't reuse the same binding"
fi
expect "a second ACME account can't reuse the same binding" \
  grep -q "Attempting to rebind external account" "${WORK}/certbot-rebind.log"

ACCOUNT_PAGE=$(page "${ACCOUNT_PATH}")
expect "account page shows the bound account" grep -q 'id="binding-name"' <<<"${ACCOUNT_PAGE}"
# shellcheck disable=SC2016
expect "account page no longer shows the HMAC key" bash -c '! grep -qF -- "$1" <<<"$2"' _ "${EAB_HMAC}" "${ACCOUNT_PAGE}"

# ---------------------------------------------------------------------------
# Phase 5: order a certificate
# ---------------------------------------------------------------------------

phase "5. A certificate can be ordered"

if certbot "${CERTBOT_VOLUME}" certonly --standalone --non-interactive \
  --server "${DIRECTORY_URL}" -d "${DOMAIN}" >"${WORK}/certbot-certonly.log" 2>&1; then
  pass "certbot certonly succeeded"
else
  cat "${WORK}/certbot-certonly.log" >&2
  fail "certbot certonly succeeded"
fi

certbot_file cert.pem >"${WORK}/cert.pem" || fail "could not read the issued certificate"
expect "certificate is issued by the generated CA" \
  grep -q "CertifiCat Evaluation CA" <<<"$(openssl x509 -in "${WORK}/cert.pem" -noout -issuer)"
expect "certificate SAN is ${DOMAIN}" \
  grep -q "DNS:${DOMAIN}" <<<"$(openssl x509 -in "${WORK}/cert.pem" -noout -ext subjectAltName)"
expect "certificate verifies against the CA in config.yaml" \
  openssl verify -CAfile "${WORK}/ca.crt" "${WORK}/cert.pem"

expect "order is listed as valid in the web interface" order_listed_as_valid
expect "certificate is listed in the web interface" grep -q "${DOMAIN}" <<<"$(page /certificates/)"
expect "no errors in the logs" logs_clean

# ---------------------------------------------------------------------------
# Phase 6: rerun with the existing config
# ---------------------------------------------------------------------------

phase "6. Rerunning quickstart.sh keeps the existing setup"

CONFIG_SUM=$(sha256sum "${CONFIG}")
if run_quickstart "${WORK}/run" "${TEST_NAME}" "${TEST_PORT}" >"${WORK}/quickstart-2.log" 2>&1; then
  pass "quickstart.sh exited 0"
else
  cat "${WORK}/quickstart-2.log" >&2
  fail "quickstart.sh exited non-zero"
fi
expect "quickstart.sh skipped setup" grep -q "skipping setup" "${WORK}/quickstart-2.log"
expect "config.yaml is unchanged" test "$(sha256sum "${CONFIG}")" = "${CONFIG_SUM}"
expect "CertifiCat container is running without restarts" test "$(container_state "${TEST_NAME}")" = running/0
expect "admin user was kept" wait_for_log "Local admin user updated" 30
expect "finalizer thumbprint is unchanged" logs_contain "Finalizer default \([0-9a-f]+\) is unchanged"

RESULT=$(login "${ADMIN_PASSWORD}")
expect "login still works with the same password" grep -q '^302' <<<"${RESULT}"
expect "earlier order survived the restart" order_listed_as_valid

if certbot "${CERTBOT_VOLUME}" renew --force-renewal --no-random-sleep-on-renew --non-interactive >"${WORK}/certbot-renew.log" 2>&1; then
  pass "certbot renew works with the existing ACME account"
else
  cat "${WORK}/certbot-renew.log" >&2
  fail "certbot renew works with the existing ACME account"
fi
expect "no errors in the logs" logs_clean

# ---------------------------------------------------------------------------
# Phase 7: a broken startup is reported
# ---------------------------------------------------------------------------

phase "7. A broken startup is reported"

# A config that loads far enough for quickstart.sh but fails validation inside
# the container, because the database, authentication and finalizer are missing.
mkdir -p "${WORK}/broken"
cp "${QUICKSTART}" "${WORK}/broken/"
cat >"${WORK}/broken/config.yaml" <<EOF
certificat:
  secret_key: "broken"
  url_root: "http://localhost:$((TEST_PORT + 1))"
  redis:
    host: "${BROKEN_NAME}-redis"
    password: "broken"
EOF
chmod 644 "${WORK}/broken/config.yaml"

START=${SECONDS}
if timeout 180 bash -c "$(declare -f run_quickstart); TEST_IMAGE='${TEST_IMAGE}' run_quickstart '${WORK}/broken' '${BROKEN_NAME}' '$((TEST_PORT + 1))'" \
  >"${WORK}/quickstart-broken.log" 2>&1; then
  fail "quickstart.sh exits non-zero when CertifiCat can't start"
fi
pass "quickstart.sh exits non-zero when CertifiCat can't start"
expect "quickstart.sh says CertifiCat exited" grep -q "CertifiCat exited during startup" "${WORK}/quickstart-broken.log"
expect "failure was reported within 60 seconds" test $((SECONDS - START)) -lt 60

echo
log "All quickstart tests passed."
