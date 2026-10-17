import { NextRequest, NextResponse } from 'next/server';
import { executeQuery } from '../../../lib/snowflake';
import { sanitizeRegions, sanitizeClusters, sanitizeCustomerTypes, sanitizeDate, sqlInList } from '../../../lib/sanitize';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const conditions: string[] = [];

  const region = searchParams.get('region');
  if (region) {
    const values = sanitizeRegions(region);
    if (values.length > 0) conditions.push(`REGION IN (${sqlInList(values)})`);
  }
  const cluster = searchParams.get('cluster');
  if (cluster) {
    const values = sanitizeClusters(cluster);
    if (values.length > 0) conditions.push(`CLUSTER_ID IN (${sqlInList(values)})`);
  }
  const customerType = searchParams.get('type');
  if (customerType) {
    const values = sanitizeCustomerTypes(customerType);
    if (values.length > 0) conditions.push(`CUSTOMER_TYPE IN (${sqlInList(values)})`);
  }
  const from = sanitizeDate(searchParams.get('from') || '');
  if (from) conditions.push(`DAY >= '${from}'`);
  const to = sanitizeDate(searchParams.get('to') || '');
  if (to) conditions.push(`DAY <= '${to}'`);

  let sql = `
    SELECT
      SUM(ACTIVE_VPP_DEVICES) / COUNT(DISTINCT DAY) AS avg_active_devices,
      AVG(AVG_BATTERY_SOC_PCT) AS avg_battery_soc_pct,
      AVG(AVG_SOLAR_KW) AS avg_solar_kw,
      SUM(NET_GRID_KWH) AS total_net_grid_kwh,
      AVG(AVG_PRICE_EUR_MWH) AS avg_price_eur_mwh,
      SUM(TOTAL_CUSTOMER_MARGIN_EUR) AS total_customer_margin,
      SUM(TOTAL_EPOWER_MARGIN_EUR) AS total_epower_margin,
      SUM(TOTAL_NET_MARGIN_EUR) AS total_net_margin
    FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_KPI
    WHERE 1=1
  `;
  if (conditions.length > 0) sql += ' AND ' + conditions.join(' AND ');

  try {
    const result = await executeQuery(sql);
    return NextResponse.json(result.rows[0] || {});
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Query failed' },
      { status: 500 }
    );
  }
}
