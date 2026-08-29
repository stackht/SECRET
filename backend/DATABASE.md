# SECRET — Database Design (PostgreSQL)

**Phase 1 deliverable** — corresponding DDL lives in [`sql/schema.sql`](sql/schema.sql).

## Overview

PostgreSQL is the **normative, relational source of truth**. It stores users,
criminal profiles, cases, evidence, FIRs, alerts, and the audit trail. The
analytical **graph** (Neo4j) is a derived projection of this data, not the
source of truth.

All values are **synthetic / fictional**.

## ERD (logical)

```
users ─┬─< case_members >─ cases
       └─< case_criminals >─ criminal_profiles
criminal_profiles >─< fir_profiles >─ firs
cases ─< firs
cases ─< evidence
cases ─< alerts
criminal_profiles ─< alerts
users ─< audit_logs
```

## Tables

### `users`
Authentication + authorization.
- `id`, `username` (unique), `email` (unique)
- `password_hash` (never store plain text)
- `role` enum: `admin|analyst|investigator|viewer`
- `status` enum: `active|disabled`
- timestamps + `last_login_at`

### `criminal_profiles`
The core **entity** table. A row is a person / organization / phone / vehicle /
location / account, distinguished by `profile_type` (enum `entity_type`).
- `secret_id` — stable public identifier, e.g. `P-0421`, `O-1101`, `V-2048`.
- `aliases` (JSONB array of strings)
- `risk_score` (0..100), `risk_level` enum, `confidence` (0..100)
- `attributes` (JSONB) — type-specific free-form fields (e.g. phone number,
  vehicle reg, coordinates) kept flexible to avoid rigid columns.

### `cases`
An investigation (`CASE-2026-0817`).
- `status` enum `OPEN|IN_PROGRESS|CLOSED|ARCHIVED`
- `priority` enum `LOW|MEDIUM|HIGH|CRITICAL`
- associations: `case_criminals` (entities in case), `case_members` (investigators)

### `firs`
Synthetic First Information Reports.
- `fir_number` (unique), optional `case_id` link
- `description`, `police_station`, `registered_at`, `status` enum
- `raw_json` stores the original synthetic payload (for provenance/replay)
- `fir_profiles` links people/entities named in the FIR

### `evidence`
Captured evidence linked to a case and optionally a profile.
- `evidence_type` enum, `storage_ref`, `chain_of_custody` (JSONB)

### `alerts`
Analytical indicators generated from AI/analytics modules.
- `severity`, `status` (`NEW|REVIEWING|RESOLVED|DISMISSED`)
- `score`, `confidence`, `source_ids` (JSONB provenance)
- **Important:** alerts describe *indicators/anomalies*, never declare guilt.

### `audit_logs`
Append-only record of meaningful actions.
- `action` (e.g. `case.created`, `alert.reviewed`), `object_id`, `object_type`, `result` (JSONB)

## Enums (summary)

| Category | Values |
|---|---|
| `user_role` | admin, analyst, investigator, viewer |
| `entity_type` | PERSON, ORGANIZATION, PHONE, VEHICLE, LOCATION, ACCOUNT |
| `risk_level` | LOW, MEDIUM, HIGH, CRITICAL |
| `case_status` | OPEN, IN_PROGRESS, CLOSED, ARCHIVED |
| `case_priority` | LOW, MEDIUM, HIGH, CRITICAL |
| `evidence_type` | DOCUMENT, PHOTO, VIDEO, AUDIO, RECORD, OTHER |
| `alert_severity` | LOW, MEDIUM, HIGH, CRITICAL |
| `alert_status` | NEW, REVIEWING, RESOLVED, DISMISSED |
| `fir_status` | REGISTERED, UNDER_INVESTIGATION, CHARGE_SHEET, CLOSED |

## Conventions

- `id` — `BIGSERIAL` surrogate PK.
- `secret_id` — stable business identifier with a type prefix.
- `*_at` — `TIMESTAMPTZ`.
- JSONB columns — flexible/type-specific data + provenance payloads.
- `updated_at` — auto-maintained via `set_updated_at()` trigger.
- Foreign keys use `ON DELETE` policies appropriate to each relationship.

## How to run (local dev)

See [`docker-compose.yml`](docker-compose.yml) for Postgres + Neo4j.

```bash
docker compose up -d postgres neo4j
# apply schema
psql "$DATABASE_URL" -f sql/schema.sql
```

> Full migrations use Alembic in Phase 2; `schema.sql` is the authoritative DDL for Phase 1.
