{{ config(materialized='semantic_view') }}

TABLES (
    TELEMETRY AS {{ ref('fct_epulse_telemetry') }}
        PRIMARY KEY (TS, GATEWAY_ID),
    PRICE_OPT AS {{ ref('mart_vpp_price_optimization') }}
        PRIMARY KEY (HOUR, CUSTOMER_KEY),
    CLUSTER AS {{ source('epower_gold', 'vpp_cluster_dim') }}
        PRIMARY KEY (CLUSTER_ID)
)

RELATIONSHIPS (
    TELEMETRY_TO_CLUSTER AS TELEMETRY (CLUSTER_ID) REFERENCES CLUSTER,
    PRICE_OPT_TO_CLUSTER AS PRICE_OPT (CLUSTER_ID) REFERENCES CLUSTER
)

FACTS (
    TELEMETRY.SOLAR_YIELD_KW AS SOLAR_YIELD_KW
        COMMENT = 'Solar generation in kW per device per hour',
    TELEMETRY.BATTERY_SOC_PCT AS BATTERY_SOC_PCT
        COMMENT = 'Battery state of charge 0-100 percent',
    TELEMETRY.HEATPUMP_CONSUMPTION_KW AS HEATPUMP_CONSUMPTION_KW
        COMMENT = 'Heat pump power draw in kW',
    TELEMETRY.GRID_IMPORT_KW AS GRID_IMPORT_KW
        COMMENT = 'Power drawn FROM grid in kW (always >= 0, high when charging from cheap grid power)',
    TELEMETRY.GRID_EXPORT_KW AS GRID_EXPORT_KW
        COMMENT = 'Power fed TO grid in kW (always >= 0, high when discharging during expensive hours)',

    PRICE_OPT.TOTAL_IMPORT_KWH AS TOTAL_IMPORT_KWH
        COMMENT = 'Total energy imported from grid in kWh for this customer-hour',
    PRICE_OPT.TOTAL_EXPORT_KWH AS TOTAL_EXPORT_KWH
        COMMENT = 'Total energy exported to grid in kWh for this customer-hour',
    PRICE_OPT.PRICE_EUR_MWH AS PRICE_EUR_MWH
        COMMENT = 'Day-ahead electricity price in EUR per MWh',
    PRICE_OPT.IMPORT_COST_EUR AS IMPORT_COST_EUR
        COMMENT = 'Cost of grid import for this customer-hour in EUR',
    PRICE_OPT.EXPORT_REVENUE_EUR AS EXPORT_REVENUE_EUR
        COMMENT = 'Revenue from grid export for this customer-hour in EUR',
    PRICE_OPT.NET_MARGIN_EUR AS NET_MARGIN_EUR
        COMMENT = 'Net margin (export revenue minus import cost) in EUR',
    PRICE_OPT.CUSTOMER_MARGIN_EUR AS CUSTOMER_MARGIN_EUR
        COMMENT = 'Customer share of VPP margin (70 percent) in EUR',
    PRICE_OPT.EPOWER_MARGIN_EUR AS EPOWER_MARGIN_EUR
        COMMENT = 'EPOWER share of VPP margin (30 percent) in EUR'
)

DIMENSIONS (
    TELEMETRY.TS AS TS
        COMMENT = 'Telemetry timestamp (15-min intervals)',
    TELEMETRY.GATEWAY_ID AS GATEWAY_ID
        COMMENT = 'IoT gateway device identifier',
    TELEMETRY.CUSTOMER_KEY AS CUSTOMER_KEY,
    TELEMETRY.CUSTOMER_NAME AS CUSTOMER_NAME,
    TELEMETRY.CITY AS CITY,
    TELEMETRY.REGION AS REGION
        COMMENT = 'German region: North, South, East, or West',
    TELEMETRY.CLUSTER_ID AS CLUSTER_ID
        COMMENT = 'VPP geographic cluster identifier',
    TELEMETRY.CUSTOMER_TYPE AS CUSTOMER_TYPE,
    TELEMETRY.IS_VPP_ENROLLED AS IS_VPP_ENROLLED
        COMMENT = 'True if customer has battery and is enrolled in VPP program',

    PRICE_OPT.HOUR AS HOUR
        COMMENT = 'Hour timestamp for price optimization',
    PRICE_OPT.PRICE_ZONE AS PRICE_ZONE
        COMMENT = 'Price classification: NEGATIVE, LOW, MEDIUM, HIGH, or NO_PRICE_DATA',
    PRICE_OPT.BATTERY_ACTION AS BATTERY_ACTION
        COMMENT = 'VPP strategy action: MAX_CHARGE, CHARGE, DISCHARGE, or SELF_CONSUME',

    CLUSTER.CLUSTER_NAME AS CLUSTER_NAME
        COMMENT = 'Human-readable cluster name',
    CLUSTER.COMPASS_REGION AS COMPASS_REGION
        COMMENT = 'Compass direction region grouping',
    CLUSTER.REGION_CHARACTER AS REGION_CHARACTER
        COMMENT = 'Characteristic description of the region'
)

METRICS (
    TELEMETRY.AVG_SOLAR_YIELD       AS AVG(TELEMETRY.SOLAR_YIELD_KW)
        COMMENT = 'Average solar generation per device in kW',
    TELEMETRY.TOTAL_SOLAR_YIELD     AS SUM(TELEMETRY.SOLAR_YIELD_KW)
        COMMENT = 'Total solar generation in kWh',
    TELEMETRY.AVG_BATTERY_SOC       AS AVG(TELEMETRY.BATTERY_SOC_PCT)
        COMMENT = 'Average battery state of charge in percent',
    TELEMETRY.AVG_HEATPUMP          AS AVG(TELEMETRY.HEATPUMP_CONSUMPTION_KW)
        COMMENT = 'Average heat pump consumption in kW',
    TELEMETRY.TOTAL_GRID_IMPORT     AS SUM(TELEMETRY.GRID_IMPORT_KW)
        COMMENT = 'Total power imported from grid in kWh',
    TELEMETRY.TOTAL_GRID_EXPORT     AS SUM(TELEMETRY.GRID_EXPORT_KW)
        COMMENT = 'Total power exported to grid in kWh',
    TELEMETRY.NET_GRID_BALANCE      AS SUM(TELEMETRY.GRID_IMPORT_KW) - SUM(TELEMETRY.GRID_EXPORT_KW)
        COMMENT = 'Net grid balance in kWh: positive means net consumer, negative means net producer',
    TELEMETRY.READING_COUNT         AS COUNT(TELEMETRY.TS)
        COMMENT = 'Number of telemetry readings',

    PRICE_OPT.TOTAL_VPP_MARGIN      AS SUM(PRICE_OPT.NET_MARGIN_EUR)
        COMMENT = 'Total VPP net margin (export revenue minus import cost) in EUR',
    PRICE_OPT.TOTAL_CUSTOMER_MARGIN  AS SUM(PRICE_OPT.CUSTOMER_MARGIN_EUR)
        COMMENT = 'Total customer share of VPP margin (70 percent) in EUR',
    PRICE_OPT.TOTAL_EPOWER_MARGIN    AS SUM(PRICE_OPT.EPOWER_MARGIN_EUR)
        COMMENT = 'Total EPOWER share of VPP margin (30 percent) in EUR',
    PRICE_OPT.TOTAL_IMPORT_COST      AS SUM(PRICE_OPT.IMPORT_COST_EUR)
        COMMENT = 'Total cost of grid imports in EUR',
    PRICE_OPT.TOTAL_EXPORT_REVENUE   AS SUM(PRICE_OPT.EXPORT_REVENUE_EUR)
        COMMENT = 'Total revenue from grid exports in EUR',
    PRICE_OPT.AVG_PRICE              AS AVG(PRICE_OPT.PRICE_EUR_MWH)
        COMMENT = 'Average day-ahead electricity price in EUR per MWh',
    PRICE_OPT.ACTIVE_VPP_CUSTOMERS   AS COUNT(DISTINCT PRICE_OPT.CUSTOMER_KEY)
        COMMENT = 'Number of distinct active VPP customers'
)

COMMENT = 'VPP (Virtual Power Plant) semantic view covering device telemetry, price optimization, battery dispatch actions, and financial margins. Grid columns: grid_import_kw is power drawn from grid (always >= 0), grid_export_kw is power fed to grid (always >= 0). Sign convention: positive net_grid_balance means the fleet is a net consumer.'
