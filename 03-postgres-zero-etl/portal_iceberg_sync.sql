-- =============================================================================
-- EPOWER Module 2: Portal Iceberg Sync Setup
-- =============================================================================
-- Run this AFTER portal_postgres_setup.sql and portal_seed_data.sql:
--
--   psql service=my_epower_portal -f portal_iceberg_sync.sql
--
-- This script:
--   1. Bulk-copies existing portal_activity_log data into the Iceberg table
--   2. Creates a pg_incremental pipeline for ongoing 1-minute sync
--   3. Verifies row counts match
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Section 1: Initial Backfill (bulk copy historical data to Iceberg)
-- ---------------------------------------------------------------------------

INSERT INTO portal_activity_log_iceberg
SELECT activity_id, customer_key, event_time, event_type,
       event_detail, city, region, customer_type
FROM portal_activity_log;

-- ---------------------------------------------------------------------------
-- Section 2: Create Incremental Pipeline (for new data going forward)
-- ---------------------------------------------------------------------------
-- pg_incremental automatically substitutes $1 and $2 with the time window
-- boundaries for each 1-minute chunk. Since we bulk-copied all existing data
-- above, we start the pipeline from now() to avoid duplicates.

SELECT incremental.create_time_interval_pipeline(
    pipeline_name      := 'sync_portal_activity_to_iceberg',
    time_interval      := '1 minute',
    source_table_name  := 'portal_activity_log',
    start_time         := now(),
    command            := $inner$
        INSERT INTO portal_activity_log_iceberg
        SELECT activity_id, customer_key, event_time, event_type,
               event_detail, city, region, customer_type
        FROM portal_activity_log
        WHERE event_time >= $1 AND event_time < $2
    $inner$
);

-- ---------------------------------------------------------------------------
-- Section 3: Verification
-- ---------------------------------------------------------------------------

SELECT 'portal_users' AS table_name, count(*) AS rows FROM portal_users
UNION ALL SELECT 'meter_readings', count(*) FROM meter_readings
UNION ALL SELECT 'tariff_orders', count(*) FROM tariff_orders
UNION ALL SELECT 'service_requests', count(*) FROM service_requests
UNION ALL SELECT 'portal_activity_log', count(*) FROM portal_activity_log
ORDER BY table_name;

SELECT
    (SELECT count(*) FROM portal_activity_log) AS heap_rows,
    (SELECT count(*) FROM portal_activity_log_iceberg) AS iceberg_rows;

-- ---------------------------------------------------------------------------
-- Section 4: Live Demo Helper
-- ---------------------------------------------------------------------------
-- Run this during a demo to simulate 50 customers using the portal RIGHT NOW.
-- After running, wait ~60 seconds for pg_incremental to sync to Iceberg,
-- then verify in Snowflake.

-- INSERT INTO portal_activity_log (customer_key, event_time, event_type, event_detail, city, region, customer_type)
-- SELECT
--     customer_key,
--     now(),
--     (ARRAY['LOGIN', 'METER_READING', 'TARIFF_CHANGE', 'SERVICE_REQUEST'])[1 + (random() * 3)::int],
--     '{"source": "live_demo"}',
--     'Hamburg',
--     'Nord',
--     'Privatkunde'
-- FROM portal_users
-- ORDER BY random()
-- LIMIT 50;
