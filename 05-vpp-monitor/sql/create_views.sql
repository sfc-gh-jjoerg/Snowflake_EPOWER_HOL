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
-- 0. VPP_CLUSTER_DIM & CITY_CLUSTER_MAP
--    Reference tables for the 14 VPP regional clusters.
--    Maps each city in the dataset to its corresponding cluster.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS VPP_CLUSTER_DIM (
    CLUSTER_ID      VARCHAR(30) PRIMARY KEY,
    CLUSTER_NAME    VARCHAR(50),
    COMPASS_REGION  VARCHAR(10),
    CENTROID_LAT    FLOAT,
    CENTROID_LNG    FLOAT
);

MERGE INTO VPP_CLUSTER_DIM t USING (
    SELECT * FROM VALUES
        ('freiburg_oberrhein', 'Freiburg/Oberrhein',  'South', 47.99, 7.85),
        ('bavaria_south',      'Bayern Sued',         'South', 47.85, 11.90),
        ('munich_metro',       'Muenchen Metro',      'South', 48.14, 11.58),
        ('stuttgart_metro',    'Stuttgart Metro',     'South', 48.78, 9.18),
        ('nuernberg_franken',  'Nuernberg/Franken',   'South', 49.45, 11.08),
        ('frankfurt_main',     'Frankfurt/Rhein-Main','West',  50.11, 8.68),
        ('koeln_bonn',         'Koeln/Bonn',          'West',  50.94, 6.96),
        ('rhine_ruhr',         'Rhein-Ruhr',          'West',  51.23, 6.78),
        ('berlin_metro',       'Berlin Metro',        'East',  52.52, 13.41),
        ('leipzig_halle',      'Leipzig/Halle',       'East',  51.34, 12.38),
        ('saxony_east',        'Sachsen/Ost',         'East',  51.05, 13.74),
        ('hamburg_metro',      'Hamburg Metro',       'North', 53.55, 9.99),
        ('bremen_weser',       'Bremen/Weser',        'North', 53.08, 8.80),
        ('lower_saxony',       'Niedersachsen/Nord',  'North', 52.65, 9.20)
    AS s(CLUSTER_ID, CLUSTER_NAME, COMPASS_REGION, CENTROID_LAT, CENTROID_LNG)
) s ON t.CLUSTER_ID = s.CLUSTER_ID
WHEN MATCHED THEN UPDATE SET
    CLUSTER_NAME = s.CLUSTER_NAME, COMPASS_REGION = s.COMPASS_REGION,
    CENTROID_LAT = s.CENTROID_LAT, CENTROID_LNG = s.CENTROID_LNG
WHEN NOT MATCHED THEN INSERT VALUES
    (s.CLUSTER_ID, s.CLUSTER_NAME, s.COMPASS_REGION, s.CENTROID_LAT, s.CENTROID_LNG);

-- City-to-cluster mapping for all 40 cities in MART_VPP_PRICE_OPTIMIZATION
CREATE OR REPLACE TABLE CITY_CLUSTER_MAP (
    CITY        VARCHAR(100),
    REGION      VARCHAR(10),
    CLUSTER_ID  VARCHAR(30),
    FOREIGN KEY (CLUSTER_ID) REFERENCES VPP_CLUSTER_DIM(CLUSTER_ID)
);

INSERT INTO CITY_CLUSTER_MAP (CITY, REGION, CLUSTER_ID) VALUES
    -- South clusters
    ('Freiburg',    'South', 'freiburg_oberrhein'),
    ('Augsburg',    'South', 'bavaria_south'),
    ('Ingolstadt',  'South', 'bavaria_south'),
    ('Regensburg',  'South', 'bavaria_south'),
    ('München',     'South', 'munich_metro'),
    ('Stuttgart',   'South', 'stuttgart_metro'),
    ('Karlsruhe',   'South', 'stuttgart_metro'),
    ('Ulm',         'South', 'stuttgart_metro'),
    ('Nürnberg',    'South', 'nuernberg_franken'),
    ('Würzburg',    'South', 'nuernberg_franken'),
    -- West clusters
    ('Frankfurt',   'West',  'frankfurt_main'),
    ('Köln',        'West',  'koeln_bonn'),
    ('Bonn',        'West',  'koeln_bonn'),
    ('Aachen',      'West',  'koeln_bonn'),
    ('Düsseldorf',  'West',  'rhine_ruhr'),
    ('Dortmund',    'West',  'rhine_ruhr'),
    ('Essen',       'West',  'rhine_ruhr'),
    ('Bochum',      'West',  'rhine_ruhr'),
    ('Duisburg',    'West',  'rhine_ruhr'),
    ('Wuppertal',   'West',  'rhine_ruhr'),
    ('Münster',     'West',  'rhine_ruhr'),
    -- East clusters
    ('Berlin',      'East',  'berlin_metro'),
    ('Potsdam',     'East',  'berlin_metro'),
    ('Cottbus',     'East',  'berlin_metro'),
    ('Leipzig',     'East',  'leipzig_halle'),
    ('Halle',       'East',  'leipzig_halle'),
    ('Jena',        'East',  'leipzig_halle'),
    ('Erfurt',      'East',  'leipzig_halle'),
    ('Magdeburg',   'East',  'leipzig_halle'),
    ('Dresden',     'East',  'saxony_east'),
    ('Chemnitz',    'East',  'saxony_east'),
    -- North clusters
    ('Hamburg',     'North', 'hamburg_metro'),
    ('Kiel',        'North', 'hamburg_metro'),
    ('Lübeck',      'North', 'hamburg_metro'),
    ('Rostock',     'North', 'hamburg_metro'),
    ('Bremen',      'North', 'bremen_weser'),
    ('Hannover',    'North', 'lower_saxony'),
    ('Braunschweig','North', 'lower_saxony'),
    ('Oldenburg',   'North', 'lower_saxony'),
    ('Osnabrück',   'North', 'lower_saxony'),
    ('Wolfsburg',   'North', 'lower_saxony');

-- -----------------------------------------------------------------------------
-- 1. V_VPP_MONITOR_TIMESERIES
--    Hourly/daily aggregation with cluster support.
--    Built from price optimization + city-cluster map.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_VPP_MONITOR_TIMESERIES AS
SELECT
    o.HOUR,
    o.REGION,
    cm.CLUSTER_ID,
    COUNT(DISTINCT o.CUSTOMER_KEY)  AS ACTIVE_VPP_DEVICES,
    ROUND(SUM(o.AVG_BATTERY_SOC_PCT * 1.0) / NULLIF(COUNT(*), 0), 1) AS AVG_BATTERY_SOC_PCT,
    ROUND(AVG(o.AVG_SOLAR_KW), 2)  AS AVG_SOLAR_YIELD_KW,
    ROUND(SUM(o.TOTAL_IMPORT_KWH) - SUM(o.TOTAL_EXPORT_KWH), 2) AS NET_GRID_KW,
    AVG(o.PRICE_EUR_MWH)           AS PRICE_EUR_MWH
FROM MART_VPP_PRICE_OPTIMIZATION o
JOIN CITY_CLUSTER_MAP cm ON o.CITY = cm.CITY AND o.REGION = cm.REGION
GROUP BY o.HOUR, o.REGION, cm.CLUSTER_ID;

-- -----------------------------------------------------------------------------
-- 2. V_VPP_MONITOR_ACTIONS
--    Battery action distribution and margin totals by day/region/cluster/type.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_VPP_MONITOR_ACTIONS AS
SELECT
    DATE_TRUNC('day', o.HOUR)::DATE AS DAY,
    o.REGION,
    cm.CLUSTER_ID,
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
JOIN CITY_CLUSTER_MAP cm ON o.CITY = cm.CITY AND o.REGION = cm.REGION
GROUP BY 1, 2, 3, 4, 5;

-- -----------------------------------------------------------------------------
-- 3. V_VPP_MONITOR_KPI
--    Summary KPIs by day/region/cluster/customer_type.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_VPP_MONITOR_KPI AS
SELECT
    DATE_TRUNC('day', o.HOUR)::DATE AS DAY,
    o.REGION,
    cm.CLUSTER_ID,
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
JOIN CITY_CLUSTER_MAP cm ON o.CITY = cm.CITY AND o.REGION = cm.REGION
GROUP BY 1, 2, 3, 4;

-- -----------------------------------------------------------------------------
-- 4. V_VPP_MONITOR_MAP
--    Hourly cluster-level aggregation for the regional comparison chart.
--    Built from price optimization + cluster dim for display names.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW V_VPP_MONITOR_MAP AS
SELECT
    o.HOUR,
    cm.CLUSTER_ID,
    cl.CLUSTER_NAME,
    cl.COMPASS_REGION,
    COUNT(DISTINCT o.CUSTOMER_KEY)  AS ACTIVE_DEVICES,
    ROUND(AVG(o.AVG_BATTERY_SOC_PCT), 1) AS AVG_SOC_PCT,
    ROUND(AVG(o.AVG_SOLAR_KW), 2)  AS AVG_SOLAR_KW,
    ROUND(SUM(o.TOTAL_IMPORT_KWH), 1) AS TOTAL_IMPORT_KWH,
    ROUND(SUM(o.TOTAL_EXPORT_KWH), 1) AS TOTAL_EXPORT_KWH,
    ROUND(SUM(o.TOTAL_EXPORT_KWH) - SUM(o.TOTAL_IMPORT_KWH), 1) AS NET_FLOW_KWH,
    ROUND(AVG(o.PRICE_EUR_MWH), 2) AS AVG_PRICE_EUR_MWH
FROM MART_VPP_PRICE_OPTIMIZATION o
JOIN CITY_CLUSTER_MAP cm ON o.CITY = cm.CITY AND o.REGION = cm.REGION
JOIN VPP_CLUSTER_DIM cl ON cm.CLUSTER_ID = cl.CLUSTER_ID
GROUP BY o.HOUR, cm.CLUSTER_ID, cl.CLUSTER_NAME, cl.COMPASS_REGION;
