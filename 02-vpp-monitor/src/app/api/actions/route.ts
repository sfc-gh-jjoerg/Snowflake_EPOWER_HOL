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
      DAY, REGION, CUSTOMER_TYPE, BATTERY_ACTION,
      SUM(ACTION_COUNT) AS ACTION_COUNT,
      SUM(TOTAL_CUSTOMER_MARGIN_EUR) AS CUSTOMER_MARGIN_EUR,
      SUM(TOTAL_EPOWER_MARGIN_EUR) AS EPOWER_MARGIN_EUR,
      SUM(TOTAL_NET_MARGIN_EUR) AS NET_MARGIN_EUR,
      SUM(TOTAL_IMPORT_KWH) AS IMPORT_KWH,
      SUM(TOTAL_EXPORT_KWH) AS EXPORT_KWH
    FROM EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_ACTIONS
    WHERE 1=1
  `;
  if (conditions.length > 0) sql += ' AND ' + conditions.join(' AND ');
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
