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
    TELEMETRY.SOLAR_YIELD_KW
        WITH DESCRIPTION = 'Solar generation in kW per device per hour',
    TELEMETRY.BATTERY_SOC_PCT
        WITH DESCRIPTION = 'Battery state of charge 0-100 percent',
    TELEMETRY.HEATPUMP_CONSUMPTION_KW
        WITH DESCRIPTION = 'Heat pump power draw in kW',
    TELEMETRY.GRID_IMPORT_KW
        WITH DESCRIPTION = 'Power drawn FROM grid in kW (always >= 0, high when charging from cheap grid power)',
    TELEMETRY.GRID_EXPORT_KW
        WITH DESCRIPTION = 'Power fed TO grid in kW (always >= 0, high when discharging during expensive hours)',

    PRICE_OPT.TOTAL_IMPORT_KWH
        WITH DESCRIPTION = 'Total energy imported from grid in kWh for this customer-hour',
    PRICE_OPT.TOTAL_EXPORT_KWH
        WITH DESCRIPTION = 'Total energy exported to grid in kWh for this customer-hour',
    PRICE_OPT.PRICE_EUR_MWH
        WITH DESCRIPTION = 'Day-ahead electricity price in EUR per MWh',
    PRICE_OPT.IMPORT_COST_EUR
        WITH DESCRIPTION = 'Cost of grid import for this customer-hour in EUR',
    PRICE_OPT.EXPORT_REVENUE_EUR
        WITH DESCRIPTION = 'Revenue from grid export for this customer-hour in EUR',
    PRICE_OPT.NET_MARGIN_EUR
        WITH DESCRIPTION = 'Net margin (export revenue minus import cost) in EUR',
    PRICE_OPT.CUSTOMER_MARGIN_EUR
        WITH DESCRIPTION = 'Customer share of VPP margin (70 percent) in EUR',
    PRICE_OPT.EPOWER_MARGIN_EUR
        WITH DESCRIPTION = 'EPOWER share of VPP margin (30 percent) in EUR'
)

DIMENSIONS (
    TELEMETRY.TS         WITH DESCRIPTION = 'Telemetry timestamp (15-min intervals)',
    TELEMETRY.GATEWAY_ID WITH DESCRIPTION = 'IoT gateway device identifier',
    TELEMETRY.CUSTOMER_KEY,
    TELEMETRY.CUSTOMER_NAME,
    TELEMETRY.CITY,
    TELEMETRY.REGION     WITH DESCRIPTION = 'German region: North, South, East, or West',
    TELEMETRY.CLUSTER_ID WITH DESCRIPTION = 'VPP geographic cluster identifier',
    TELEMETRY.CUSTOMER_TYPE,
    TELEMETRY.IS_VPP_ENROLLED WITH DESCRIPTION = 'True if customer has battery and is enrolled in VPP program',

    PRICE_OPT.HOUR       WITH DESCRIPTION = 'Hour timestamp for price optimization',
    PRICE_OPT.PRICE_ZONE WITH DESCRIPTION = 'Price classification: NEGATIVE, LOW, MEDIUM, HIGH, or NO_PRICE_DATA',
    PRICE_OPT.BATTERY_ACTION WITH DESCRIPTION = 'VPP strategy action: MAX_CHARGE, CHARGE, DISCHARGE, or SELF_CONSUME',

    CLUSTER.CLUSTER_NAME WITH DESCRIPTION = 'Human-readable cluster name',
    CLUSTER.COMPASS_REGION WITH DESCRIPTION = 'Compass direction region grouping',
    CLUSTER.REGION_CHARACTER WITH DESCRIPTION = 'Characteristic description of the region'
)

METRICS (
    TELEMETRY.AVG_SOLAR_YIELD       AS AVG(TELEMETRY.SOLAR_YIELD_KW)
        WITH DESCRIPTION = 'Average solar generation per device in kW',
    TELEMETRY.TOTAL_SOLAR_YIELD     AS SUM(TELEMETRY.SOLAR_YIELD_KW)
        WITH DESCRIPTION = 'Total solar generation in kWh',
    TELEMETRY.AVG_BATTERY_SOC       AS AVG(TELEMETRY.BATTERY_SOC_PCT)
        WITH DESCRIPTION = 'Average battery state of charge in percent',
    TELEMETRY.AVG_HEATPUMP          AS AVG(TELEMETRY.HEATPUMP_CONSUMPTION_KW)
        WITH DESCRIPTION = 'Average heat pump consumption in kW',
    TELEMETRY.TOTAL_GRID_IMPORT     AS SUM(TELEMETRY.GRID_IMPORT_KW)
        WITH DESCRIPTION = 'Total power imported from grid in kWh',
    TELEMETRY.TOTAL_GRID_EXPORT     AS SUM(TELEMETRY.GRID_EXPORT_KW)
        WITH DESCRIPTION = 'Total power exported to grid in kWh',
    TELEMETRY.NET_GRID_BALANCE      AS SUM(TELEMETRY.GRID_IMPORT_KW) - SUM(TELEMETRY.GRID_EXPORT_KW)
        WITH DESCRIPTION = 'Net grid balance in kWh: positive means net consumer, negative means net producer',
    TELEMETRY.READING_COUNT         AS COUNT(TELEMETRY.TS)
        WITH DESCRIPTION = 'Number of telemetry readings',

    PRICE_OPT.TOTAL_VPP_MARGIN      AS SUM(PRICE_OPT.NET_MARGIN_EUR)
        WITH DESCRIPTION = 'Total VPP net margin (export revenue minus import cost) in EUR',
    PRICE_OPT.TOTAL_CUSTOMER_MARGIN  AS SUM(PRICE_OPT.CUSTOMER_MARGIN_EUR)
        WITH DESCRIPTION = 'Total customer share of VPP margin (70 percent) in EUR',
    PRICE_OPT.TOTAL_EPOWER_MARGIN    AS SUM(PRICE_OPT.EPOWER_MARGIN_EUR)
        WITH DESCRIPTION = 'Total EPOWER share of VPP margin (30 percent) in EUR',
    PRICE_OPT.TOTAL_IMPORT_COST      AS SUM(PRICE_OPT.IMPORT_COST_EUR)
        WITH DESCRIPTION = 'Total cost of grid imports in EUR',
    PRICE_OPT.TOTAL_EXPORT_REVENUE   AS SUM(PRICE_OPT.EXPORT_REVENUE_EUR)
        WITH DESCRIPTION = 'Total revenue from grid exports in EUR',
    PRICE_OPT.AVG_PRICE              AS AVG(PRICE_OPT.PRICE_EUR_MWH)
        WITH DESCRIPTION = 'Average day-ahead electricity price in EUR per MWh',
    PRICE_OPT.ACTIVE_VPP_CUSTOMERS   AS COUNT(DISTINCT PRICE_OPT.CUSTOMER_KEY)
        WITH DESCRIPTION = 'Number of distinct active VPP customers'
)

COMMENT = 'VPP (Virtual Power Plant) semantic view covering device telemetry, price optimization, battery dispatch actions, and financial margins. Grid columns: grid_import_kw is power drawn from grid (always >= 0), grid_export_kw is power fed to grid (always >= 0). Sign convention: positive net_grid_balance means the fleet is a net consumer.'
