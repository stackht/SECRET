// ============================================================================
// SECRET — Neo4j Graph Schema (Phase 1)
// Smart Entity & Criminal Relationship Exploration Tool
//
// The graph is the DERIVED analytical layer, materialized from relational
// records (PostgreSQL) or synthetic source adapters.
//
// Property graph model:
//   Nodes        : Person, Organization, Phone, Vehicle, Location, Account, Event, Case
//   Relationships: OWNS, USES, CALLED, MEMBER_OF, VISITED, LOCATED_AT,
//                  TRANSFERRED_TO, ASSOCIATED_WITH, OBSERVED_AT, INVOLVED_IN
//
// All relationship edges carry: confidence, first_seen, last_seen, source_ids.
//
// NOTE: All data is SYNTHETIC / FICTIONAL.
// ============================================================================

// --- Constraints & indexes ------------------------------------------------

// Skip if constraints already exist (Neo4j supports CREATE CONSTRAINT IF NOT EXISTS on 4.4+ / 5.x)
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (n:Entity) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (n:Person) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT org_id_unique IF NOT EXISTS
FOR (n:Organization) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT phone_id_unique IF NOT EXISTS
FOR (n:Phone) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT vehicle_id_unique IF NOT EXISTS
FOR (n:Vehicle) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT location_id_unique IF NOT EXISTS
FOR (n:Location) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (n:Account) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT case_id_unique IF NOT EXISTS
FOR (n:Case) REQUIRE n.id IS UNIQUE;

// --- Node labels & properties ---------------------------------------------

// Label properties: {id, name, aliases[], risk_score, risk_level, confidence,
//                    status, source_ids[], created_at, updated_at}
// Additional type-specific properties live on each label.

// :Entity is a common super-label enabling generic traversal across all types.
// Concrete labels are used for fine-grained queries:
//   :Person      {full_name, dob?, gender?, identity_marks?}
//   :Organization{org_type, registration_no?}
//   :Phone       {number, provider?, imei?}
//   :Vehicle     {registration_no, model?, color?}
//   :Location    {latitude?, longitude?, area, city?, country?}
//   :Account     {account_number, bank_name?, account_type?}
//
// NOTE: stored latitude/longitude must be SYNTHETIC only.

// --- Relationship types & intended semantics -------------------------------

//   (Person)-[:OWNS]->(Vehicle|Phone|Account|Organization)
//   (Person)-[:USES]->(Phone|Vehicle|Account|Location)
//   (Person)-[:CALLED]->(Phone)                // direction = caller -> receiver phone
//   (Person)-[:MEMBER_OF]->(Organization)
//   (Entity)-[:VISITED]->(Location)
//   (Entity)-[:LOCATED_AT]->(Location)
//   (Account)-[:TRANSFERRED_TO]->(Account)     // financial flow, amount on edge
//   (Entity)-[:ASSOCIATED_WITH]->(Entity)      // generic/observed association
//   (Entity)-[:OBSERVED_AT]->(Event)           // appearance in an event
//   (Entity)-[:INVOLVED_IN]->(Case)
//
// Edge common properties:
//   confidence (0..1 or 0..100), first_seen, last_seen,
//   source_ids[], strength (optional), amount (for TRANSFERRED_TO, in synthetic currency)

// --- Type-based relationships: schema definition (advisory) -----------------
// Neo4j does not enforce schema on relationships by default; these are
// documented conventions to be honored by GraphService at write time.

// (Person)-[:OWNS]->(:Vehicle)
// (Person)-[:OWNS]->(:Phone)
// (Person)-[:OWNS]->(:Account)
// (Person)-[:USES]->(:Phone)
// (Person)-[:MEMBER_OF]->(:Organization)
// (Account)-[:TRANSFERRED_TO]->(:Account)
// (Person)-[:CALLED]->(:Phone)
// (:Phone)-[:USES]->(:Location)
// (:Entity)-[:VISITED]->(:Location)
// (:Entity)-[:OBSERVED_AT]->(:Event)
// (:Entity)-[:INVOLVED_IN]->(:Case)

// ============================================================================
// OPTIONAL SEED (synthetic, deterministic). Uncomment to load a small demo.
// ============================================================================
//
// MERGE (ra:Account {id: 'A-0421'}) SET ra.account_number='ACC-0421', ra.bank_name='Syndicate Bank', ra.confidence=0.9
// MERGE (rb:Account {id: 'A-0182'}) SET rb.account_number='ACC-0182', rb.bank_name='Meridian Bank', rb.confidence=0.9
// MERGE (p:Person {id: 'P-0421'}) SET p.name='Person A', p.risk_score=94, p.risk_level='CRITICAL', p.confidence=0.96
// MERGE (o:Organization {id: 'O-1101'}) SET o.name='Organization Orion', o.risk_score=89, p.risk_level='HIGH'
// MERGE (v:Vehicle {id: 'V-2048'}) SET v.registration_no='VX-2048', v.model='Sedan'
// MERGE (ph:Phone {id: 'N-4821'}) SET ph.number='+91-XXX-4821'
// MERGE (l:Location {id: 'L-3007'}) SET l.area='Sector 17', l.city='Fictional City'
//
// MERGE (p)-[:OWNS {confidence:0.95, source_ids:['S-FIR-001']}]->(v)
// MERGE (p)-[:USES {confidence:0.94, source_ids:['S-CDR-001']}]->(ph)
// MERGE (p)-[:MEMBER_OF {confidence:0.92, source_ids:['S-INT-001']}]->(o)
// MERGE (ph)-[:USES {confidence:0.86, source_ids:['S-CDR-001']}]->(l)
// MERGE (ra)-[:TRANSFERRED_TO {amount:2400000, confidence:0.97, source_ids:['S-TX-001']}]->(rb)
