-- ========================================================================
-- Module 2: EPOWER VPP Monitor - One-time Account Setup (Additional Grants)
-- ========================================================================
-- ONE-TIME SETUP: run once per account (and once per deploy role).
-- Not needed for subsequent deploys - 'snow app deploy' reuses these grants.
-- Re-running is harmless (GRANT is idempotent).
--
-- Run as ACCOUNTADMIN.
--
-- PREREQUISITE:
--   Step 1 of README-module2.md completed in Snowsight
--   (Settings -> Account -> Apps -> Begin Setup -> Quick start).
--   The wizard creates SNOWFLAKE_APPS + SNOWFLAKE_APPS_QUERY_WH and grants
--   the deploy role CREATE APPLICATION SERVICE etc. on SNOWFLAKE_APPS.PUBLIC.
--
-- WHAT THIS ADDS (not covered by the wizard):
--   1. USAGE on the compute pool used to build and run the app
--   2. BIND SERVICE ENDPOINT so the service can expose its HTTPS endpoint
--
-- Replace SYSADMIN below if you selected a different deploy role
-- in the wizard (must match the role of your Snowflake CLI connection).
-- ========================================================================

USE ROLE ACCOUNTADMIN;

-- Step 1: Allow the deploy role to use the compute pool
GRANT USAGE ON COMPUTE POOL SYSTEM_COMPUTE_POOL_CPU TO ROLE SYSADMIN;

-- Step 2: Allow the service to expose an HTTPS endpoint
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE SYSADMIN;

-- Verification
SHOW GRANTS TO ROLE SYSADMIN
  ->> SELECT "privilege", "granted_on", "name"
      FROM $1
      WHERE "privilege" = 'BIND SERVICE ENDPOINT'
         OR "granted_on" = 'COMPUTE_POOL'
         OR "name" LIKE 'SNOWFLAKE_APPS%';

SELECT 'Module 2 (VPP Monitor) one-time setup completed!' AS status;
