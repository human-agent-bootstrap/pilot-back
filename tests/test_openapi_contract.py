"""The generated OpenAPI document must describe the contract, and runtime must match it.

The contract is Markdown, so this does not compare documents byte for byte. It checks that
every documented path, method, status, and schema says what the contract says.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def openapi(client: TestClient) -> dict[str, Any]:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()


def resolve(document: dict[str, Any], node: Any) -> Any:
    """Follow a local $ref into components so a schema can be inspected inline."""
    while isinstance(node, dict) and "$ref" in node:
        target: Any = document
        for part in node["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        node = target
    return node


def json_schema(document: dict[str, Any], container: dict[str, Any]) -> dict[str, Any]:
    return resolve(document, container["content"]["application/json"]["schema"])


def test_only_the_contract_path_is_documented(openapi: dict[str, Any]) -> None:
    assert set(openapi["paths"]) == {"/api/tasks"}
    assert set(openapi["paths"]["/api/tasks"]) == {"get", "post"}


def test_get_takes_no_parameters_and_no_body(openapi: dict[str, Any]) -> None:
    operation = openapi["paths"]["/api/tasks"]["get"]

    assert operation.get("parameters", []) == []
    assert "requestBody" not in operation


def test_get_documents_200_with_items_only(openapi: dict[str, Any]) -> None:
    responses = openapi["paths"]["/api/tasks"]["get"]["responses"]
    assert set(responses) == {"200", "500"}

    schema = json_schema(openapi, responses["200"])
    assert set(schema["properties"]) == {"items"}
    assert schema["required"] == ["items"]
    assert schema["properties"]["items"]["type"] == "array"

    task = resolve(openapi, schema["properties"]["items"]["items"])
    assert set(task["properties"]) == {"id", "title", "status"}


def test_post_documents_a_title_only_request_body(openapi: dict[str, Any]) -> None:
    operation = openapi["paths"]["/api/tasks"]["post"]

    assert operation.get("parameters", []) == []
    schema = json_schema(openapi, operation["requestBody"])
    assert set(schema["properties"]) == {"title"}
    assert schema["required"] == ["title"]
    assert schema["properties"]["title"]["type"] == "string"
    assert schema["additionalProperties"] is False


def test_post_documents_201_422_and_500(openapi: dict[str, Any]) -> None:
    responses = openapi["paths"]["/api/tasks"]["post"]["responses"]
    assert set(responses) == {"201", "422", "500"}

    task = json_schema(openapi, responses["201"])
    assert set(task["properties"]) == {"id", "title", "status"}
    assert sorted(task["required"]) == ["id", "status", "title"]
    assert task["properties"]["id"]["type"] == "integer"
    assert task["properties"]["title"]["type"] == "string"
    assert task["properties"]["status"]["const"] == "open"


@pytest.mark.parametrize(("method", "code"), [("get", "500"), ("post", "422"), ("post", "500")])
def test_error_responses_document_the_error_envelope(
    openapi: dict[str, Any], method: str, code: str
) -> None:
    schema = json_schema(openapi, openapi["paths"]["/api/tasks"][method]["responses"][code])

    assert set(schema["properties"]) == {"error"}
    assert schema["required"] == ["error"]
    detail = resolve(openapi, schema["properties"]["error"])
    assert set(detail["properties"]) == {"code", "message"}
    assert sorted(detail["required"]) == ["code", "message"]


def test_runtime_responses_match_the_documented_property_names(
    client: TestClient, openapi: dict[str, Any]
) -> None:
    paths = openapi["paths"]["/api/tasks"]

    def documented_properties(method: str, code: str) -> set[str]:
        return set(json_schema(openapi, paths[method]["responses"][code])["properties"])

    created = client.post("/api/tasks", json={"title": "첫 작업"})
    assert created.status_code == 201
    assert set(created.json()) == documented_properties("post", "201")

    listed = client.get("/api/tasks")
    assert listed.status_code == 200
    assert set(listed.json()) == documented_properties("get", "200")

    rejected = client.post("/api/tasks", json={"title": " "})
    assert rejected.status_code == 422
    assert set(rejected.json()) == documented_properties("post", "422")
