import os
from pathlib import Path
import subprocess
import tempfile
import time

from requests import RequestException
import requests


def invoke_script(*args) -> subprocess.CompletedProcess[bytes]:
    script = os.path.join(
        os.path.dirname(__file__), "../../../../scripts/acme-toolkit.py"
    )

    result = subprocess.run(
        ["uv", "run", script] + list(args), check=True, capture_output=True
    )

    return result


def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")


def wait_for_pebble():
    directory = "https://localhost:14000/dir"
    timeout = 5
    start_time = time.time()
    # wait for pebble to start
    while True:
        elapsed_time = time.time() - start_time

        if elapsed_time > timeout:
            raise Exception("Timed out waiting for pebble server to start")

        try:
            requests.get(directory)
            break
        except RequestException:
            pass

        time.sleep(0.1)


def test_account_operations():
    key = "zWNDZM6eQGHWpSRTPal5eIUYFTu7EajVIoguysqZ9wG44nMEtx3MUAsUDkMTQ12W"
    kid = "kid-1"
    directory = "https://localhost:14000/dir"

    try:
        pebble = subprocess.Popen(
            [
                "/home/vscode/go/bin/pebble",
                "-config",
                "/opt/pebble/test/config/pebble-config-external-account-bindings.json",
            ],
            cwd="/opt/pebble",
        )

        wait_for_pebble()

        toolkit_proc_result = invoke_script(
            "bind-account",
            "-s",
            directory,
            "-c",
            "noreply@acme.edu",
            "-i",
            kid,
            "-k",
            key,
        )

        assert "-----BEGIN RSA PRIVATE KEY-----" in toolkit_proc_result.stdout.decode()

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(toolkit_proc_result.stdout)
            temp_file.flush()
            lookup_result = invoke_script(
                "lookup-account", "-s", directory, "-i", temp_file.name
            )
            # will be something like '46b6f93b881a7cc0\n'
            assert len(lookup_result.stdout.decode().strip()) > 5
    finally:
        pebble.terminate()
        pebble.wait()


def test_pem_to_jwk():
    toolkit_proc_result = invoke_script(
        "pem-to-jwk", "-i", os.path.join(fixtures_dir(), "key.pem")
    )
    assert (
        Path(os.path.join(fixtures_dir(), "key.jwk")).read_text()
        == toolkit_proc_result.stdout.decode()
    )


def test_jwk_to_pem():
    toolkit_proc_result = invoke_script(
        "jwk-to-pem", "-i", os.path.join(fixtures_dir(), "key.jwk")
    )

    assert (
        Path(os.path.join(fixtures_dir(), "key.pem")).read_text()
        == toolkit_proc_result.stdout.decode()
    )
