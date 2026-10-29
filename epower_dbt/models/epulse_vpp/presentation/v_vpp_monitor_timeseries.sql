SELECT
    o.hour,
    o.region,
    cm.cluster_id,
    COUNT(DISTINCT o.customer_key)  AS active_vpp_devices,
    ROUND(SUM(o.avg_battery_soc_pct * 1.0) / NULLIF(COUNT(*), 0), 1) AS avg_battery_soc_pct,
    ROUND(AVG(o.avg_solar_kw), 2)  AS avg_solar_yield_kw,
    ROUND(SUM(o.total_import_kwh), 2) AS total_import_kwh,
    ROUND(SUM(o.total_export_kwh), 2) AS total_export_kwh,
    ROUND(SUM(o.total_import_kwh) - SUM(o.total_export_kwh), 2) AS net_grid_kwh,
    AVG(o.price_eur_mwh)           AS price_eur_mwh
FROM {{ ref('mart_vpp_price_optimization') }} o
JOIN {{ ref('city_cluster_map') }} cm ON o.city = cm.city AND o.region = cm.region
GROUP BY o.hour, o.region, cm.cluster_id
