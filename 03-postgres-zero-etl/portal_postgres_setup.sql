-- =============================================================================
-- EPOWER Module 2: "Mein EPOWER" Portal — Postgres Setup
-- =============================================================================
-- Run this file against your Snowflake Postgres instance:
--
--   psql service=my_epower_portal -f portal_postgres_setup.sql
--
-- Or with a full connection string:
--
--   psql "host=<HOST> port=5432 dbname=postgres user=snowflake_admin sslmode=require" \
--        -f portal_postgres_setup.sql
--
-- This creates:
--   1. Portal schema (5 tables + indexes)
--   2. pg_lake + pg_incremental extensions
--   3. Iceberg mirror table for portal_activity_log
--
-- After running this script AND portal_seed_data.sql, run portal_iceberg_sync.sql
-- to bulk-copy data and start the incremental sync pipeline.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Section 1: Portal Schema
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS portal_users (
    customer_key       INT PRIMARY KEY,
    email              TEXT NOT NULL UNIQUE,
    display_name       TEXT NOT NULL,
    registered_at      TIMESTAMPTZ DEFAULT now(),
    last_login_at      TIMESTAMPTZ,
    login_count        INT DEFAULT 0,
    preferred_language TEXT DEFAULT 'de',
    notifications_enabled BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS meter_readings (
    reading_id         BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL REFERENCES portal_users(customer_key),
    reading_date       DATE NOT NULL,
    meter_type         TEXT NOT NULL,
    reading_kwh        INT NOT NULL,
    submitted_at       TIMESTAMPTZ DEFAULT now(),
    source             TEXT DEFAULT 'PORTAL',
    CONSTRAINT valid_meter_type CHECK (meter_type IN ('ELECTRICITY', 'GAS'))
);

CREATE TABLE IF NOT EXISTS tariff_orders (
    order_id           BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL REFERENCES portal_users(customer_key),
    order_type         TEXT NOT NULL,
    current_product    TEXT,
    requested_product  TEXT NOT NULL,
    status             TEXT DEFAULT 'PENDING',
    created_at         TIMESTAMPTZ DEFAULT now(),
    confirmed_at       TIMESTAMPTZ,
    effective_date     DATE,
    CONSTRAINT valid_status CHECK (status IN ('PENDING', 'CONFIRMED', 'ACTIVE', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS service_requests (
    request_id         BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL REFERENCES portal_users(customer_key),
    request_type       TEXT NOT NULL,
    subject            TEXT NOT NULL,
    description        TEXT,
    status             TEXT DEFAULT 'OPEN',
    priority           TEXT DEFAULT 'NORMAL',
    created_at         TIMESTAMPTZ DEFAULT now(),
    resolved_at        TIMESTAMPTZ,
    CONSTRAINT valid_request_type CHECK (request_type IN ('SUPPORT', 'COMPLAINT', 'VPP_ENROLLMENT', 'VPP_OPTOUT', 'BILLING_INQUIRY', 'MOVE'))
);

CREATE TABLE IF NOT EXISTS portal_activity_log (
    activity_id        BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL,
    event_time         TIMESTAMPTZ DEFAULT now(),
    event_type         TEXT NOT NULL,
    event_detail       JSONB DEFAULT '{}',
    city               TEXT,
    region             TEXT,
    customer_type      TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_email ON portal_users(email);
CREATE INDEX IF NOT EXISTS idx_readings_customer ON meter_readings(customer_key, reading_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON tariff_orders(status) WHERE status = 'PENDING';
CREATE INDEX IF NOT EXISTS idx_requests_open ON service_requests(status) WHERE status = 'OPEN';
CREATE INDEX IF NOT EXISTS idx_activity_time ON portal_activity_log(event_time);

-- ---------------------------------------------------------------------------
-- Section 2: pg_lake + pg_incremental Extensions
-- ---------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS pg_lake CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_incremental;

-- ---------------------------------------------------------------------------
-- Section 3: Iceberg Mirror Table
-- ---------------------------------------------------------------------------
-- This table stores portal_activity_log data in Apache Iceberg format.
-- pg_lake manages the Iceberg metadata and Parquet data files on object storage.

CREATE TABLE IF NOT EXISTS portal_activity_log_iceberg (
    activity_id        BIGINT,
    customer_key       INT,
    event_time         TIMESTAMPTZ,
    event_type         TEXT,
    event_detail       JSONB,
    city               TEXT,
    region             TEXT,
    customer_type      TEXT
) USING iceberg;


