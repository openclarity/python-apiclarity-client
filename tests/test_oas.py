# flake8: noqa
# type: ignore

from pathlib import Path
from typing import Dict

import pytest
import ujson

from apiclarity.openapispec import *

SCHEMA_PATH = Path("./tests/test_schemas")


def test_min_document():
    fname_test_schema = "01_minimal_schema.json"
    with open(SCHEMA_PATH / fname_test_schema) as hnd:
        test_schema = ujson.load(hnd)
    model: OpenAPI3 = build_openapi_model(test_schema)

    assert isinstance(model, OpenAPI3)
    assert model.openapi == "3.1.0"
    assert isinstance(model.info, Info)
    assert model.info.title == "Minimal example"
    assert model.info.version == "1.0.0"
    assert isinstance(model.paths, Dict)
    assert len(model.paths) == 0


def test_paths():
    fname_test_schema = "02_paths.json"
    with open(SCHEMA_PATH / fname_test_schema) as hnd:
        test_schema = ujson.load(hnd)
    model: OpenAPI3 = build_openapi_model(test_schema)

    assert len(model.paths) == 2
    assert model.paths["/users"] is not None

    expected_verbs_users = ["get"]
    verbs_users = [v for v, _ in model.paths["/users"].operations()]
    assert expected_verbs_users == verbs_users

    expected_verbs_pets = ["post"]
    verbs_pets = [v for v, _ in model.paths["/pets"].operations()]
    assert expected_verbs_pets == verbs_pets

    assert "A long summary" == model.paths["/users"].summary
    assert "A short description" == model.paths["/users"].description


def test_operation():
    fname_test_schema = "03_operation.json"
    with open(SCHEMA_PATH / fname_test_schema) as hnd:
        test_schema = ujson.load(hnd)
    model: OpenAPI3 = build_openapi_model(test_schema)

    op: OASOperation3 = model.paths["/users"].get

    assert ["one", "two"] == op.tags
    assert "Get summary" == op.summary
    assert "Another description" == op.description
    assert "http://www.example.com" == op.externalDocs.url
    assert "id01" == op.operationId
    assert 1 == len(op.parameters)
    assert "param1" == op.parameters[0].name
    assert "header" == op.parameters[0].oas_in
    assert ["application/json"] == list(op.requestBody.content.keys())
    assert (
        "#/components/schemas/Pet"
        == op.requestBody.content["application/json"].oas_schema.ref
    )
    assert ["200"] == list(op.responses.keys())
    assert "This is required" == op.responses["200"].description
    assert ["application/xml"] == list(op.responses["200"].content.keys())
    assert (
        "#/components/schemas/PetResp"
        == op.responses["200"].content["application/xml"].oas_schema.ref
    )
    assert ["OnData"] == list(op.callbacks.keys())
    assert ["somePattern"] == list(op.callbacks["OnData"])
    assert "#/components/schemas/PetResp2" == op.callbacks["OnData"]["somePattern"].ref
    assert ["api_key"] == list(op.security.keys())
    assert "server1.com" == op.servers.url


def test_server():
    fname_test_schema = "04_server.json"
    with open(SCHEMA_PATH / fname_test_schema) as hnd:
        test_schema = ujson.load(hnd)
    model: OpenAPI3 = build_openapi_model(test_schema)

    servers = model.servers
    assert 3 == len(servers)
    # server 1
    assert "https://development.gigantic-server.com/v1" == servers[0].url
    assert "Development server" == servers[0].description
    # server 3
    assert "https://api.gigantic-server.com/v1" == servers[2].url
    assert "Production server" == servers[2].description
    # variables
    s3_vars = servers[2].variables
    assert ["username", "port", "basePath"] == list(s3_vars.keys())
    assert "demo" == s3_vars["username"].default
    assert (
        "this value is assigned by the service provider, in this example `gigantic-server.com`"
        == s3_vars["username"].description
    )
    assert ["8443", "443"] == s3_vars["port"].oas_enum


def test_tag_external_doc():
    fname_test_schema = "05_tag_and_ext_doc.json"
    with open(SCHEMA_PATH / fname_test_schema) as hnd:
        test_schema = ujson.load(hnd)
    model: OpenAPI3 = build_openapi_model(test_schema)

    assert 2 == len(model.tags)
    assert "pet" == model.tags[0].name
    assert "Pets operations" == model.tags[0].description
    assert "https://example.com" == model.tags[1].externalDocs.url
    assert "Find more info here" == model.tags[1].externalDocs.description


def test_response():
    fname_test_schema = "06_multiple_responses.json"
    with open(SCHEMA_PATH / fname_test_schema) as hnd:
        test_schema = ujson.load(hnd)
    model: OpenAPI3 = build_openapi_model(test_schema)

    op_resp = model.paths["/users"].get.responses

    assert ["200", "404"] == list(op_resp.keys())
    assert "Not found" == op_resp["404"].description

    assert ["application/json"] == list(op_resp["200"].content.keys())

    assert ["one_link"] == list(op_resp["200"].links)
    link = op_resp["200"].links["one_link"]

    assert "#/components/operations/1" == link.operationRef
    assert "op_id_1" == link.operationId
    assert "val1" == link.parameters["param1"]
    assert "val2" == link.requestBody
    assert "Desc3" == link.description
    assert isinstance(link.server, OASServer)
    assert "cisco.com" == link.server.url

    media_type = op_resp["200"].content["application/json"]
    assert "v1" == media_type.oas_schema["discriminator"]["mapping"]["k1"]
    assert "prop1" == media_type.oas_schema["discriminator"]["propertyName"]

    assert "v11" == media_type.example["k1"]
    assert "value1" == media_type.examples["dog"].value

    assert "ct1" == media_type.encoding["key1"].contentType
    assert True == media_type.encoding["key1"].explode
    assert True == media_type.encoding["key1"].allowReserved
