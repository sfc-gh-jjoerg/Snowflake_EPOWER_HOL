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
      DAY,
      REGION,
      CUSTOMER_TYPE,
      BATTERY_ACTION,
      SUM(ACTION_COUNT) AS ACTION_COUNT,
      SUM(TOTAL_CUSTOMER_MARGIN_EUR) AS CUSTOMER_MARGIN_EUR,
      SUM(TOTAL_EPOWER_MARGIN_EUR) AS EPOWER_MARGIN_EUR,
      SUM(TOTAL_NET_MARGIN_EUR) AS NET_MARGIN_EUR,
      SUM(TOTAL_IMPORT_KWH) AS IMPORT_KWH,
      SUM(TOTAL_EXPORT_KWH) AS EXPORT_KWH
    FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_ACTIONS
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

  sql += ' GROUP BY DAY, REGION, CUSTOMER_TYPE, BATTERY_ACTION ORDER BY DAY ASC';

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
