SELECT
    d.customer_key,
    c.customer_name,
    c.city,
    c.state AS region,
    c.cluster_id,
    c.customer_type,
    d.gateway_id,
    d.has_solar,
    d.has_battery,
    d.has_heatpump,
    d.is_vpp_enrolled,
    d.enrollment_date
FROM {{ source('epower_bronze', 'epulse_devices') }} d
INNER JOIN {{ source('epower_gold', 'customer_dim') }} c 
    ON d.customer_key = c.customer_key
