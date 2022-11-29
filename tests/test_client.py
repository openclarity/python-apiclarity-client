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

from typing import List

import pytest
import ujson
from pytest_docker_tools import wrappers

from apiclarity.client import ClientSession, ClientSettings
from apiclarity.schemas import ApiInventory, ApiType, TelemetryTrace


@pytest.fixture
def apiclarity_session(
    monkeypatch: pytest.MonkeyPatch,
    apiclarity_port_telemetry: int,
    apiclarity_port_inventory: int,
) -> ClientSession:
    monkeypatch.setenv(
        "APICLARITY_ENDPOINT",
        "http://localhost:" + str(apiclarity_port_inventory),
    )
    monkeypatch.setenv(
        "TELEMETRY_ENDPOINT",
        "http://localhost:" + str(apiclarity_port_telemetry),
    )
    base_settings = ClientSettings()
    return ClientSession(base_settings)


@pytest.fixture
def petstore_traces() -> List[TelemetryTrace]:
    with open("tests/traces/petstore.json", "r") as fp:
        return [TelemetryTrace.parse_obj(o) for o in ujson.load(fp)]


@pytest.fixture
def petstore_provided_spec() -> str:
    with open("tests/provided_spec/provided_spec.json", "r") as apiSpec:
        return apiSpec.read()


@pytest.fixture
def pestore_api_id() -> str:
    return str(1)


def test_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APICLARITY_ENDPOINT", "http://localhost")
    base_settings = ClientSettings()
    assert str(base_settings.apiclarity_endpoint) == "http://localhost"


def test_server(apiclarity_server: wrappers.Container) -> None:
    assert apiclarity_server.status == "running"


def print_api_inventory(apiInfo: ApiInventory) -> None:
    if apiInfo.items:
        print(f"received {len(apiInfo.items)} apis of {apiInfo.total} apis\n")
        for api in apiInfo.items:
            print(f"received: {api}\n")
    else:
        print(f"received 0 apis of {apiInfo.total} apis\n")


def test_get_inventory(
    apiclarity_session: ClientSession,
    petstore_traces: List[TelemetryTrace],
    pestore_api_id: str,
) -> None:
    # We have to first post a trace before we can create an api entry
    apiclarity_session.postTelemetry(petstore_traces[0])

    apiInfo = apiclarity_session.getInventory()  # default EXTERNAL
    assert (not apiInfo.items or len(apiInfo.items) == 0) and apiInfo.total == 0
    print_api_inventory(apiInfo)
    apiInfo = apiclarity_session.getInventory(apiType=ApiType.INTERNAL)
    print_api_inventory(apiInfo)
    assert apiInfo.items and len(apiInfo.items) > 0 and apiInfo.total > 0
    apiData = apiInfo.items[0]
    assert str(apiData.id) == pestore_api_id
    apiInfo = apiclarity_session.getInventory(apiType=ApiType.EXTERNAL)
    print_api_inventory(apiInfo)
    assert (not apiInfo.items or len(apiInfo.items) == 0) and apiInfo.total == 0


def test_provided_spec(
    apiclarity_session: ClientSession,
    petstore_provided_spec: str,
    pestore_api_id: str,
) -> None:
    # Test provided spec as string
    apiclarity_session.putProvidedSpec(pestore_api_id, petstore_provided_spec)
    apiInfo = apiclarity_session.getInventory(apiType=ApiType.INTERNAL)
    print_api_inventory(apiInfo)
    assert apiInfo.items and len(apiInfo.items) > 0
    apiData = apiInfo.items[0]
    assert apiData.hasProvidedSpec and str(apiData.id) == pestore_api_id

    # Test provided spec as object
    petstoreProvidedSpec = ujson.loads(petstore_provided_spec)
    apiclarity_session.putProvidedSpec(pestore_api_id, petstoreProvidedSpec)
    apiInfo = apiclarity_session.getInventory(apiType=ApiType.INTERNAL)
    print_api_inventory(apiInfo)
    assert apiInfo.items and len(apiInfo.items) > 0
    apiData = apiInfo.items[0]
    assert apiData.hasProvidedSpec and str(apiData.id) == pestore_api_id


def test_get_provided_spec(
    apiclarity_session: ClientSession,
    petstore_provided_spec: str,
    pestore_api_id: str,
) -> None:
    petstoreProvidedSpec = ujson.loads(petstore_provided_spec)
    apiSpec = apiclarity_session.getProvidedSpec(pestore_api_id)
    assert apiSpec is not None
    print("received apispec:\n" + ujson.dumps(apiSpec) + "\n")
    assert apiSpec["info"]["title"] == petstoreProvidedSpec["info"]["title"]
