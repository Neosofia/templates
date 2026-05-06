import os
import pathlib
import subprocess
import time
import uuid

import pytest
import requests


pytestmark = pytest.mark.integration

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_IMAGE = f"service-template-test:{uuid.uuid4().hex[:8]}"
_CONTAINER = f"service-template-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def live_server():
    if os.environ.get("RUN_DOCKER_TESTS") != "1":
        pytest.skip(
            "Set RUN_DOCKER_TESTS=1 to build the runtime image and run the live container check."
        )

    try:
        subprocess.run(
            [
                "docker",
                "build",
                "--target",
                "runtime",
                "-t",
                _IMAGE,
                str(_ROOT),
            ],
            check=True,
        )
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--rm",
                "--name",
                _CONTAINER,
                "-P",
                "-e",
                "ENV=test",
                _IMAGE,
            ],
            check=True,
        )

        port_mapping = subprocess.check_output(
            ["docker", "port", _CONTAINER, "8018/tcp"],
            text=True,
        ).strip()
        host_port = port_mapping.rsplit(":", 1)[-1]

        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                response = requests.get(f"http://localhost:{host_port}/health", timeout=3)
                if response.status_code == 200:
                    yield f"http://localhost:{host_port}"
                    return
            except requests.RequestException:
                pass
            time.sleep(1)

        raise RuntimeError("Timed out waiting for the container health endpoint")
    finally:
        subprocess.run(["docker", "rm", "-f", _CONTAINER], check=False)


def test_health(live_server):
    response = requests.get(f"{live_server}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
