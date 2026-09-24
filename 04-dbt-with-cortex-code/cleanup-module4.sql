-- ============================================================
-- EPOWER Module 4 — Cleanup Script
-- Removes all objects created by Module 4
-- Does NOT affect Module 1 or Module 3 objects
-- ============================================================

USE ROLE EPOWER_ROLE;
USE WAREHOUSE EPOWER_COMPUTE;
USE DATABASE EPOWER_DEMO;

-- Source tables (loaded from CSV into Bronze)
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_BRONZE.CONTRACT_CANCELLATIONS;
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_BRONZE.CUSTOMER_SURVEYS;

-- dbt staging models (created by CoCo in EPOWER_SILVER)
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_SILVER.STG_CANCELLATIONS;
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_SILVER.STG_SURVEYS;

-- dbt mart models (created by CoCo in EPOWER_GOLD)
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_GOLD.MART_CUSTOMER_CHURN;
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_GOLD.MART_NPS_ANALYSIS;
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_GOLD.MART_CUSTOMER_HEALTH;

-- Semantic View (bonus section)
DROP SEMANTIC VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_HEALTH_SEMANTIC_VIEW;

-- Note: The EPOWER_AGENT is re-created cumulatively by each module.
-- After cleanup, re-run Module 1 (or Module 3) agent cell to restore
-- the agent without the customer_health_analyst tool.

SELECT 'Module 4 cleanup complete' AS status;
