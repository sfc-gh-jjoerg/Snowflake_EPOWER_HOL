SELECT
    t.ts,
    t.gateway_id,
    t.customer_key,
    d.customer_name,
    d.city,
    d.region,
    d.cluster_id,
    d.customer_type,
    d.is_vpp_enrolled,
    t.solar_yield_kw,
    t.battery_soc_pct,
    t.heatpump_consumption_kw,
    t.grid_import_export_kw
FROM {{ source('epower_bronze', 'raw_epulse_iot_telemetry') }} t
INNER JOIN {{ ref('stg_devices') }} d
    ON t.customer_key = d.customer_key
