-- ========================================================================
-- Module 5: EPOWER VPP Monitor - Cleanup Script
-- ========================================================================
-- Removes the Snowflake App and all associated objects created by Module 5.
-- Safe to run even if some objects don't exist (uses IF EXISTS).
--
-- Run as SYSADMIN (or ACCOUNTADMIN if SYSADMIN lacks permissions).
--
-- WHAT THIS REMOVES:
--   1. Application Service (stops the container, frees compute)
--   2. Artifact repository (built images)
--   3. Code stage (uploaded source files)
--   4. Snowflake views in EPOWER_DEMO.EPOWER_GOLD
--
-- WHAT THIS DOES NOT REMOVE:
--   - The SNOWFLAKE_APPS database (shared by all apps on the account)
--   - The SNOWFLAKE_APPS_QUERY_WH warehouse
--   - The base tables in EPOWER_DEMO that the views read from
-- ========================================================================

USE ROLE SYSADMIN;

-- Step 1: Drop the Application Service (stops the running container)
DROP APPLICATION SERVICE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR;

-- Step 2: Drop the artifact repository (contains built Docker images)
DROP ARTIFACT REPOSITORY IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_REPO;

-- Step 3: Drop the code stage (uploaded source files)
DROP STAGE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_CODE;

-- Step 4: Drop the backend views
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_ACTIONS;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_KPI;

-- Verification
SHOW APPLICATION SERVICES LIKE 'EPOWER_VPP%' IN SCHEMA SNOWFLAKE_APPS.PUBLIC;
SELECT 'Module 5 (VPP Monitor) cleanup completed!' AS status;
