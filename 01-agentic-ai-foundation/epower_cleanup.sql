-- ========================================================================
-- EPOWER Energy Demo - Full Cleanup Script
-- Run with ACCOUNTADMIN role to ensure all objects can be dropped.
--
-- This script handles cleanup for ALL modules (1, 2, 3, 4, 5).
-- It is safe to run even if only some modules were deployed.
--
-- DEPENDENCY ORDER:
--   1. Remove agent from Snowflake Intelligence
--   2. Drop VPP Monitor app service (Module 5)
--   3. Detach network policy from Postgres instance (Module 2)
--   4. Drop Postgres instance (Module 2)
--   5. Drop network policy and rule (Module 2)
--   6. Drop integrations
--   7. Drop database (includes all schemas, tables, views, etc.)
--   8. Drop SNOWFLAKE_APPS objects (Module 5 artifacts)
--   9. Drop warehouse
--  10. Drop role
-- ========================================================================

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE EPOWER_COMPUTE;

-- ========================================================================
-- STEP 1: REMOVE AGENT FROM SNOWFLAKE INTELLIGENCE
-- ========================================================================
BEGIN
    ALTER SNOWFLAKE INTELLIGENCE snowflake_intelligence_object_default 
        DROP AGENT EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT;
EXCEPTION
    WHEN OTHER THEN NULL;
END;

-- ========================================================================
-- STEP 2: DROP VPP MONITOR APP SERVICE (Module 5)
-- Must happen before dropping EPOWER_DEMO database since the app queries
-- views in that database. Also removes the artifact repo and code stage.
-- Safe to skip if Module 5 was never deployed (IF EXISTS).
-- Note: SNOWFLAKE_APPS database may not exist if App Development Setup
-- was never run — wrap in BEGIN/EXCEPTION to handle gracefully.
-- ========================================================================
BEGIN
    DROP APPLICATION SERVICE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR;
    DROP ARTIFACT REPOSITORY IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_REPO;
    DROP STAGE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_CODE;
EXCEPTION
    WHEN OTHER THEN NULL;  -- SNOWFLAKE_APPS database may not exist
END;

-- ========================================================================
-- STEP 3: DETACH NETWORK POLICY FROM POSTGRES INSTANCE (Module 2)
-- Must happen BEFORE dropping the network policy. A policy cannot be
-- dropped while still assigned to an entity.
-- ========================================================================
BEGIN
    ALTER POSTGRES INSTANCE MY_EPOWER_PORTAL UNSET NETWORK_POLICY;
EXCEPTION
    WHEN OTHER THEN NULL;  -- Instance may not exist if Module 2 was not run
END;

-- ========================================================================
-- STEP 4: DROP POSTGRES INSTANCE (Module 2)
-- ========================================================================
DROP POSTGRES INSTANCE IF EXISTS MY_EPOWER_PORTAL;

-- ========================================================================
-- STEP 5: DROP NETWORK POLICY AND RULE (Module 2)
-- Now safe — policy is no longer attached to any entity.
-- Note: USE DATABASE required because BEGIN...END resets session context.
-- ========================================================================
USE DATABASE EPOWER_DEMO;
DROP NETWORK POLICY IF EXISTS EPOWER_PG_POLICY;
DROP NETWORK RULE IF EXISTS EPOWER_PG_INGRESS;

-- ========================================================================
-- STEP 6: DROP INTEGRATIONS
-- ========================================================================
DROP CATALOG INTEGRATION IF EXISTS PORTAL_POSTGRES_CATALOG;
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS Energy_ExternalAccess;
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS energy_charts_integration;
DROP API INTEGRATION IF EXISTS git_api_integration_energy;

-- ========================================================================
-- STEP 7: DROP DATABASE (includes all schemas, tables, views, stages, etc.)
-- ========================================================================
DROP DATABASE IF EXISTS EPOWER_DEMO;

-- ========================================================================
-- STEP 8: DROP WAREHOUSE
-- ========================================================================
DROP WAREHOUSE IF EXISTS EPOWER_COMPUTE;

-- ========================================================================
-- STEP 9: DROP ROLE
-- ========================================================================
SET current_user_name = CURRENT_USER();
ALTER USER IDENTIFIER($current_user_name) SET DEFAULT_ROLE = 'SYSADMIN';
DROP ROLE IF EXISTS EPOWER_ROLE;

-- ========================================================================
-- VERIFICATION
-- ========================================================================
SHOW DATABASES LIKE 'EPOWER%';
SHOW WAREHOUSES LIKE 'EPOWER%';
SHOW ROLES LIKE 'EPOWER%';
SHOW INTEGRATIONS LIKE '%energy%';
SHOW INTEGRATIONS LIKE '%PORTAL%';
SHOW NETWORK POLICIES LIKE 'EPOWER%';

-- Module 5 verification (may fail if SNOWFLAKE_APPS database doesn't exist)
BEGIN
    SHOW APPLICATION SERVICES LIKE 'EPOWER%' IN SCHEMA SNOWFLAKE_APPS.PUBLIC;
EXCEPTION
    WHEN OTHER THEN NULL;
END;

SELECT 'EPOWER Demo cleanup completed!' AS status;
