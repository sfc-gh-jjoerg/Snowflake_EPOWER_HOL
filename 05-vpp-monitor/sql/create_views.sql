-- =============================================================================
-- EPOWER VPP Monitor — Backend Views
-- =============================================================================
-- These views power the EPOWER VPP Monitor dashboard.
-- Run this script before deploying the app.
--
-- Usage:
--   USE ROLE EPOWER_ROLE;
--   USE WAREHOUSE EPOWER_COMPUTE;
--   !source create_views.sql
-- =============================================================================

USE ROLE EPOWER_ROLE;
USE WAREHOUSE EPOWER_COMPUTE;
USE SCHEMA EPOWER_DEMO.EPOWER_GOLD;

-- -----------------------------------------------------------------------------
-- 1. V_VPP_MONITOR_TIMESERIES
--    Joins hourly VPP capacity with day-ahead prices.
--    Supports both hourly and daily granularity via the consuming query.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_VPP_MONITOR_TIMESERIES AS
SELECT
    c.HOUR,
    c.REGION,
    c.ACTIVE_VPP_DEVICES,
    c.TOTAL_BATTERY_SOC,
    c.AVG_BATTERY_SOC_PCT,
    c.TOTAL_SOLAR_YIELD_KW,
    c.AVG_SOLAR_YIELD_KW,
    c.NET_GRID_KW,
    p.PRICE_EUR_MWH,
    p.PRICE_EUR_KWH,
    p.DAY_OF_WEEK,
    p.HOUR_OF_DAY
FROM MART_VPP_CAPACITY_HOURLY c
LEFT JOIN (
    -- Day-ahead prices are at 15-min granularity; average to hourly
    SELECT
        HOUR,
        AVG(PRICE_EUR_MWH) AS PRICE_EUR_MWH,
        AVG(PRICE_EUR_KWH) AS PRICE_EUR_KWH,
        ANY_VALUE(DAY_OF_WEEK) AS DAY_OF_WEEK,
        ANY_VALUE(HOUR_OF_DAY) AS HOUR_OF_DAY
    FROM MART_DAY_AHEAD_PRICES
    GROUP BY HOUR
) p ON c.HOUR = p.HOUR;

-- -----------------------------------------------------------------------------
-- 2. V_VPP_MONITOR_ACTIONS
--    Aggregates the 23M-row price optimization table by day/region/customer_type.
--    Returns battery action distribution and margin totals.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_VPP_MONITOR_ACTIONS AS
SELECT
    DATE_TRUNC('day', o.HOUR)::DATE AS DAY,
    o.REGION,
    c.CUSTOMER_TYPE,
    o.BATTERY_ACTION,
    COUNT(*) AS ACTION_COUNT,
    SUM(o.TOTAL_IMPORT_KWH) AS TOTAL_IMPORT_KWH,
    SUM(o.TOTAL_EXPORT_KWH) AS TOTAL_EXPORT_KWH,
    SUM(o.IMPORT_COST_EUR) AS TOTAL_IMPORT_COST_EUR,
    SUM(o.EXPORT_REVENUE_EUR) AS TOTAL_EXPORT_REVENUE_EUR,
    SUM(o.NET_MARGIN_EUR) AS TOTAL_NET_MARGIN_EUR,
    SUM(o.CUSTOMER_MARGIN_EUR) AS TOTAL_CUSTOMER_MARGIN_EUR,
    SUM(o.EPOWER_MARGIN_EUR) AS TOTAL_EPOWER_MARGIN_EUR
FROM MART_VPP_PRICE_OPTIMIZATION o
JOIN CUSTOMER_DIM c ON o.CUSTOMER_KEY = c.CUSTOMER_KEY
GROUP BY 1, 2, 3, 4;

-- -----------------------------------------------------------------------------
-- 3. V_VPP_MONITOR_KPI
--    Summary KPIs derived from the optimization table (has customer granularity).
--    One row per day/region/customer_type with device counts, SOC, solar, grid,
--    price, and margin aggregates.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_VPP_MONITOR_KPI AS
SELECT
    DATE_TRUNC('day', o.HOUR)::DATE AS DAY,
    o.REGION,
    c.CUSTOMER_TYPE,
    COUNT(DISTINCT o.CUSTOMER_KEY) AS ACTIVE_VPP_DEVICES,
    AVG(o.AVG_BATTERY_SOC_PCT) AS AVG_BATTERY_SOC_PCT,
    AVG(o.AVG_SOLAR_KW) AS AVG_SOLAR_KW,
    SUM(o.TOTAL_IMPORT_KWH) - SUM(o.TOTAL_EXPORT_KWH) AS NET_GRID_KWH,
    AVG(o.PRICE_EUR_MWH) AS AVG_PRICE_EUR_MWH,
    SUM(o.CUSTOMER_MARGIN_EUR) AS TOTAL_CUSTOMER_MARGIN_EUR,
    SUM(o.EPOWER_MARGIN_EUR) AS TOTAL_EPOWER_MARGIN_EUR,
    SUM(o.NET_MARGIN_EUR) AS TOTAL_NET_MARGIN_EUR
FROM MART_VPP_PRICE_OPTIMIZATION o
JOIN CUSTOMER_DIM c ON o.CUSTOMER_KEY = c.CUSTOMER_KEY
GROUP BY 1, 2, 3;
