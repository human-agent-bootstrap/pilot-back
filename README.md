# pilot-back

Task Board API v1 — the FastAPI + SQLite backend for the `collaboration-workflow` pilot.
The shared truth for this API is the approved contract snapshot in the root repository:
`changes/CHG-TASK-001/contracts/tasks-api.md`. Do not change behaviour here without a
re-approved contract.

## API

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/api/tasks` | `200 {"items":[Task]}`, ascending `id` | `500 INTERNAL_ERROR` |
| POST | `/api/tasks` | `201 Task` | `422 INVALID_REQUEST`, `500 INTERNAL_ERROR` |

`Task` is `{"id": 1, "title": "첫 작업", "status": "open"}`. A `title` is trimmed of leading
and trailing space, tab, LF, and CR, then must be 1–100 Unicode code points. CORS allows the
frontend origin `http://127.0.0.1:5173` only, without credentials.

## Requirements

- Python 3.12 (provisioned by uv)
- [uv](https://docs.astral.sh/uv/) — `pyproject.toml` and `uv.lock` are the dependency truth

## Run

```bash
uv sync --locked --python 3.12
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Tasks are stored in SQLite at `TASK_DB_PATH` (default `./data/tasks.sqlite3`); the directory
is created on first use and the file survives a restart. OpenAPI is at `/openapi.json`.

## Verify

```bash
uv sync --locked --python 3.12
uv run --locked pytest
uv run --locked ruff check .
```
