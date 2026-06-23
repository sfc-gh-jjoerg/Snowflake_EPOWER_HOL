SELECT
    DATE_TRUNC('HOUR', ts)          AS hour,
    region,
    cluster_id,
    COUNT(DISTINCT customer_key)    AS active_vpp_devices,
    ROUND(SUM(battery_soc_pct), 1)  AS total_battery_soc,
    ROUND(AVG(battery_soc_pct), 1)  AS avg_battery_soc_pct,
    ROUND(SUM(solar_yield_kw), 2)   AS total_solar_yield_kw,
    ROUND(AVG(solar_yield_kw), 2)   AS avg_solar_yield_kw,
    ROUND(SUM(grid_import_export_kw), 2) AS net_grid_kw
FROM {{ ref('fct_epulse_telemetry') }}
WHERE is_vpp_enrolled = TRUE
GROUP BY DATE_TRUNC('HOUR', ts), region, cluster_id
