{{
    config(
        materialized='incremental',
        unique_key=['hour', 'customer_key'],
        on_schema_change='sync_all_columns'
    )
}}

WITH telemetry AS (
    SELECT
        DATE_TRUNC('HOUR', ts) AS hour,
        customer_key,
        customer_name,
        city,
        region,
        cluster_id,
        is_vpp_enrolled,
        AVG(solar_yield_kw) AS avg_solar_kw,
        AVG(battery_soc_pct) AS avg_battery_soc_pct,
        AVG(heatpump_consumption_kw) AS avg_heatpump_kw,
        AVG(grid_import_export_kw) AS avg_grid_kw,
        SUM(CASE WHEN grid_import_export_kw > 0 THEN grid_import_export_kw ELSE 0 END) AS total_import_kwh,
        SUM(CASE WHEN grid_import_export_kw < 0 THEN ABS(grid_import_export_kw) ELSE 0 END) AS total_export_kwh
    FROM {{ ref('fct_epulse_telemetry') }}
    WHERE is_vpp_enrolled = TRUE
    {% if is_incremental() %}
        AND DATE_TRUNC('HOUR', ts) > (SELECT MAX(hour) FROM {{ this }})
    {% endif %}
    GROUP BY 1, 2, 3, 4, 5, 6, 7
),

prices AS (
    SELECT
        hour,
        price_eur_mwh,
        price_eur_kwh
    FROM {{ ref('mart_day_ahead_prices') }}
),

price_bands AS (
    SELECT
        APPROX_PERCENTILE(price_eur_mwh, 0.25) AS p25,
        APPROX_PERCENTILE(price_eur_mwh, 0.75) AS p75,
        AVG(price_eur_mwh) AS avg_price
    FROM prices
),

joined AS (
    SELECT
        t.hour,
        t.customer_key,
        t.customer_name,
        t.city,
        t.region,
        t.cluster_id,
        t.avg_solar_kw,
        t.avg_battery_soc_pct,
        t.avg_heatpump_kw,
        t.avg_grid_kw,
        t.total_import_kwh,
        t.total_export_kwh,
        p.price_eur_mwh,
        p.price_eur_kwh,
        CASE
            WHEN p.price_eur_mwh IS NULL THEN 'NO_PRICE_DATA'
            WHEN p.price_eur_mwh < 0 THEN 'NEGATIVE'
            WHEN p.price_eur_mwh < pb.p25 THEN 'LOW'
            WHEN p.price_eur_mwh > pb.p75 THEN 'HIGH'
            ELSE 'MEDIUM'
        END AS price_zone,
        CASE
            WHEN p.price_eur_mwh IS NULL THEN 'SELF_CONSUME'
            WHEN p.price_eur_mwh < 0 THEN 'MAX_CHARGE'
            WHEN p.price_eur_mwh < pb.p25 THEN 'CHARGE'
            WHEN p.price_eur_mwh > pb.p75 THEN 'DISCHARGE'
            ELSE 'SELF_CONSUME'
        END AS battery_action,
        ROUND(t.total_import_kwh * COALESCE(p.price_eur_kwh, 0), 4) AS import_cost_eur,
        ROUND(t.total_export_kwh * COALESCE(p.price_eur_kwh, 0), 4) AS export_revenue_eur,
        ROUND(t.total_export_kwh * COALESCE(p.price_eur_kwh, 0)
            - t.total_import_kwh * COALESCE(p.price_eur_kwh, 0), 4) AS net_margin_eur,
        ROUND((t.total_export_kwh * COALESCE(p.price_eur_kwh, 0)
            - t.total_import_kwh * COALESCE(p.price_eur_kwh, 0)) * 0.70, 4) AS customer_margin_eur,
        ROUND((t.total_export_kwh * COALESCE(p.price_eur_kwh, 0)
            - t.total_import_kwh * COALESCE(p.price_eur_kwh, 0)) * 0.30, 4) AS epower_margin_eur
    FROM telemetry t
    LEFT JOIN prices p ON t.hour = p.hour
    CROSS JOIN price_bands pb
)

SELECT * FROM joined
