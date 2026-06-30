import { NextRequest, NextResponse } from 'next/server';
import { executeQuery } from '@/lib/snowflake';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const hour = searchParams.get('hour'); // ISO timestamp e.g. "2025-06-20T14:00:00"

  let sql = `
    SELECT
      CLUSTER_ID,
      CLUSTER_NAME,
      COMPASS_REGION,
      ACTIVE_DEVICES,
      AVG_SOC_PCT,
      AVG_SOLAR_KW,
      TOTAL_IMPORT_KWH,
      TOTAL_EXPORT_KWH,
      NET_FLOW_KWH,
      AVG_PRICE_EUR_MWH
    FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP
  `;

  if (hour) {
    sql += ` WHERE HOUR = '${hour}'`;
  } else {
    sql += ` WHERE HOUR = (SELECT MAX(HOUR) FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP)`;
  }

  sql += ` ORDER BY CLUSTER_ID`;

  try {
    const result = await executeQuery(sql);
    return NextResponse.json(result.rows || []);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Query failed' },
      { status: 500 }
    );
  }
}
