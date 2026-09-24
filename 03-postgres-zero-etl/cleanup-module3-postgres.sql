-- ========================================================================
-- Module 3 Cleanup: Postgres Side
-- Run this BEFORE dropping the Postgres instance from Snowflake.
--
--   psql service=my_epower_portal -f cleanup-module3-postgres.sql
-- ========================================================================

-- Stop the incremental pipeline first
SELECT incremental.drop_pipeline('sync_portal_activity_to_iceberg');

-- Drop Iceberg mirror table
DROP TABLE IF EXISTS portal_activity_log_iceberg;

-- Drop portal tables
DROP TABLE IF EXISTS portal_activity_log CASCADE;
DROP TABLE IF EXISTS service_requests CASCADE;
DROP TABLE IF EXISTS tariff_orders CASCADE;
DROP TABLE IF EXISTS meter_readings CASCADE;
DROP TABLE IF EXISTS portal_users CASCADE;

-- Drop extensions
DROP EXTENSION IF EXISTS pg_incremental CASCADE;
DROP EXTENSION IF EXISTS pg_cron CASCADE;
DROP EXTENSION IF EXISTS pg_lake CASCADE;

SELECT 'Module 3 Postgres cleanup completed.' AS status;
