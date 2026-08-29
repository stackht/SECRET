-- ============================================================================
-- SECRET — PostgreSQL Schema (Phase 1)
-- Smart Entity & Criminal Relationship Exploration Tool
--
-- Relationship database: normative source-of-truth records.
-- Graph (Neo4j) is derived from these records.
--
-- NOTE: All data is SYNTHETIC / FICTIONAL.
-- ============================================================================

-- Extensions ----------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;          -- gen_random_uuid

-- ENUM types ----------------------------------------------------------------
CREATE TYPE user_role   AS ENUM ('admin', 'analyst', 'investigator', 'viewer');
CREATE TYPE user_status AS ENUM ('active', 'disabled');

CREATE TYPE entity_type AS ENUM (
    'PERSON', 'ORGANIZATION', 'PHONE', 'VEHICLE', 'LOCATION', 'ACCOUNT'
);

CREATE TYPE risk_level AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

CREATE TYPE case_status   AS ENUM ('OPEN', 'IN_PROGRESS', 'CLOSED', 'ARCHIVED');
CREATE TYPE case_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

CREATE TYPE evidence_type AS ENUM (
    'DOCUMENT', 'PHOTO', 'VIDEO', 'AUDIO', 'RECORD', 'OTHER'
);

CREATE TYPE alert_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE alert_status   AS ENUM ('NEW', 'REVIEWING', 'RESOLVED', 'DISMISSED');

CREATE TYPE fir_status AS ENUM ('REGISTERED', 'UNDER_INVESTIGATION', 'CHARGE_SHEET', 'CLOSED');

-- ============================================================================
-- USERS (authentication & authorization)
-- ============================================================================
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(64)  NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   TEXT         NOT NULL,
    full_name       VARCHAR(160),
    role            user_role    NOT NULL DEFAULT 'viewer',
    status          user_status  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    last_login_at   TIMESTAMPTZ
);

-- ============================================================================
-- CRIMINAL PROFILES (entities in the domain)
-- Each row may represent a person, org, phone, vehicle, location or account.
-- ============================================================================
CREATE TABLE criminal_profiles (
    id               BIGSERIAL PRIMARY KEY,
    secret_id        VARCHAR(32)  NOT NULL UNIQUE,   -- e.g. 'P-0421', 'O-1101'
    profile_type     entity_type  NOT NULL,
    name             VARCHAR(255) NOT NULL,
    aliases          JSONB        NOT NULL DEFAULT '[]'::jsonb,    -- string[]
    risk_score       NUMERIC(5,2) NOT NULL DEFAULT 0,               -- 0..100
    risk_level       risk_level   NOT NULL DEFAULT 'LOW',
    confidence       NUMERIC(5,2) NOT NULL DEFAULT 0,               -- 0..100
    status           VARCHAR(32)  NOT NULL DEFAULT 'MONITORED',     -- e.g. MONITORED, ARCHIVED
    attributes       JSONB        NOT NULL DEFAULT '{}'::jsonb,     -- free-form type-specific fields
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    last_activity_at TIMESTAMPTZ
);

CREATE INDEX idx_criminal_profiles_type ON criminal_profiles (profile_type);
CREATE INDEX idx_criminal_profiles_risk ON criminal_profiles (risk_score DESC);
CREATE INDEX idx_criminal_profiles_name ON criminal_profiles (name);

-- ============================================================================
-- CASES (investigations)
-- ============================================================================
CREATE TABLE cases (
    id            BIGSERIAL PRIMARY KEY,
    case_number   VARCHAR(64)   NOT NULL UNIQUE,      -- e.g. 'CASE-2026-0817'
    title         VARCHAR(255)  NOT NULL,
    description   TEXT,
    status        case_status   NOT NULL DEFAULT 'OPEN',
    priority      case_priority NOT NULL DEFAULT 'MEDIUM',
    created_by_id BIGINT        REFERENCES users(id) ON DELETE SET NULL,
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ   NOT NULL DEFAULT now(),
    closed_at     TIMESTAMPTZ
);

CREATE INDEX idx_cases_status ON cases (status);
CREATE INDEX idx_cases_priority ON cases (priority);

-- Case ↔ Criminal profile (many-to-many: which entities belong to a case)
CREATE TABLE case_criminals (
    case_id      BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    profile_id   BIGINT NOT NULL REFERENCES criminal_profiles(id) ON DELETE CASCADE,
    role_in_case VARCHAR(64),                          -- 'PRIMARY', 'RELATED', 'WITNESS'
    added_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (case_id, profile_id)
);

-- Investigators assigned to a case
CREATE TABLE case_members (
    case_id      BIGINT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    user_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (case_id, user_id)
);

-- ============================================================================
-- FIRs (First Information Reports — synthetic)
-- ============================================================================
CREATE TABLE firs (
    id          BIGSERIAL PRIMARY KEY,
    fir_number  VARCHAR(64) NOT NULL UNIQUE,
    case_id     BIGINT REFERENCES cases(id) ON DELETE SET NULL,
    police_station VARCHAR(160),
    description TEXT,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status      fir_status NOT NULL DEFAULT 'REGISTERED',
    source_ref  VARCHAR(128),                          -- provenance linkage
    raw_json    JSONB NOT NULL DEFAULT '{}'::jsonb,    -- original synthetic payload
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_firs_case ON firs (case_id);
CREATE INDEX idx_firs_registered ON firs (registered_at DESC);

-- FIR ↔ criminal profile (people/entities named in the FIR)
CREATE TABLE fir_profiles (
    fir_id     BIGINT NOT NULL REFERENCES firs(id) ON DELETE CASCADE,
    profile_id BIGINT NOT NULL REFERENCES criminal_profiles(id) ON DELETE CASCADE,
    PRIMARY KEY (fir_id, profile_id)
);

-- ============================================================================
-- EVIDENCE
-- ============================================================================
CREATE TABLE evidence (
    id             BIGSERIAL PRIMARY KEY,
    case_id        BIGINT REFERENCES cases(id) ON DELETE CASCADE,
    profile_id     BIGINT REFERENCES criminal_profiles(id) ON DELETE SET NULL,
    evidence_type  evidence_type NOT NULL,
    title          VARCHAR(255) NOT NULL,
    description    TEXT,
    storage_ref    VARCHAR(255),                       -- path/uri (mock)
    chain_of_custody JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_by_id  BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_evidence_case ON evidence (case_id);
CREATE INDEX idx_evidence_profile ON evidence (profile_id);

-- ============================================================================
-- ALERTS (analytical indicators — never a guilt declaration)
-- ============================================================================
CREATE TABLE alerts (
    id           BIGSERIAL PRIMARY KEY,
    case_id      BIGINT REFERENCES cases(id) ON DELETE CASCADE,
    profile_id   BIGINT REFERENCES criminal_profiles(id) ON DELETE SET NULL,
    severity     alert_severity NOT NULL,
    status       alert_status   NOT NULL DEFAULT 'NEW',
    title        VARCHAR(255) NOT NULL,
    description  TEXT,
    score        NUMERIC(5,2) NOT NULL DEFAULT 0,      -- anomaly/priority indicator
    confidence   NUMERIC(5,2) NOT NULL DEFAULT 0,
    source_ids   JSONB NOT NULL DEFAULT '[]'::jsonb,   -- provenance
    reviewed_by  BIGINT REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alerts_severity ON alerts (severity);
CREATE INDEX idx_alerts_status ON alerts (status);
CREATE INDEX idx_alerts_case ON alerts (case_id);

-- ============================================================================
-- AUDIT LOG
-- ============================================================================
CREATE TABLE audit_logs (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action     VARCHAR(128) NOT NULL,                  -- e.g. 'case.created', 'alert.reviewed'
    object_id  VARCHAR(64),
    object_type VARCHAR(64),
    result     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_logs_user ON audit_logs (user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs (created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs (action);

-- utility trigger for updated_at ----------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_criminal_profiles_updated BEFORE UPDATE ON criminal_profiles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_cases_updated BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
