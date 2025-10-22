````markdown
# memo-notes-api

A minimal **FastAPI CRUD API** for notes, designed for clarity and maintainability.
It demonstrates good REST practices, versioned endpoints, and developer tooling with:

- **Poetry** – dependency & environment management
- **FastAPI** – high-performance web framework
- **Uvicorn** – ASGI server
- **Taskipy** – developer task runner
- **Pytest** – testing & coverage
- **Ruff** – linting & auto-formatting
- **Docker Compose** – for easy containerized execution

---

## Quickstart

```bash
# clone your repo or copy project
cd ~/repos/python/memo-notes-api

# install dependencies
poetry install

# run development server (with auto-reload)
poetry run task dev
````

Once running, visit:

  * Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
  * ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
  * Health check: [http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz) *(if enabled)*

-----

## API overview

Base URL: `http://127.0.0.1:8000/v1`

| Method | Endpoint | Description |
| ---------: | :------------ | :-------------------------------------------- |
| **POST** | `/notes` | Create a new note |
| **GET** | `/notes` | List notes (search, filter, pagination) |
| **GET** | `/notes/{id}` | Retrieve a note by ID (supports ETag caching) |
| **PUT** | `/notes/{id}` | Update a note |
| **DELETE** | `/notes/{id}` | Delete a note |

### Data model

```json
{
  "id": 1,
  "title": "Meeting notes",
  "content": "Discussed project milestones.",
  "tags": ["work", "planning"],
  "created_at": "2025-10-22T14:00:00Z",
  "updated_at": "2025-10-22T14:00:00Z"
}
```

### Pagination envelope

`GET /v1/notes` returns:

```json
{
  "items": [],
  "total": 0,
  "limit": 100,
  "offset": 0
}
```

-----

## Testing the API (via cURL or Insomnia)

You can interact with the API manually using **curl** or a GUI tool such as **Insomnia** or **Postman**.

### Using cURL

```bash
# Create a new note
curl -X POST http://127.0.0.1:8000/v1/notes \
      -H "Content-Type: application/json" \
      -d '{"title": "First Note", "content": "Hello World", "tags": ["demo"]}'

# List all notes
curl http://127.0.0.1:8000/v1/notes | jq

# Retrieve a specific note
curl http://127.0.0.1:8000/v1/notes/1 | jq

# Update a note
curl -X PUT http://127.0.0.1:8000/v1/notes/1 \
      -H "Content-Type: application/json" \
      -d '{"title": "Updated", "content": "Updated content", "tags": ["edited"]}'

# Delete a note
curl -X DELETE http://127.0.0.1:8000/v1/notes/1 -v
```

### Using Insomnia

1.  Open **Insomnia** and create a new workspace.

2.  Set an environment variable:

    ```json
    { "base_url": "http://127.0.0.1:8000/v1" }
    ```

3.  Create the following requests:

      * `POST {{ base_url }}/notes`
      * `GET {{ base_url }}/notes`
      * `GET {{ base_url }}/notes/1`
      * `PUT {{ base_url }}/notes/1`
      * `DELETE {{ base_url }}/notes/1`

4.  Run each request and check the responses.

You can also import a ready-made JSON Insomnia collection (available in `/insomnia_collection.json`).

-----

## Running automated tests

The project uses **pytest** for testing, with task aliases defined in `pyproject.toml`.

### Run all tests

```bash
poetry run task test
```

### Run tests with coverage report

```bash
poetry run task cov
```

### Run a specific test

```bash
poetry run pytest -k test_create_and_get_note -v
```

### Show test output (logs)

```bash
poetry run pytest -s
```

Expected output:

```
==================== test session starts ====================
collected 3 items

tests/test_notes.py ...                                  [100%]
===================== 3 passed in 0.5s =====================
```

-----

## Linting & formatting

Check code style:

```bash
poetry run task lint
```

Auto-fix imports & formatting:

```bash
poetry run task fmt
```

-----

## Taskipy commands

| Task | Description |
| ---------------------- | -------------------------------- |
| `poetry run task list` | Show available tasks |
| `poetry run task dev` | Run FastAPI server (reload mode) |
| `poetry run task lint` | Run Ruff lint checks |
| `poetry run task fmt` | Format code with Ruff |
| `poetry run task test` | Run all tests |
| `poetry run task cov` | Run tests with coverage report |

-----

## Project structure

```
memo-notes-api/
├─ pyproject.toml               # Poetry + Ruff + Taskipy configuration
├─ docker-compose.yml           # Multi-service Docker config
├─ Dockerfile                   # Container build recipe
├─ .dockerignore                # Files to exclude from Docker build
├─ README.md
├─ src/
│  └─ app/
│      ├─ main.py               # FastAPI app setup (versioned routes)
│      ├─ __init__.py
│      └─ routers/
│          └─ notes.py          # CRUD logic (in-memory)
└─ tests/
   └─ test_notes.py             # Pytest suite for API endpoints
```

-----

## Developer notes

  * The API stores data **in memory**; it resets every time the server restarts.
  * Versioned routes (`/v1/notes`) prepare the codebase for future backward-compatible releases.
  * ETags are included in note retrievals to support **client-side caching**.
  * Pagination envelope (`items`, `total`, `limit`, `offset`) is returned for list endpoints.
  * The Docker setup supports both **production** and **live-reload development** modes.

-----

## Run with Docker

This project includes a preconfigured **Docker and Docker Compose** setup.

### Build & run (production-like)

```bash
docker compose up --build api
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Run in dev mode with live reload

```bash
docker compose --profile dev up --build api-dev
```

The `src/` folder is mounted, so code changes trigger hot reload.

### Stop & clean up

```bash
docker compose down
```

-----

*Developed using FastAPI and Poetry.*

```
```
