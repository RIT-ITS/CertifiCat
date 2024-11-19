#!/usr/bin/env bash
set -euo pipefail

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LOGLEVEL='DEBUG'

CONFIG="${CERTIFICAT__CONFIG:-${HERE}/config.yml}"
PYTHON="/srv/www/.venv/bin/python"

usage() {
	cat << EOF
Usage: COMMAND [OPTIONS] 

Commands:
  manage
  migrate
  start_server
  start_huey
  shell
EOF
}

[ -z "${1:-}" ] && {
    usage
    exit 1
}

# Logging functions
function log_output {
  echo `date "+%Y/%m/%d %H:%M:%S"`" $1"
}

function log_debug {
  if [[ "$LOGLEVEL" =~ ^(DEBUG)$ ]]; then
    log_output "DEBUG $1"
  fi
}

function log_info {
  if [[ "$LOGLEVEL" =~ ^(DEBUG|INFO)$ ]]; then
    log_output "INFO $1"
  fi
}

function log_warn {
  if [[ "$LOGLEVEL" =~ ^(DEBUG|INFO|WARN)$ ]]; then
    log_output "WARN $1"
  fi
}

function log_err {
  if [[ "$LOGLEVEL" =~ ^(DEBUG|INFO|WARN|ERROR)$ ]]; then
    log_output "ERROR $1"
  fi
}

migrate() {
  "${PYTHON}" /srv/www/manage.py migrate  
}

manage() {
  "${PYTHON}" /srv/www/manage.py "$@"
}

runserver() {
    [ -f "${CONFIG}" ] || {
        log_err "File ${CONFIG} not found and is required."
        exit 1;
    }
        
    supervisord -c /etc/supervisor/supervisord.web.conf
}

collectstatic() {
    [ -f "${CONFIG}" ] || {
        log_err "File ${CONFIG} not found and is required."
        exit 1;
    }

    CERTIFICAT__STATICFILES_ROOT="/srv/www/static" "${PYTHON}" /srv/www/manage.py collectstatic --noinput
}

runhuey() {
  [ -f "${CONFIG}" ] || {
        log_err "File ${CONFIG} not found and is required."
        exit 1;
    }
        
    "${PYTHON}" /srv/www/manage.py run_huey -w4
}

SUB_COMMAND=${1}; shift
case "$SUB_COMMAND" in
    manage)
      while getopts ":" flag; do
        case "${flag}" in            
            *) 
              usage
              exit 1
              ;;
        esac        
      done 
      
      manage "$@"
      ;;

    migrate)
      while getopts ":" flag; do
        case "${flag}" in            
            *) 
              usage
              exit 1
              ;;
        esac        
      done 
      
      migrate
      ;;

    start_server)
      while getopts ":" flag; do
        case "${flag}" in
            *) 
              usage
              exit 1
              ;;
        esac
      done 
      
      log_info "Running Django migrate command"
      migrate

      log_info "Collecting static files to /srv/www/static"
      collectstatic

      runserver
      ;;

    start_huey)
      while getopts ":" flag; do
        case "${flag}" in
            *) 
              usage
              exit 1
              ;;
        esac
      done 
      
      runhuey
      ;;

    shell)
      exec /bin/bash
      ;;

    *) usage
    
esac