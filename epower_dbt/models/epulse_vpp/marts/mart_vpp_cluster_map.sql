SELECT
    hour,
    cluster_id,
    COUNT(DISTINCT customer_key) AS active_devices,
    ROUND(AVG(avg_battery_soc_pct), 1) AS avg_soc_pct,
    ROUND(AVG(avg_solar_kw), 2) AS avg_solar_kw,
    ROUND(SUM(total_import_kwh), 2) AS total_import_kwh,
    ROUND(SUM(total_export_kwh), 2) AS total_export_kwh,
    ROUND(SUM(total_import_kwh) - SUM(total_export_kwh), 2) AS net_flow_kwh,
    ROUND(AVG(price_eur_mwh), 2) AS avg_price_eur_mwh
FROM {{ ref('mart_vpp_price_optimization') }}
GROUP BY hour, cluster_id
