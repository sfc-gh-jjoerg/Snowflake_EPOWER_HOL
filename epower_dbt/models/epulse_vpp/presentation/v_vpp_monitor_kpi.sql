SELECT
    DATE_TRUNC('day', o.hour)::DATE AS day,
    o.region,
    cm.cluster_id,
    c.customer_type,
    COUNT(DISTINCT o.customer_key) AS active_vpp_devices,
    AVG(o.avg_battery_soc_pct) AS avg_battery_soc_pct,
    AVG(o.avg_solar_kw) AS avg_solar_kw,
    SUM(o.total_import_kwh) - SUM(o.total_export_kwh) AS net_grid_kwh,
    AVG(o.price_eur_mwh) AS avg_price_eur_mwh,
    SUM(o.customer_margin_eur) AS total_customer_margin_eur,
    SUM(o.epower_margin_eur) AS total_epower_margin_eur,
    SUM(o.net_margin_eur) AS total_net_margin_eur
FROM {{ ref('mart_vpp_price_optimization') }} o
JOIN {{ source('epower_gold', 'customer_dim') }} c ON o.customer_key = c.customer_key
JOIN {{ ref('city_cluster_map') }} cm ON o.city = cm.city AND o.region = cm.region
GROUP BY 1, 2, 3, 4
