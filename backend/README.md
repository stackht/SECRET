# SECRET — Backend

Backend for the **Strategic Entity & Criminal Relationship Exploration Tool**.
This folder contains the FastAPI/Python backend that powers the (frozen) React UI.

> **Status.** All roadmap phases implemented and tested (126 tests). Backend serves
> every UI surface of the frozen React frontend (see [ARCHITECTURE.md](ARCHITECTURE.md)).
> The full demo loop is real: create case → upload files (CSV/JSON/TXT, XLSX when
> openpyxl present) → parse + quality + duplicate checks → process (persist entities
> + relationships with provenance) → materialize graph → analytics → alerts → report.

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

Apply the relational schema (migrations are authoritative):

```bash
python -m alembic upgrade head
# Alternative (no migration history): psql "postgresql://secret:secret@localhost:5432/secret" -f sql/schema.sql
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

| Phase | Scope | Status |
|---|---|---|
| 1 | Architecture, folder layout, DB + graph schema, scaffolding | ✅ |
| 2 | FastAPI bootstrap, JWT + connections, health checks, Alembic | ✅ |
| 3 | Authentication APIs (+ source registry) | ✅ |
| 4 | Criminal / entity APIs | ✅ |
| 5 | Case APIs (incl. archive, sources, investigation export) | ✅ |
| 6 | Relationship / graph APIs (materialize, network, analytics) | ✅ |
| 7 | Network visualization integration (frontend freeze) | ✅ |
| 8 | AI modules (community, kingpin, centrality, link prediction, risk) | ✅ |
| 9 | Report generation (PDF + investigation export) | ✅ |
| 10 | Deployment (Docker compose, migration-owned schema, desktop packaging) | ✅ |
| 11 | Real file ingestion: upload → parse (CSV/JSON/TXT/XLSX) → quality metrics → hash dedup | ✅ |
| 12 | Entity/relationship persistence w/ provenance + case read-back + analytics (comms/tx/timeline/locations) | ✅ |
| 13 | Indicator alerts (bursts / high-value transfers), dashboard summary, global search | ✅ |
