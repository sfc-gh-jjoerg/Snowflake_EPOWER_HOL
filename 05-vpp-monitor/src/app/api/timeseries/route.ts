import { NextRequest, NextResponse } from 'next/server';
import { executeQuery } from '@/lib/snowflake';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const region = searchParams.get('region');
  const cluster = searchParams.get('cluster');
  const from = searchParams.get('from');
  const to = searchParams.get('to');
  const granularity = searchParams.get('granularity') || 'daily';

  let sql: string;

  if (granularity === 'hourly') {
    sql = `
      SELECT
        HOUR AS time,
        REGION,
        CLUSTER_ID,
        ACTIVE_VPP_DEVICES,
        AVG_BATTERY_SOC_PCT,
        AVG_SOLAR_YIELD_KW,
        NET_GRID_KW,
        PRICE_EUR_MWH
      FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES
      WHERE 1=1
    `;
  } else {
    sql = `
      SELECT
        DATE_TRUNC('day', HOUR)::DATE AS time,
        REGION,
        AVG(ACTIVE_VPP_DEVICES) AS ACTIVE_VPP_DEVICES,
        AVG(AVG_BATTERY_SOC_PCT) AS AVG_BATTERY_SOC_PCT,
        AVG(AVG_SOLAR_YIELD_KW) AS AVG_SOLAR_YIELD_KW,
        SUM(NET_GRID_KW) AS NET_GRID_KW,
        AVG(PRICE_EUR_MWH) AS PRICE_EUR_MWH
      FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES
      WHERE 1=1
    `;
  }

  const conditions: string[] = [];

  if (region) {
    const regions = region.split(',').map(r => `'${r.trim()}'`).join(',');
    conditions.push(`REGION IN (${regions})`);
  }
  if (cluster) {
    const clusters = cluster.split(',').map(c => `'${c.trim()}'`).join(',');
    conditions.push(`CLUSTER_ID IN (${clusters})`);
  }
  if (from) {
    conditions.push(`HOUR >= '${from}'`);
  }
  if (to) {
    conditions.push(`HOUR <= '${to} 23:59:59'`);
  }

  if (conditions.length > 0) {
    sql += ' AND ' + conditions.join(' AND ');
  }

  if (granularity !== 'hourly') {
    sql += ' GROUP BY 1, 2';
  }

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
