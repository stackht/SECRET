# SECRET — Backend

Backend for the **Strategic Entity & Criminal Relationship Exploration Tool**.
This folder contains the FastAPI/Python backend that powers the (frozen) React UI.

> **Phase 1** status: architecture + database/graph schema + scaffolding only.
> No business logic yet. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Contents

| Path | Purpose |
|---|---|
| `ARCHITECTURE.md` | Requirement analysis, stack, layers, folder layout, API map |
| `DATABASE.md` | PostgreSQL design guide |
| `GRAPH-SCHEMA.md` | Neo4j graph design guide |
| `sql/schema.sql` | PostgreSQL DDL (authoritative for Phase 1) |
| `cypher/schema.cypher` | Neo4j constraints + node/relationship schema |
| `docker-compose.yml` | Local Postgres + Neo4j |
| `requirements.txt` | Python dependencies (Phase 2 hardening) |
| `app/` | FastAPI application scaffold (folders + empty modules) |
| `.env.example` | Environment variable template |

## Local databases

```bash
docker compose up -d postgres neo4j
```

- PostgreSQL: `localhost:5432`, db/user/pass `secret`/`secret`/`secret`
- Neo4j: `localhost:7474` (browser) / `bolt://localhost:7687`, user `neo4j`, pass `secret`

Apply the relational schema:

```bash
psql "postgresql://secret:secret@localhost:5432/secret" -f sql/schema.sql
```

## Python environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API (dev)

```bash
uvicorn app.main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
# Health:   http://localhost:8000/health
```

## Health / connectivity

- `GET /health` — service up
- `GET /api/v1/health/db` — PostgreSQL reachable (503 if down)
- `GET /api/v1/health/graph` — Neo4j reachable (503 if down)

## Tests

```bash
pytest                        # unit tests (integration auto-skipped if DBs down)
pytest -m integration         # requires PostgreSQL + Neo4j running
```

## Migrations (Alembic, async)

```bash
# Generate offline SQL without a DB (validates migration)
alembic upgrade head --sql

# Apply to a live database
alembic upgrade head
```

## Phase roadmap

| Phase | Scope |
|---|---|
| 1 ✅ | Architecture, folder layout, DB + graph schema, scaffolding |
| 2 ✅ | FastAPI bootstrap, JWT + connection wiring, health checks, tests, Alembic |
| 3 | Authentication APIs |
| 4 | Criminal APIs |
| 5 | Case APIs |
| 6 | Relationship / Graph APIs |
| 7 | Network visualization integration |
| 8 | AI modules (community, kingpin, centrality, link prediction, risk) |
| 9 | Report generation |
| 10 | Deployment |
| 4 | Criminal APIs |
| 5 | Case APIs |
| 6 | Relationship / Graph APIs |
| 7 | Network visualization integration |
| 8 | AI modules (community, kingpin, centrality, link prediction, risk) |
| 9 | Report generation |
| 10 | Deployment |
