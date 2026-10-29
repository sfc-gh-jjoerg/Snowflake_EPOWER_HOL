SELECT
    DATE_TRUNC('day', o.hour)::DATE AS day,
    o.region,
    cm.cluster_id,
    c.customer_type,
    o.battery_action,
    COUNT(*) AS action_count,
    SUM(o.total_import_kwh) AS total_import_kwh,
    SUM(o.total_export_kwh) AS total_export_kwh,
    SUM(o.import_cost_eur) AS total_import_cost_eur,
    SUM(o.export_revenue_eur) AS total_export_revenue_eur,
    SUM(o.net_margin_eur) AS total_net_margin_eur,
    SUM(o.customer_margin_eur) AS total_customer_margin_eur,
    SUM(o.epower_margin_eur) AS total_epower_margin_eur
FROM {{ ref('mart_vpp_price_optimization') }} o
JOIN {{ source('epower_gold', 'customer_dim') }} c ON o.customer_key = c.customer_key
JOIN {{ ref('city_cluster_map') }} cm ON o.city = cm.city AND o.region = cm.region
GROUP BY 1, 2, 3, 4, 5
