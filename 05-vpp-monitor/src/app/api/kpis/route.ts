import { NextRequest, NextResponse } from 'next/server';
import { executeQuery } from '@/lib/snowflake';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const region = searchParams.get('region');
  const cluster = searchParams.get('cluster');
  const customerType = searchParams.get('type');
  const from = searchParams.get('from');
  const to = searchParams.get('to');

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

  const conditions: string[] = [];

  if (region) {
    const regions = region.split(',').map(r => `'${r.trim()}'`).join(',');
    conditions.push(`REGION IN (${regions})`);
  }
  if (cluster) {
    const clusters = cluster.split(',').map(c => `'${c.trim()}'`).join(',');
    conditions.push(`CLUSTER_ID IN (${clusters})`);
  }
  if (customerType) {
    const types = customerType.split(',').map(t => `'${t.trim()}'`).join(',');
    conditions.push(`CUSTOMER_TYPE IN (${types})`);
  }
  if (from) {
    conditions.push(`DAY >= '${from}'`);
  }
  if (to) {
    conditions.push(`DAY <= '${to}'`);
  }

  if (conditions.length > 0) {
    sql += ' AND ' + conditions.join(' AND ');
  }

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
