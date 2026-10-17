import { NextRequest, NextResponse } from 'next/server';
import { executeQuery } from '../../../lib/snowflake';
import { sanitizeRegions, sanitizeClusters, sanitizeDate, sqlInList } from '../../../lib/sanitize';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const granularity = searchParams.get('granularity') || 'daily';
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
  const from = sanitizeDate(searchParams.get('from') || '');
  if (from) conditions.push(`HOUR >= '${from}'`);
  const to = sanitizeDate(searchParams.get('to') || '');
  if (to) conditions.push(`HOUR <= '${to} 23:59:59'`);

  let sql: string;
  if (granularity === 'hourly') {
    sql = `
      SELECT
        HOUR AS time, REGION, CLUSTER_ID,
        ACTIVE_VPP_DEVICES, AVG_BATTERY_SOC_PCT, AVG_SOLAR_YIELD_KW,
        NET_GRID_KWH, PRICE_EUR_MWH
      FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES
      WHERE 1=1
    `;
  } else {
    sql = `
      SELECT
        DATE_TRUNC('day', HOUR)::DATE AS time, REGION,
        AVG(ACTIVE_VPP_DEVICES) AS ACTIVE_VPP_DEVICES,
        AVG(AVG_BATTERY_SOC_PCT) AS AVG_BATTERY_SOC_PCT,
        AVG(AVG_SOLAR_YIELD_KW) AS AVG_SOLAR_YIELD_KW,
        SUM(NET_GRID_KWH) AS NET_GRID_KWH,
        AVG(PRICE_EUR_MWH) AS PRICE_EUR_MWH
      FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES
      WHERE 1=1
    `;
  }

  if (conditions.length > 0) sql += ' AND ' + conditions.join(' AND ');
  if (granularity !== 'hourly') sql += ' GROUP BY 1, 2';
  sql += ' ORDER BY time ASC, REGION ASC';

  try {
    const result = await executeQuery(sql);
    return NextResponse.json(result.rows);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Query failed' },
      { status: 500 }
    );
  }
}
