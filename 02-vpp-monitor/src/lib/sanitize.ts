const VALID_REGIONS = new Set(['North', 'South', 'East', 'West']);

const VALID_CLUSTERS = new Set([
  'freiburg_oberrhein', 'bavaria_south', 'munich_metro', 'stuttgart_metro',
  'nuernberg_franken', 'frankfurt_main', 'koeln_bonn', 'rhine_ruhr',
  'berlin_metro', 'leipzig_halle', 'saxony_east', 'hamburg_metro',
  'bremen_weser', 'lower_saxony',
]);

const VALID_CUSTOMER_TYPES = new Set(['Privatkunde', 'Kleingewerbe', 'Gewerbekunde']);

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

export function sanitizeList(raw: string, allowed: Set<string>): string[] {
  return raw.split(',').map(s => s.trim()).filter(s => allowed.has(s));
}

export function sanitizeRegions(raw: string): string[] {
  return sanitizeList(raw, VALID_REGIONS);
}

export function sanitizeClusters(raw: string): string[] {
  return sanitizeList(raw, VALID_CLUSTERS);
}

export function sanitizeCustomerTypes(raw: string): string[] {
  return sanitizeList(raw, VALID_CUSTOMER_TYPES);
}

export function sanitizeDate(raw: string): string | null {
  return DATE_RE.test(raw) ? raw : null;
}

export function sqlInList(values: string[]): string {
  return values.map(v => `'${v}'`).join(',');
}
