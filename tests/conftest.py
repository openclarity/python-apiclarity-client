# Copyright © 2022 Cisco Systems, Inc. and its affiliates.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import pytest
from pytest_docker_tools import container, fetch, wrappers


@pytest.fixture(scope="session")
def apiclarity_version() -> str:
    return os.getenv("APICLARITY_VERSION", default="latest")


apiclarity_image = fetch(
    repository="ghcr.io/openclarity/apiclarity:{apiclarity_version}"
)


apiclarity_server: wrappers.Container = container(
    image="{apiclarity_image.id}",
    name="apiclarity_server",
    scope="module",
    command=["run"],
    ports={
        "9000/tcp": None,
        "8080/tcp": None,
    },
    environment={
        "DATABASE_DRIVER": "LOCAL",  # for storage
        "NO_K8S_MONITOR": "true",  # local deployment
        "DEPLOYMENT_TYPE": "fake",  # for fuzzer config
        "FAKE_DATA": "false",  # init db with fake data
        "FAKE_TRACES": "false",  # init db with fake traces
        "ENABLE_K8S": "false",  # do not use k8s
        "HTTP_TRACES_PORT": "9000",  # for publishing traces
        "BACKEND_REST_PORT": "8080",  # inventory API port
        "HEALTH_CHECK_ADDRESS": ":8081",  # go health checks
        "TRACE_SAMPLING_ENABLED": "false",  # do not use trace-sampling-manager
    },
    volumes={
        os.getcwd() + "/tests/provided_spec": {"bind": "/provided_spec", "mode": "ro"},
    },
)


@pytest.fixture(scope="module")
def apiclarity_port_telemetry(apiclarity_server: wrappers.Container) -> int:
    return int(
        apiclarity_server.attrs["NetworkSettings"]["Ports"]["9000/tcp"][0]["HostPort"]
    )


@pytest.fixture(scope="module")
def apiclarity_port_inventory(apiclarity_server: wrappers.Container) -> int:
    return int(
        apiclarity_server.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"]
    )
