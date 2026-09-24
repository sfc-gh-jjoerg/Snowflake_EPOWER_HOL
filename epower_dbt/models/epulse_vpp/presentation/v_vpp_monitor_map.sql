SELECT
    o.hour,
    cm.cluster_id,
    cl.cluster_name,
    cl.compass_region,
    COUNT(DISTINCT o.customer_key)  AS active_devices,
    ROUND(AVG(o.avg_battery_soc_pct), 1) AS avg_soc_pct,
    ROUND(AVG(o.avg_solar_kw), 2)  AS avg_solar_kw,
    ROUND(SUM(o.total_import_kwh), 1) AS total_import_kwh,
    ROUND(SUM(o.total_export_kwh), 1) AS total_export_kwh,
    ROUND(SUM(o.total_import_kwh) - SUM(o.total_export_kwh), 1) AS net_grid_kwh,
    ROUND(AVG(o.price_eur_mwh), 2) AS avg_price_eur_mwh
FROM {{ ref('mart_vpp_price_optimization') }} o
JOIN {{ ref('city_cluster_map') }} cm ON o.city = cm.city AND o.region = cm.region
JOIN {{ source('epower_gold', 'vpp_cluster_dim') }} cl ON cm.cluster_id = cl.cluster_id
GROUP BY o.hour, cm.cluster_id, cl.cluster_name, cl.compass_region
