"""Registration, listing, and title normalization for Task Board API v1."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_empty_list_returns_only_items(client: TestClient) -> None:
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"items": []}


def test_create_returns_201_with_the_created_task(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "첫 작업"})

    assert response.status_code == 201
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"id": 1, "title": "첫 작업", "status": "open"}


def test_create_trims_the_contract_whitespace_characters(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": " \t\n\r첫 작업\r\n\t "})

    assert response.status_code == 201
    assert response.json()["title"] == "첫 작업"
    assert client.get("/api/tasks").json() == {
        "items": [{"id": 1, "title": "첫 작업", "status": "open"}]
    }


def test_created_task_appears_in_the_list(client: TestClient) -> None:
    created = client.post("/api/tasks", json={"title": "첫 작업"}).json()

    listed = client.get("/api/tasks")

    assert listed.status_code == 200
    assert listed.json() == {"items": [created]}


def test_list_is_ordered_by_ascending_id(client: TestClient) -> None:
    titles = ["첫 작업", "둘째 작업", "셋째 작업"]
    created_ids = [client.post("/api/tasks", json={"title": t}).json()["id"] for t in titles]

    items = client.get("/api/tasks").json()["items"]

    assert created_ids == sorted(created_ids)
    assert [item["id"] for item in items] == created_ids
    assert [item["title"] for item in items] == titles


def test_ids_are_positive_and_stable_across_reads(client: TestClient) -> None:
    client.post("/api/tasks", json={"title": "첫 작업"})
    client.post("/api/tasks", json={"title": "둘째 작업"})

    first = client.get("/api/tasks").json()["items"]
    second = client.get("/api/tasks").json()["items"]

    assert all(item["id"] > 0 for item in first)
    assert first == second


def test_title_of_exactly_100_code_points_is_accepted(client: TestClient) -> None:
    title = "가" * 100

    response = client.post("/api/tasks", json={"title": title})

    assert response.status_code == 201
    assert response.json()["title"] == title


def test_inner_whitespace_is_preserved(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "  첫   작업  "})

    assert response.status_code == 201
    assert response.json()["title"] == "첫   작업"


def test_tasks_survive_a_backend_restart(db_file: Path) -> None:
    """A second app lifecycle over the same file still sees the stored task (AC-002)."""
    with TestClient(app) as first_run:
        created = first_run.post("/api/tasks", json={"title": "첫 작업"}).json()

    assert db_file.exists()

    with TestClient(app) as second_run:
        assert second_run.get("/api/tasks").json() == {"items": [created]}
