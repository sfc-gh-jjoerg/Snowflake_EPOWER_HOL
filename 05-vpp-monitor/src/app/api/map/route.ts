import { NextRequest, NextResponse } from 'next/server';
import { executeQuery } from '@/lib/snowflake';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const date = searchParams.get('date');   // YYYY-MM-DD
  const hour = searchParams.get('hour');   // 0-23 (used with date) or full ISO timestamp (legacy)

  let sql: string;

  if (date && hour != null) {
    // Specific hour on a specific day
    const hourNum = parseInt(hour, 10);
    sql = `
      SELECT
        CLUSTER_ID, CLUSTER_NAME, COMPASS_REGION,
        ACTIVE_DEVICES, AVG_SOC_PCT, AVG_SOLAR_KW,
        TOTAL_IMPORT_KWH, TOTAL_EXPORT_KWH, NET_FLOW_KWH, AVG_PRICE_EUR_MWH
      FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP
      WHERE HOUR = '${date}T${String(hourNum).padStart(2, '0')}:00:00'::TIMESTAMP_NTZ
      ORDER BY CLUSTER_ID
    `;
  } else if (date) {
    // Aggregate all hours of a day
    sql = `
      SELECT
        CLUSTER_ID, CLUSTER_NAME, COMPASS_REGION,
        ROUND(AVG(ACTIVE_DEVICES)) AS ACTIVE_DEVICES,
        ROUND(AVG(AVG_SOC_PCT), 1) AS AVG_SOC_PCT,
        ROUND(AVG(AVG_SOLAR_KW), 2) AS AVG_SOLAR_KW,
        ROUND(SUM(TOTAL_IMPORT_KWH), 1) AS TOTAL_IMPORT_KWH,
        ROUND(SUM(TOTAL_EXPORT_KWH), 1) AS TOTAL_EXPORT_KWH,
        ROUND(SUM(NET_FLOW_KWH), 1) AS NET_FLOW_KWH,
        ROUND(AVG(AVG_PRICE_EUR_MWH), 2) AS AVG_PRICE_EUR_MWH
      FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP
      WHERE HOUR::DATE = '${date}'
      GROUP BY CLUSTER_ID, CLUSTER_NAME, COMPASS_REGION
      ORDER BY CLUSTER_ID
    `;
  } else {
    // Default: latest hour
    sql = `
      SELECT
        CLUSTER_ID, CLUSTER_NAME, COMPASS_REGION,
        ACTIVE_DEVICES, AVG_SOC_PCT, AVG_SOLAR_KW,
        TOTAL_IMPORT_KWH, TOTAL_EXPORT_KWH, NET_FLOW_KWH, AVG_PRICE_EUR_MWH
      FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP
      WHERE HOUR = (SELECT MAX(HOUR) FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP)
      ORDER BY CLUSTER_ID
    `;
  }

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
