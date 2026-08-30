# SECRET — Deployment

**Phase 10** — running the full stack and packaging the desktop app.

All data is synthetic / fictional.

---

## 1. Architecture for deployment

```
┌──────────────────────────────────────────────┐
│  SECRET.exe (Electron desktop)               │
│   - frozen React UI                         │
│   - calls http://localhost:8000/api/v1/*    │
│   - falls back to synthetic mode if offline │
└──────────────┬───────────────────────────────┘
               │ REST (JSON)
┌──────────────▼───────────────────────────────┐
│  SECRET API (FastAPI :8000)                  │
│   - auth · criminals · cases · graph ·       │
│     analytics · reports                      │
└──────┬──────────────────┬────────────────────┘
       │                  │
       ▼                  ▼
┌─────────────┐   ┌─────────────┐
│ PostgreSQL  │   │   Neo4j     │
└─────────────┘   └─────────────┘
```

---

## 2. Full-stack with Docker Compose

`docker-compose.yml` starts PostgreSQL, Neo4j, and the API.

```bash
docker compose up -d postgres neo4j
docker compose build api
docker compose up -d api
```

- `api` waits for Postgres + Neo4j health checks, then starts the app.
- Alembic migrations own the schema: the `api` container runs
  `python run.py --port 8000`, which applies `alembic upgrade head` (baseline +
  `0002_add_case_sources`) before serving.

Check services:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health/db     # 200 if Postgres reachable
curl http://localhost:8000/api/v1/health/graph  # 200 if Neo4j reachable
```

API docs: `http://localhost:8000/docs`

---

## 3. Local (non-Docker) deployment

1. Start databases (Docker): `docker compose up -d postgres neo4j`
2. Install deps: `python -m venv .venv && .\venv\Scripts\activate && pip install -r requirements.txt`
3. Configure env: copy `.env.example` → `.env` (set `JWT_SECRET`).
4. Migrate: `python -m alembic upgrade head`
5. Run API: `python run.py`  (or `.\run.bat`, `.\run.bat --check`)

> Pre-seeded DBs (schema created from `sql/schema.sql`, no `alembic_version`
> row): run `python -m alembic stamp head` once instead of `upgrade head`, so
> migrations resume from the current state instead of re-creating objects.

---

## 4. Demo lifecycle

1. Start the API (`python run.py`).
2. `POST /api/v1/auth/login` with `admin` / `admin-secret` to get a token.
3. Optionally `POST /api/v1/criminals`, `POST /api/v1/cases`, link profiles.
4. `POST /api/v1/graph/materialize` to build the graph from relational records.
5. Query graph + analytics:
   - `GET /api/v1/graph/network`
   - `GET /api/v1/graph/analytics/key-entities`
   - `GET /api/v1/graph/analytics/communities`
   - `GET /api/v1/graph/analytics/risk`
   - `GET /api/v1/graph/analytics/link-prediction`
6. `POST /api/v1/reports/generate` to produce a PDF preview report.

---

## 5. Packaging the desktop app (SECRET.exe)

The Electron desktop app is packaged from the project root (the React UI is the
frozen SECRET frontend).

```bash
# 1. Build the renderer bundle
npm run build:web            # -> dist/

# 2. (Optional) full Electron build incl. electron-builder
npm run build                # -> release-fresh/SECRET 0.1.0.exe (portable)
```

`electron-builder` config lives in `package.json` (`build` section):

```jsonc
{
  "appId": "com.secret.intelligence",
  "productName": "SECRET",
  "win": { "target": ["portable"], "executableName": "SECRET" },
  "directories": { "output": "release-fresh" }
}
```

Result: `release-fresh/SECRET.exe` (portable, no installer required).

### Running the packaged app

- The packaged renderer is served from `dist/index.html`.
- The UI attempts to reach the backend at `http://localhost:8000` (`VITE_API_URL`).
- If the backend is not running (or CORS blocks `file://`), the UI transparently
  falls back to **synthetic mode** so the demo still works.

```bash
# Run the API first so the packaged app connects to live data
cd backend && .\run.bat
# Then launch
.\release-fresh\SECRET.exe
```

> For a full live demo: keep the API + Postgres + Neo4j running, set
> `VITE_API_URL` to your backend origin in a `.env` at the project root, rebuild
> the renderer, and repackage.

---

## 6. Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async URL | `postgresql+asyncpg://...:5432/secret` |
| `NEO4J_URI/...` | Neo4j connection | `bolt://localhost:7687` |
| `JWT_SECRET` | JWT signing secret (set in prod!) | `change-me` |
| `SECRET_ENV` | `dev`/`demo`/`production` | `dev` |
| `CORS_ORIGINS` | Allowed frontend origins | `["http://localhost:5173"]` |
| `VITE_API_URL` (frontend) | Backend origin | `http://localhost:8000` |

---

## 7. Useful commands

```bash
# Backend tests (integration auto-skip when Docker/DBs are down)
cd backend && python -m pytest

# Backend connectivity check
cd backend && python run.py --check

# Regenerate offline migration SQL (no DB needed)
cd backend && python -m alembic upgrade head --sql

# Full export (JSON) of an investigation
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/cases/CASE-2026-0001
```
