import { NextResponse } from 'next/server';
import { executeQuery } from '@/lib/snowflake';

export async function GET() {
  const sql = `
    SELECT
      MIN(HOUR)::DATE AS min_date,
      MAX(HOUR)::DATE AS max_date
    FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP
  `;

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
