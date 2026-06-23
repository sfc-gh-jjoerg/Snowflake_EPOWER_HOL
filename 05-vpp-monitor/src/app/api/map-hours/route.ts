import { NextRequest, NextResponse } from 'next/server';
import { executeQuery } from '@/lib/snowflake';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const date = searchParams.get('date'); // YYYY-MM-DD

  let sql = `
    SELECT DISTINCT HOUR
    FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP
  `;

  if (date) {
    sql += ` WHERE HOUR::DATE = '${date}'`;
  } else {
    sql += ` WHERE HOUR::DATE = (SELECT MAX(HOUR)::DATE FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP)`;
  }

  sql += ` ORDER BY HOUR`;

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
