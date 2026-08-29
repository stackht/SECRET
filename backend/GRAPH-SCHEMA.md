# SECRET — Graph Schema (Neo4j)

**Phase 1 deliverable** — corresponding Cypher lives in [`cypher/schema.cypher`](cypher/schema.cypher).

## Role of the graph

Neo4j is the **derived analytical layer** used for graph traversal, community
detection, centrality, link prediction, and risk scoring. It is materialized
from relational records (PostgreSQL) / synthetic source adapters — it is not the
source of truth for relational attributes.

## Node labels

| Label | Purpose | Key properties |
|---|---|---|
| `Entity` | Common super-label enabling generic traversal | `id`, `name`, `confidence`, `source_ids`, `created_at`, `updated_at` |
| `Person` | Individual subject | `full_name`, `aliases[]`, `risk_score`, `risk_level`, `dob?`, `gender?` |
| `Organization` | Group / gang / company | `org_type`, `registration_no?` |
| `Phone` | Phone identifier | `number`, `provider?`, `imei?` |
| `Vehicle` | Vehicle | `registration_no`, `model?`, `color?` |
| `Location` | Place (synthetic coords only) | `latitude?`, `longitude?`, `area`, `city?` |
| `Account` | Bank / financial account | `account_number`, `bank_name?`, `account_type?` |
| `Event` | A temporal occurrence | `event_type`, `timestamp`, `description` |
| `Case` | Investigation container | `case_number`, `status`, `priority` |

Every concrete node also carries the `:Entity` label for uniform lookup.

> All coordinates and identifiers are **SYNTHETIC**. Never store real sensitive data.

## Relationship types (directed edges)

| Relationship | Direction | Meaning | Notable edge props |
|---|---|---|---|
| `OWNS` | Person → Vehicle/Phone/Account/Org | Ownership | `confidence`, `source_ids` |
| `USES` | Entity → Phone/Vehicle/Account/Location | Usage | `confidence`, `source_ids` |
| `CALLED` | Person → Phone | Caller placed call to number | `confidence`, `source_ids` |
| `MEMBER_OF` | Person → Organization | Membership | `confidence`, `source_ids` |
| `VISITED` | Entity → Location | Visited a place | `confidence`, `source_ids` |
| `LOCATED_AT` | Entity → Location | Is located at | `confidence`, `source_ids` |
| `TRANSFERRED_TO` | Account → Account | Financial flow | `amount` (synthetic), `confidence`, `source_ids` |
| `ASSOCIATED_WITH` | Entity → Entity | Generic observed association | `strength?`, `confidence`, `source_ids` |
| `OBSERVED_AT` | Entity → Event | Appearance in event | `confidence`, `source_ids` |
| `INVOLVED_IN` | Entity → Case | Participation in case | `role` |

### Common edge properties

- `confidence` — model/extraction confidence (0..1 or 0..100)
- `first_seen`, `last_seen` — temporal bounds
- `source_ids[]` — provenance records that support the edge
- `strength` (optional) — weighted edge for analytics
- `amount` (only on `TRANSFERRED_TO`)

## Provenance-first design

Every node and edge is expected to carry `source_ids` and `confidence` so the UI
can implement a **VIEW SOURCE** interaction — showing the original synthetic
record that produced the analytical result.

## Example subgraph (synthetic)

```
Person P-0421
  └─ OWNS ── Vehicle V-2048
  ├─ USES ── Phone N-4821
  ├─ MEMBER_OF ── Organization O-1101
  └─ ASSOCIATED_WITH ── Person P-0182
Account A-0421
  └─ TRANSFERRED_TO (amount 2,400,000) ── Account A-0182
Phone N-4821
  └─ USES ── Location L-3007 (Sector 17)
```

## Constraints

- Unique constraint on `id` for every labeled `Entity` subtype and `Case`.

## Traversal patterns needed by analytics (later phases)

- **K-hop neighborhood** of a target entity (expanding search).
- **Community detection** on person/organization subgraph (gang detection).
- **Betweenness / degree centrality** for key connectors / kingpin scoring.
- **Shortest path** + **bridge detection** between communities.
- **Link prediction features** from co-occurrence in events/cases.
