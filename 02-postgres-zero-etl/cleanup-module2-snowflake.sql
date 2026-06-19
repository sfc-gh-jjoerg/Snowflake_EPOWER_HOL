-- ========================================================================
-- Module 2 Cleanup: Snowflake Side
-- Run this AFTER the Postgres cleanup (cleanup-module2-postgres.sql).
-- Requires ACCOUNTADMIN role.
--
-- DEPENDENCY ORDER (important!):
--   1. Drop data objects (Iceberg table, views, semantic view, stage)
--   2. Drop catalog integration
--   3. Detach network policy from Postgres instance
--   4. Drop Postgres instance
--   5. Drop network policy and network rule
--   6. Restore agent to Module 1 state
-- ========================================================================

USE ROLE ACCOUNTADMIN;

-- ========================================================================
-- STEP 1: Drop data objects
-- ========================================================================
DROP ICEBERG TABLE IF EXISTS EPOWER_DEMO.EPOWER_BRONZE.PORTAL_ACTIVITY_LOG;
DROP TABLE IF EXISTS EPOWER_DEMO.EPOWER_GOLD.MART_PORTAL_ENGAGEMENT;
DROP SEMANTIC VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.PORTAL_SEMANTIC_VIEW;
DROP STAGE IF EXISTS EPOWER_DEMO.EPOWER_GOLD.PORTAL_SEED_STAGE;

-- ========================================================================
-- STEP 2: Drop catalog integration
-- ========================================================================
DROP CATALOG INTEGRATION IF EXISTS PORTAL_POSTGRES_CATALOG;

-- ========================================================================
-- STEP 3: Detach network policy from Postgres instance
-- (Must happen BEFORE dropping the policy — a policy cannot be dropped
--  while it is still assigned to an entity)
-- ========================================================================
BEGIN
    ALTER POSTGRES INSTANCE MY_EPOWER_PORTAL UNSET NETWORK_POLICY;
EXCEPTION
    WHEN OTHER THEN NULL;  -- Instance may not exist
END;

-- ========================================================================
-- STEP 4: Drop Postgres instance (irreversible)
-- ========================================================================
DROP POSTGRES INSTANCE IF EXISTS MY_EPOWER_PORTAL;

-- ========================================================================
-- STEP 5: Drop network policy and rule
-- (Now safe — policy is no longer attached to any entity)
-- ========================================================================
DROP NETWORK POLICY IF EXISTS EPOWER_PG_POLICY;
DROP NETWORK RULE IF EXISTS EPOWER_PG_INGRESS;

-- ========================================================================
-- STEP 6: Restore agent to Module 1 state (without portal_analyst)
-- ========================================================================
USE ROLE EPOWER_ROLE;
USE WAREHOUSE EPOWER_COMPUTE;

CREATE OR REPLACE AGENT EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT
WITH PROFILE='{ "display_name": "EPOWER AGENT" }'
FROM SPECIFICATION $$
models:
  orchestration: auto
instructions:
  response: |
    You are a data analyst for EPOWER Energie Deutschland.
    CRITICAL LANGUAGE RULE: You MUST always respond in the SAME language as the user's question.
    DATA ACCESS: Energy sales, billing/consumption, service tickets, HR data, day-ahead electricity market prices, VPP IoT telemetry, and documents.
  orchestration: |
    TOOL SELECTION:
    - Document questions → energy_docs_search, product_docs_search, service_docs_search
    - Consumption + products → customer_energy_analyst
    - Sales/contracts → energy_sales_analyst
    - Billing → billing_analyst
    - Service tickets → service_analyst
    - HR data → hr_analyst
    - Electricity market prices, day-ahead → epulse_prices_analyst
    - VPP telemetry, solar yield, battery SOC, grid import/export → vpp_telemetry_analyst
tools:
  - tool_spec: {type: cortex_analyst_text_to_sql, name: energy_sales_analyst, description: "Contracts, products, sales, revenue"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: billing_analyst, description: "Consumption, billing, payments"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: customer_energy_analyst, description: "Consumption by product ownership"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: service_analyst, description: "Service tickets, complaints"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: hr_analyst, description: "HR data, salaries"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: market_prices_analyst, description: "Day-ahead electricity market prices"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: vpp_telemetry_analyst, description: "VPP IoT telemetry: solar yield, battery SOC, grid import/export"}
  - tool_spec: {type: cortex_search, name: energy_docs_search, description: "Energy policies, terms"}
  - tool_spec: {type: cortex_search, name: product_docs_search, description: "Product documentation"}
  - tool_spec: {type: cortex_search, name: service_docs_search, description: "Service handbook"}
  - tool_spec: {type: cortex_search, name: service_logs_search, description: "Historical tickets"}
  - tool_spec: {type: data_to_chart, name: data_to_chart, description: "Generate visualizations"}
tool_resources:
  energy_sales_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.ENERGY_SALES_SEMANTIC_VIEW", execution_environment: {type: warehouse, warehouse: EPOWER_COMPUTE}}
  billing_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.BILLING_SEMANTIC_VIEW", execution_environment: {type: warehouse, warehouse: EPOWER_COMPUTE}}
  customer_energy_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_ENERGY_SEMANTIC_VIEW", execution_environment: {type: warehouse, warehouse: EPOWER_COMPUTE}}
  service_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.SERVICE_SEMANTIC_VIEW", execution_environment: {type: warehouse, warehouse: EPOWER_COMPUTE}}
  hr_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.HR_SEMANTIC_VIEW", execution_environment: {type: warehouse, warehouse: EPOWER_COMPUTE}}
  market_prices_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.MARKET_PRICES_SEMANTIC_VIEW", execution_environment: {type: warehouse, warehouse: EPOWER_COMPUTE}}
  vpp_telemetry_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.EPULSE_VPP_SEMANTIC_VIEW", execution_environment: {type: warehouse, warehouse: EPOWER_COMPUTE}}
  energy_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_ENERGY_DOCS", max_results: 5}
  product_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_PRODUCT_DOCS", max_results: 5}
  service_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_DOCS", max_results: 5}
  service_logs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_LOGS", max_results: 5}
$$;

SELECT 'Module 2 Snowflake cleanup completed. Agent restored to Module 1 state.' AS status;
