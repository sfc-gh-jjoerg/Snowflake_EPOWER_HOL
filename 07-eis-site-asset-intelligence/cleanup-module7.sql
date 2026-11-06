-- =============================================================================
-- Module 7 Cleanup: EIS Site & Asset Intelligence
-- Removes all Module 7 objects. Module 1 objects (EPOWER_GOLD etc.) stay untouched.
-- Requires ACCOUNTADMIN for removing the agent from Snowflake CoWork.
-- =============================================================================

USE ROLE ACCOUNTADMIN;

-- 1. Remove the agent from Snowflake CoWork (ignore error if it isn't registered)
BEGIN
    ALTER SNOWFLAKE INTELLIGENCE snowflake_intelligence_object_default
        DROP AGENT EPOWER_DEMO.EIS_GOLD.EIS_OPERATIONS_AGENT;
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Agent not registered in CoWork - skipped';
END;

-- 2. Drop the EIS schema: tables, views, stage, semantic view, Cortex Search service, agent, MCP server
DROP SCHEMA IF EXISTS EPOWER_DEMO.EIS_GOLD CASCADE;

-- 3. Make sure the warehouse is back to its Module 1 size (in case setup stopped mid-way)
ALTER WAREHOUSE IF EXISTS EPOWER_COMPUTE SET WAREHOUSE_SIZE = 'SMALL';

USE ROLE EPOWER_ROLE;
