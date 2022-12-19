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
