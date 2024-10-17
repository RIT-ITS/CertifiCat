SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c


ARGS=""

ROOT="$(shell realpath ../)"
SRC_PATH="${ROOT}/src"
LIB_PATH="${SRC_PATH}/certificat"
TESTS_PATH="${LIB_PATH}/tests"
VENV_PATH="${ROOT}/.venv"
VENV_PYTHON="${VENV_PATH}/bin/python3"
ACTIVATE_VENV="${ROOT}/.venv/bin/activate"

.PHONY: dist
dist: setup-venv
	@cd "${SRC_PATH}"
	uv build -o "${ROOT}/dist"

.PHONY: setup-venv
setup-venv:
	@[ ! -d "${VENV_PATH}" ] && { uv venv "${VENV_PATH}"; }
	cd "${SRC_PATH}"
	uv sync 
	echo "${SRC_PATH}" > "$$(realpath "${VENV_PATH}"/lib/python*)/site-packages/local.pth"
