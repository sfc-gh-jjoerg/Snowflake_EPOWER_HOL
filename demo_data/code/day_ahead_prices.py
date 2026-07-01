"""
EPOWER Day-Ahead Electricity Prices — Snowflake Stored Procedure Handlers

Fetches day-ahead electricity prices from the energy-charts.info API (EPEX Spot DE-LU).
Two entry points:
  - fetch_day_ahead_prices(session, target_date): Single day fetch (idempotent)
  - backfill_day_ahead_prices(session): Bulk 60-day backfill with delivery-day bucketing

Data is stored in RAW_DAY_AHEAD_PRICES (VARIANT) as one row per delivery day,
containing 96 price points (15-min intervals) in EUR/MWh.

Usage:
  Uploaded to @EPOWER_OPS.EPOWER_STAGE/code/ and referenced via IMPORTS:
    CALL EPOWER_DEMO.EPOWER_OPS.FETCH_DAY_AHEAD_PRICES('2025-01-15');
    CALL EPOWER_DEMO.EPOWER_OPS.BACKFILL_DAY_AHEAD_PRICES();
"""

import requests
import json
from datetime import date, timedelta, datetime, timezone

API_URL = "https://api.energy-charts.info/price"
BZN = "DE-LU"
TARGET_TABLE = "EPOWER_DEMO.EPOWER_BRONZE.RAW_DAY_AHEAD_PRICES"


def fetch_day_ahead_prices(session, target_date):
    """Fetch prices for a single date. Idempotent — skips if data already exists."""
    td = target_date if isinstance(target_date, date) else date.fromisoformat(str(target_date)[:10])

    existing = session.sql(
        f"SELECT COUNT(*) AS cnt FROM {TARGET_TABLE} WHERE fetch_date = '{td}'"
    ).collect()
    if existing[0]['CNT'] > 0:
        return f"Skipped: Data for {td} already exists"

    params = {"bzn": BZN, "start": td.isoformat()}

    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        json_str = json.dumps(data).replace("'", "''")
        session.sql(
            f"INSERT INTO {TARGET_TABLE} (fetch_date, raw_data) "
            f"SELECT '{td}', PARSE_JSON('{json_str}')"
        ).collect()

        record_count = len(data.get('unix_seconds', []))
        return f"Success: Fetched {record_count} price records for {td}"

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def backfill_day_ahead_prices(session):
    """Backfill 60 days using a single bulk API call, splitting by CET delivery day.

    Delivery day alignment: CET 22:00 (day-1) to CET 21:45 (day) per EPEX convention.
    Idempotent — skips dates that already exist.
    """
    today = date.today()
    start_date = today - timedelta(days=59)

    # Find which days are missing
    existing_rows = session.sql(
        f"SELECT DISTINCT fetch_date FROM {TARGET_TABLE} "
        f"WHERE fetch_date BETWEEN '{start_date}' AND '{today}'"
    ).collect()
    existing_dates = {row['FETCH_DATE'] for row in existing_rows}

    all_dates = {start_date + timedelta(days=i) for i in range(60)}
    missing_dates = sorted(all_dates - existing_dates)

    if not missing_dates:
        return f"Backfill skipped: all {len(all_dates)} days already exist ({start_date} to {today})"

    # Single bulk API call for the full range
    params = {"bzn": BZN, "start": missing_dates[0].isoformat(), "end": missing_dates[-1].isoformat()}

    try:
        response = requests.get(API_URL, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"Error fetching data: {str(e)}"

    unix_seconds = data.get('unix_seconds', [])
    prices = data.get('price', [])
    if not unix_seconds:
        return "Error: API returned no data"

    # Bucket timestamps into delivery days (CET-aligned)
    from zoneinfo import ZoneInfo
    cet = ZoneInfo('Europe/Berlin')

    day_buckets = {}
    for i, ts in enumerate(unix_seconds):
        dt_cet = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(cet)
        delivery_day = dt_cet.date() + timedelta(days=1) if dt_cet.hour >= 22 else dt_cet.date()
        if delivery_day not in day_buckets:
            day_buckets[delivery_day] = {'unix_seconds': [], 'price': []}
        day_buckets[delivery_day]['unix_seconds'].append(ts)
        day_buckets[delivery_day]['price'].append(prices[i] if i < len(prices) else None)

    # Insert each delivery day as a separate row
    inserted = 0
    skipped = 0
    errors = []

    for day_date in sorted(day_buckets.keys()):
        if day_date in existing_dates:
            skipped += 1
            continue

        day_data = {
            'license_info': data.get('license_info', ''),
            'unix_seconds': day_buckets[day_date]['unix_seconds'],
            'price': day_buckets[day_date]['price'],
            'unit': data.get('unit', 'EUR/MWh'),
            'deprecated': data.get('deprecated', False)
        }

        try:
            json_str = json.dumps(day_data).replace("'", "''")
            session.sql(
                f"INSERT INTO {TARGET_TABLE} (fetch_date, raw_data) "
                f"SELECT '{day_date}', PARSE_JSON('{json_str}')"
            ).collect()
            inserted += 1
        except Exception as e:
            errors.append(f"{day_date}: {str(e)}")

    result = f"Backfill complete: {inserted} days inserted, {skipped} skipped ({start_date} to {today})"
    if errors:
        result += f", {len(errors)} errors: " + "; ".join(errors[:3])
    return result
