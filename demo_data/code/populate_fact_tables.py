"""
EPOWER Fact Table Populator — Snowflake Stored Procedure Handler

Populates all fact/transactional tables with dates anchored to CURRENT_DATE(),
ensuring temporal overlap with VPP telemetry (last 60 days).

Tables generated:
  1. sales_fact          — 80,000 contracts (today - 4 years → yesterday)
  2. customer_products   — ~71,000 product ownership records (derived from sales)
  3. billing_history     — ~530,000 monthly billing records (today - 3 years → last month)
  4. service_logs        — 10,000 customer service tickets (today - 3 years → yesterday)
  5. finance_transactions — 30,000 financial transactions (today - 4 years → yesterday)
  6. marketing_campaign_fact — 16,000 campaign metrics (today - 4 years → yesterday)
  7. hr_employee_fact    — ~7,000 HR records (hire date → today)
  8. sf_accounts         — 20,000 Salesforce accounts (from customer_dim)
  9. sf_opportunities    — 50,000 CRM opportunities (today - 5 years → yesterday)
  10. sf_contacts        — 75,000 CRM contacts (today - 5 years → yesterday)

Business rules preserved:
  - 70% of customers have solar, 70% have heat pumps, 60% overlap
  - Heat pump customers are excluded from gas contracts (except 5% migrators)
  - Billing includes seasonal patterns and product-specific consumption adjustments
  - Service tickets have realistic sentiment/priority based on description keywords

Data realism enhancements (v2):
  - Regional product specialization (South=Solar, North=HeatPump, West=Gewerbe)
  - YoY growth trend (+15%) and seasonal sales patterns
  - Segment-dependent contract values (Gewerbe >> Kleingewerbe >> Privat)
  - Realistic contracts per customer (Privat: 1-3, Kleingewerbe: 2-4, Gewerbe: 3-6)
  - Regional service clusters (East: installation complaints from fast growth)
  - Temporal service trends (winter = heat pump issues)
  - HR with stable department assignments and realistic career paths

Usage:
  This module is uploaded to @EPOWER_OPS.EPOWER_STAGE/code/ and referenced via
  IMPORTS in the CREATE PROCEDURE statement. The handler function is called by:
    CALL EPOWER_DEMO.EPOWER_OPS.POPULATE_FACT_TABLES();
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import random


def populate_fact_tables(session):
    random.seed(42)
    np.random.seed(42)

    today = date.today()
    sales_start = today - timedelta(days=4*365)
    sales_end = today - timedelta(days=1)
    billing_start_year = (today - timedelta(days=3*365)).year
    billing_end_year = today.year
    billing_end_month = today.month - 1 if today.month > 1 else 12
    billing_end_year_adj = billing_end_year if today.month > 1 else billing_end_year - 1

    NUM_CUSTOMERS = 20000
    NUM_CONTRACTS = 80000
    NUM_SERVICE_LOGS = 10000
    results = []

    customer_df = session.table("EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_DIM").to_pandas()
    product_df = session.table("EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM").to_pandas()
    employee_df = session.table("EPOWER_DEMO.EPOWER_GOLD.EMPLOYEE_DIM").to_pandas()

    # Region keys: 400=North, 401=South, 402=West, 403=East
    REGION_NORTH = 400
    REGION_SOUTH = 401
    REGION_WEST = 402
    REGION_EAST = 403

    PRODUCT_PRICING = {
        1:  {'cmin': 0,     'cmax': 0,     'omin': 900,  'omax': 1200},
        2:  {'cmin': 0,     'cmax': 0,     'omin': 1200, 'omax': 1500},
        3:  {'cmin': 0,     'cmax': 0,     'omin': 1400, 'omax': 1800},
        4:  {'cmin': 0,     'cmax': 0,     'omin': 1200, 'omax': 1800},
        5:  {'cmin': 0,     'cmax': 0,     'omin': 1800, 'omax': 2400},
        6:  {'cmin': 12000, 'cmax': 16000, 'omin': 200,  'omax': 400},
        7:  {'cmin': 16000, 'cmax': 22000, 'omin': 300,  'omax': 500},
        8:  {'cmin': 24000, 'cmax': 30000, 'omin': 400,  'omax': 600},
        9:  {'cmin': 18000, 'cmax': 24000, 'omin': 600,  'omax': 900},
        10: {'cmin': 28000, 'cmax': 35000, 'omin': 400,  'omax': 700},
        11: {'cmin': 0,     'cmax': 0,     'omin': 0,    'omax': 0},
        12: {'cmin': 399,   'cmax': 599,   'omin': 60,   'omax': 120},
        13: {'cmin': 1400,  'cmax': 1900,  'omin': 0,    'omax': 0},
        14: {'cmin': 2200,  'cmax': 3000,  'omin': 0,    'omax': 0},
        15: {'cmin': 0,     'cmax': 0,     'omin': 600,  'omax': 1200},
    }

    # Segment-specific sizing: Gewerbe buys larger installations (more units, higher project value)
    # Instead of multiplying the same product price, we model larger projects:
    # - Privatkunde: 1x base (10 kWp solar, 1 wallbox, standard HP)
    # - Kleingewerbe: 2-3x base (25 kWp solar, 2 wallboxes, larger HP)
    # - Gewerbekunde: 5-8x base (50+ kWp solar, 5 wallboxes, industrial HP)
    SEGMENT_SIZING = {
        'Privatkunde': {'capex_mult': 1.0, 'opex_mult': 1.0, 'units_mult': 1},
        'Kleingewerbe': {'capex_mult': 2.5, 'opex_mult': 1.8, 'units_mult': 3},
        'Gewerbekunde': {'capex_mult': 6.0, 'opex_mult': 3.5, 'units_mult': 8},
    }

    elec = [1, 2, 3]
    gas = [4, 5]
    sol = [6, 7, 8]
    hp = [9, 10]
    sh = [11, 12]
    ev = [13, 14, 15]

    # Customer segmentation (deterministic via seed)
    all_customers = list(range(1, NUM_CUSTOMERS + 1))
    random.shuffle(all_customers)

    cl = customer_df.set_index('CUSTOMER_KEY')

    # Regional product assignment — Solar more likely in South, HP in North
    solar_customers = set()
    hp_customers = set()
    gas_customers = set()

    for cust in all_customers:
        try:
            region = int(cl.loc[cust]['REGION_KEY'])
        except (KeyError, TypeError):
            region = REGION_WEST

        # Solar probability by region
        solar_prob = {REGION_SOUTH: 0.85, REGION_WEST: 0.70, REGION_EAST: 0.65, REGION_NORTH: 0.55}
        # Heat pump probability by region
        hp_prob = {REGION_NORTH: 0.80, REGION_EAST: 0.75, REGION_WEST: 0.68, REGION_SOUTH: 0.60}

        if random.random() < solar_prob.get(region, 0.70):
            solar_customers.add(cust)
        if random.random() < hp_prob.get(region, 0.70):
            hp_customers.add(cust)

    # Customers without heat pump get gas
    gas_customers = set(all_customers) - hp_customers

    def rd(s, e):
        return s + timedelta(days=random.randint(0, max((e - s).days, 1)))

    def rd_with_trend(s, e):
        """Generate a date with YoY growth trend — more recent dates more likely."""
        total_days = (e - s).days
        if total_days <= 0:
            return s
        # Use a power distribution: exponent > 1 skews toward recent
        r = random.random() ** 0.7  # mild bias toward recent
        return s + timedelta(days=int(r * total_days))

    def rd_seasonal_sales(s, e, product_keys):
        """Generate date with seasonality: Solar peaks Mar-Jun, HP peaks Sep-Nov."""
        import calendar
        d = rd_with_trend(s, e)
        month = d.month
        is_solar = any(pk in sol for pk in product_keys) if isinstance(product_keys, (list, set)) else product_keys in sol
        is_hp = any(pk in hp for pk in product_keys) if isinstance(product_keys, (list, set)) else product_keys in hp

        def safe_replace_month(dt, new_month):
            max_day = calendar.monthrange(dt.year, new_month)[1]
            return dt.replace(month=new_month, day=min(dt.day, max_day))

        if is_solar:
            solar_weight = {1: 0.4, 2: 0.6, 3: 0.9, 4: 1.0, 5: 1.0, 6: 0.9, 7: 0.7, 8: 0.6, 9: 0.5, 10: 0.4, 11: 0.3, 12: 0.3}
            if random.random() > solar_weight.get(month, 0.5):
                d = safe_replace_month(d, random.choice([3, 4, 5, 6]))
        elif is_hp:
            hp_weight = {1: 0.5, 2: 0.4, 3: 0.3, 4: 0.3, 5: 0.3, 6: 0.3, 7: 0.4, 8: 0.6, 9: 0.9, 10: 1.0, 11: 0.9, 12: 0.7}
            if random.random() > hp_weight.get(month, 0.5):
                d = safe_replace_month(d, random.choice([9, 10, 11]))
        return d

    def ds(d):
        return d.isoformat() if isinstance(d, date) else str(d)[:10]

    # =========================================================================
    # 1. SALES_FACT (80,000 contracts)
    # =========================================================================
    contracts = []
    cid = 1

    # Determine contracts per customer based on segment
    # Budgets are TOTAL desired contracts (including the mandatory Phase 1 contracts)
    customer_contract_budget = {}
    for cust in all_customers:
        try:
            ctype = cl.loc[cust]['CUSTOMER_TYPE']
        except (KeyError, TypeError):
            ctype = 'Privatkunde'

        if ctype == 'Gewerbekunde':
            n = random.choices([5, 6, 7, 8], weights=[0.20, 0.35, 0.30, 0.15])[0]
        elif ctype == 'Kleingewerbe':
            n = random.choices([3, 4, 5, 6], weights=[0.25, 0.40, 0.25, 0.10])[0]
        else:  # Privatkunde
            n = random.choices([2, 3, 4], weights=[0.35, 0.45, 0.20])[0]
        customer_contract_budget[cust] = n

    # Phase 1: Mandatory products (solar, hp, gas)
    for cust in solar_customers:
        c = cl.loc[cust]
        region = int(c['REGION_KEY'])
        ctype = c['CUSTOMER_TYPE']
        sizing = SEGMENT_SIZING.get(ctype, SEGMENT_SIZING['Privatkunde'])
        # South gets premium solar (product 8 more likely)
        if region == REGION_SOUTH:
            pk = random.choices(sol, weights=[0.2, 0.3, 0.5])[0]
        else:
            pk = random.choice(sol)
        p = PRODUCT_PRICING[pk]
        # CAPEX product: larger installation for Gewerbe (project value = base price * sizing)
        amt = round(random.uniform(p['cmin'], p['cmax']) * sizing['capex_mult'], 2)
        contracts.append({
            'SALE_ID': cid, 'DATE': ds(rd_seasonal_sales(sales_start, sales_end, pk)),
            'CUSTOMER_KEY': cust, 'PRODUCT_KEY': pk,
            'SALES_REP_KEY': random.randint(1, 500),
            'REGION_KEY': region,
            'VENDOR_KEY': random.randint(1, 200),
            'AMOUNT': amt, 'UNITS': sizing['units_mult']
        })
        cid += 1

    for cust in hp_customers:
        c = cl.loc[cust]
        region = int(c['REGION_KEY'])
        ctype = c['CUSTOMER_TYPE']
        sizing = SEGMENT_SIZING.get(ctype, SEGMENT_SIZING['Privatkunde'])
        # North gets premium HP (product 10 more likely)
        if region == REGION_NORTH:
            pk = random.choices(hp, weights=[0.3, 0.7])[0]
        else:
            pk = random.choice(hp)
        p = PRODUCT_PRICING[pk]
        amt = round(random.uniform(p['cmin'], p['cmax']) * sizing['capex_mult'], 2)
        contracts.append({
            'SALE_ID': cid, 'DATE': ds(rd_seasonal_sales(sales_start, sales_end, pk)),
            'CUSTOMER_KEY': cust, 'PRODUCT_KEY': pk,
            'SALES_REP_KEY': random.randint(1, 500),
            'REGION_KEY': region,
            'VENDOR_KEY': random.randint(1, 200),
            'AMOUNT': amt, 'UNITS': sizing['units_mult']
        })
        cid += 1

    for cust in gas_customers:
        c = cl.loc[cust]
        region = int(c['REGION_KEY'])
        ctype = c['CUSTOMER_TYPE']
        sizing = SEGMENT_SIZING.get(ctype, SEGMENT_SIZING['Privatkunde'])
        pk = random.choice(gas)
        p = PRODUCT_PRICING[pk]
        amt = round(random.uniform(p['omin'], p['omax']) * sizing['opex_mult'], 2)
        contracts.append({
            'SALE_ID': cid, 'DATE': ds(rd_with_trend(sales_start, sales_end)),
            'CUSTOMER_KEY': cust, 'PRODUCT_KEY': pk,
            'SALES_REP_KEY': random.randint(1, 500),
            'REGION_KEY': region,
            'VENDOR_KEY': random.randint(1, 200),
            'AMOUNT': amt, 'UNITS': random.randint(10000, 25000) * sizing['units_mult']
        })
        cid += 1

    # Phase 2: Fill remaining contracts respecting per-customer budgets
    # Count existing contracts per customer
    existing_counts = {}
    for con in contracts:
        ck = con['CUSTOMER_KEY']
        existing_counts[ck] = existing_counts.get(ck, 0) + 1

    remaining = NUM_CONTRACTS - len(contracts)
    # Weighted customer selection: customers below their budget get more contracts
    eligible = [(cust, max(customer_contract_budget[cust] - existing_counts.get(cust, 0), 0))
                for cust in all_customers]
    eligible = [(c, w) for c, w in eligible if w > 0]

    for _ in range(remaining):
        if not eligible:
            ck = random.randint(1, NUM_CUSTOMERS)
        else:
            # Weighted selection — customers needing more contracts get priority
            if random.random() < 0.7 and eligible:
                idx = random.randint(0, len(eligible) - 1)
                ck = eligible[idx][0]
                # Reduce weight
                new_w = eligible[idx][1] - 1
                if new_w <= 0:
                    eligible.pop(idx)
                else:
                    eligible[idx] = (ck, new_w)
            else:
                ck = random.randint(1, NUM_CUSTOMERS)

        c = cl.loc[ck]
        region = int(c['REGION_KEY'])
        ctype = c['CUSTOMER_TYPE']
        sizing = SEGMENT_SIZING.get(ctype, SEGMENT_SIZING['Privatkunde'])
        is_hp_cust = ck in hp_customers

        # West has more E-Mobility (urban), East has more Smart Home
        if region == REGION_WEST:
            if is_hp_cust:
                pt = random.choices(['e', 'sh', 'ev', 'e'], weights=[0.40, 0.15, 0.30, 0.15])[0]
            else:
                pt = random.choices(['e', 'g', 'sh', 'ev', 'e'], weights=[0.30, 0.20, 0.15, 0.25, 0.10])[0]
        elif region == REGION_EAST:
            if is_hp_cust:
                pt = random.choices(['e', 'sh', 'ev', 'e'], weights=[0.45, 0.30, 0.15, 0.10])[0]
            else:
                pt = random.choices(['e', 'g', 'sh', 'ev', 'e'], weights=[0.35, 0.25, 0.25, 0.08, 0.07])[0]
        else:
            if is_hp_cust:
                pt = random.choices(['e', 'sh', 'ev', 'e'], weights=[0.55, 0.20, 0.15, 0.10])[0]
            else:
                pt = random.choices(['e', 'g', 'sh', 'ev', 'e'], weights=[0.40, 0.25, 0.15, 0.12, 0.08])[0]

        if pt == 'e':
            pk = random.choice(elec)
            p = PRODUCT_PRICING[pk]
            amt = round(random.uniform(p['omin'], p['omax']) * sizing['opex_mult'], 2)
            u = int(random.gauss(3500, 1000)) * sizing['units_mult']
            u = max(u, 1500)
        elif pt == 'g':
            pk = random.choice(gas)
            p = PRODUCT_PRICING[pk]
            amt = round(random.uniform(p['omin'], p['omax']) * sizing['opex_mult'], 2)
            u = random.randint(10000, 25000) * sizing['units_mult']
        elif pt == 'sh':
            pk = random.choice(sh)
            p = PRODUCT_PRICING[pk]
            base_amt = random.uniform(p['cmin'], p['cmax']) if p['cmax'] > 0 else 0
            amt = round(base_amt * sizing['capex_mult'], 2)
            u = sizing['units_mult']
        else:
            pk = random.choice(ev)
            p = PRODUCT_PRICING[pk]
            base_amt = random.uniform(p['cmin'], p['cmax']) if p['cmax'] > 0 else random.uniform(p['omin'], p['omax'])
            amt = round(base_amt * sizing['capex_mult'], 2)
            u = sizing['units_mult']

        contracts.append({
            'SALE_ID': cid, 'DATE': ds(rd_seasonal_sales(sales_start, sales_end, pk)),
            'CUSTOMER_KEY': ck, 'PRODUCT_KEY': pk,
            'SALES_REP_KEY': random.randint(1, 500),
            'REGION_KEY': region,
            'VENDOR_KEY': random.randint(1, 200),
            'AMOUNT': round(amt, 2), 'UNITS': u
        })
        cid += 1

    sdf = pd.DataFrame(contracts)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.SALES_FACT").collect()
    session.write_pandas(sdf, "SALES_FACT", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"sales_fact: {len(sdf):,} rows")

    # =========================================================================
    # 2. CUSTOMER_PRODUCTS (derived from sales)
    # =========================================================================
    pi = product_df.set_index('PRODUCT_KEY')
    cpl = []
    cpid = 1
    cpm = {}

    for _, r in sdf.iterrows():
        ck = int(r['CUSTOMER_KEY'])
        pk = int(r['PRODUCT_KEY'])
        if ck not in cpm:
            cpm[ck] = set()
        if pk not in cpm[ck]:
            cpm[ck].add(pk)
            pinfo = pi.loc[pk]
            cpl.append({
                'CUSTOMER_PRODUCT_ID': cpid, 'CUSTOMER_KEY': ck, 'PRODUCT_KEY': pk,
                'CATEGORY_KEY': int(pinfo['CATEGORY_KEY']),
                'CATEGORY_NAME': pinfo['CATEGORY_NAME'],
                'ACQUISITION_DATE': r['DATE'],
                'STATUS': random.choices(['Active', 'Inactive'], weights=[0.95, 0.05])[0]
            })
            cpid += 1

    cpdf = pd.DataFrame(cpl)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_PRODUCTS").collect()
    session.write_pandas(cpdf, "CUSTOMER_PRODUCTS", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"customer_products: {len(cpdf):,} rows")

    hps = set(cpdf[cpdf['CATEGORY_NAME'] == 'Heat Pumps']['CUSTOMER_KEY'].unique())
    ss = set(cpdf[cpdf['CATEGORY_NAME'] == 'Solar & Storage']['CUSTOMER_KEY'].unique())
    evs = set(cpdf[cpdf['CATEGORY_NAME'] == 'E-Mobility']['CUSTOMER_KEY'].unique())

    # =========================================================================
    # 3. BILLING_HISTORY (~530,000 monthly records)
    # =========================================================================
    bill = []
    bid = 1

    for ck in range(1, min(NUM_CUSTOMERS + 1, 10001)):
        try:
            cu = cl.loc[ck]
        except KeyError:
            continue

        housing = cu['HOUSING_TYPE']
        ctype = cu['CUSTOMER_TYPE']

        # Base consumption depends on segment
        if ctype == 'Gewerbekunde':
            be = {'Einfamilienhaus': 25000, 'Reihenhaus': 20000, 'Wohnung': 15000,
                  'Mehrfamilienhaus': 18000, 'Gewerbeimmobilie': 45000}.get(housing, 30000)
            bg = {'Einfamilienhaus': 50000, 'Reihenhaus': 40000, 'Wohnung': 25000,
                  'Mehrfamilienhaus': 35000, 'Gewerbeimmobilie': 80000}.get(housing, 50000)
        elif ctype == 'Kleingewerbe':
            be = {'Einfamilienhaus': 8000, 'Reihenhaus': 7000, 'Wohnung': 5000,
                  'Mehrfamilienhaus': 6000, 'Gewerbeimmobilie': 18000}.get(housing, 8000)
            bg = {'Einfamilienhaus': 22000, 'Reihenhaus': 18000, 'Wohnung': 10000,
                  'Mehrfamilienhaus': 14000, 'Gewerbeimmobilie': 40000}.get(housing, 20000)
        else:  # Privatkunde
            be = {'Einfamilienhaus': 4200, 'Reihenhaus': 3200, 'Wohnung': 2000,
                  'Mehrfamilienhaus': 2800, 'Gewerbeimmobilie': 12000}.get(housing, 3000)
            bg = {'Einfamilienhaus': 16000, 'Reihenhaus': 12000, 'Wohnung': 6000,
                  'Mehrfamilienhaus': 10000, 'Gewerbeimmobilie': 30000}.get(housing, 15000)

        hhp = ck in hps
        hsl = ck in ss
        hev = ck in evs
        im = hhp and (hash(f"migrate_{ck}") % 100 < 5)

        if hhp and not im:
            hyr = billing_start_year + (hash(f"hp_year_{ck}") % 2)
        elif im:
            hyr = billing_end_year_adj - (hash(f"hp_mig_{ck}") % 2)
        else:
            hyr = None

        if hhp:
            be += 3500 + (hash(f"hp_kwh_{ck}") % 2000)
        if hev:
            be += 2000 + (hash(f"ev_kwh_{ck}") % 1500)
        if hsl:
            be = int(be * (0.5 + (hash(f"solar_{ck}") % 20) / 100.0))

        for yr in range(billing_start_year, billing_end_year_adj + 1):
            for mo in range(1, 13):
                if yr == billing_end_year_adj and mo > billing_end_month:
                    continue

                if hhp and not im:
                    ug = False
                elif im:
                    ug = (yr < hyr) or (yr == hyr and mo <= 6)
                else:
                    ug = True

                se = {1: 1.3, 2: 1.3, 3: 1.1, 11: 1.2, 12: 1.4, 6: 0.75, 7: 0.7, 8: 0.7}.get(mo, 1.0)
                sg = {1: 1.8, 2: 1.7, 3: 1.4, 4: 0.8, 5: 0.4, 6: 0.2, 7: 0.15, 8: 0.15, 9: 0.3, 10: 0.7, 11: 1.3, 12: 1.6}.get(mo, 1.0)

                if hhp and not ug:
                    ke = int(be / 12 * se * random.uniform(0.85, 1.15))
                else:
                    eb = be - (random.randint(3500, 5500) if hhp else 0)
                    ke = int(max(eb, 2000) / 12 * se * random.uniform(0.85, 1.15))
                kg = int(bg / 12 * sg * random.uniform(0.80, 1.20))

                bill.append({
                    'BILLING_ID': bid, 'CUSTOMER_KEY': ck,
                    'BILLING_DATE': f"{yr}-{mo:02d}-15",
                    'BILLING_TYPE': 'Electricity',
                    'CONSUMPTION_KWH': ke,
                    'AMOUNT': round(ke * random.uniform(0.30, 0.40) + 12.50, 2),
                    'PAYMENT_STATUS': random.choices(['Bezahlt', 'Offen', 'Ueberfaellig'], weights=[0.88, 0.08, 0.04])[0]
                })
                bid += 1

                if ug and kg > 50:
                    bill.append({
                        'BILLING_ID': bid, 'CUSTOMER_KEY': ck,
                        'BILLING_DATE': f"{yr}-{mo:02d}-15",
                        'BILLING_TYPE': 'Gas',
                        'CONSUMPTION_KWH': kg,
                        'AMOUNT': round(kg * random.uniform(0.09, 0.13) + 8.90, 2),
                        'PAYMENT_STATUS': random.choices(['Bezahlt', 'Offen', 'Ueberfaellig'], weights=[0.88, 0.08, 0.04])[0]
                    })
                    bid += 1

    bdf = pd.DataFrame(bill)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.BILLING_HISTORY").collect()
    session.write_pandas(bdf, "BILLING_HISTORY", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"billing_history: {len(bdf):,} rows")

    # =========================================================================
    # 4. SERVICE_LOGS (10,000 tickets)
    # =========================================================================
    ticket_types = [
        ('Smart Meter', 'Installation'), ('Rechnung', 'Abrechnung'),
        ('Waermepumpe', 'Technisch'), ('Solar', 'Technisch'),
        ('Tarif', 'Vertrag'), ('Wallbox', 'E-Mobility'),
        ('Allgemein', 'Service'), ('Speicher', 'Technisch'),
    ]
    desc_map = {
        'Smart Meter': ['Smart Meter Installation angefragt', 'Smart Meter defekt', 'Smart Meter Ablesung fehlerhaft', 'Smart Meter zeigt keine Daten', 'Smart Meter App funktioniert nicht'],
        'Rechnung': ['Rechnungsfrage', 'Unstimmigkeit in Rechnung', 'Zahlungsplan angefragt', 'Abschlag zu hoch', 'Abschlag anpassen', 'Gutschrift angefragt'],
        'Waermepumpe': ['Waermepumpe Stoerung', 'Wartung angefragt', 'Effizienz zu niedrig', 'Waermepumpe laeuft nicht', 'Geraeuschentwicklung zu hoch', 'Fehlercode E01 angezeigt'],
        'Solar': ['Solaranlage Ertrag niedrig', 'Wechselrichter Fehler', 'Monitoring nicht verfuegbar', 'Solaranlage produziert nicht', 'Einspeiseverguetung Frage'],
        'Tarif': ['Tarifwechsel angefragt', 'Kuendigung', 'Umzug melden', 'Vertragsverlaengerung', 'Preisgarantie Frage', 'Oekostrom Umstellung'],
        'Wallbox': ['Wallbox Installation angefragt', 'Wallbox defekt', 'Ladekarte Probleme', 'Wallbox laedt nicht', 'App-Verbindung unterbrochen'],
        'Allgemein': ['Allgemeine Anfrage', 'Beschwerde', 'Lob', 'Informationsanfrage', 'Kontaktdaten aendern'],
        'Speicher': ['Batteriespeicher Stoerung', 'Speicher laedt nicht', 'Kapazitaet gesunken'],
    }

    # Regional ticket type weights — East has more installation complaints (fast growth)
    region_ticket_weights = {
        REGION_EAST: {'Smart Meter': 0.20, 'Rechnung': 0.10, 'Waermepumpe': 0.15, 'Solar': 0.20, 'Tarif': 0.10, 'Wallbox': 0.05, 'Allgemein': 0.10, 'Speicher': 0.10},
        REGION_NORTH: {'Smart Meter': 0.10, 'Rechnung': 0.15, 'Waermepumpe': 0.25, 'Solar': 0.10, 'Tarif': 0.12, 'Wallbox': 0.08, 'Allgemein': 0.12, 'Speicher': 0.08},
        REGION_SOUTH: {'Smart Meter': 0.10, 'Rechnung': 0.15, 'Waermepumpe': 0.10, 'Solar': 0.25, 'Tarif': 0.12, 'Wallbox': 0.10, 'Allgemein': 0.10, 'Speicher': 0.08},
        REGION_WEST: {'Smart Meter': 0.12, 'Rechnung': 0.15, 'Waermepumpe': 0.12, 'Solar': 0.12, 'Tarif': 0.12, 'Wallbox': 0.15, 'Allgemein': 0.12, 'Speicher': 0.08},
    }

    svc_start = today - timedelta(days=3 * 365)
    svc_end = today - timedelta(days=1)
    svl = []

    for lid in range(1, NUM_SERVICE_LOGS + 1):
        # Seasonal: more tickets in winter (HP issues) and summer (solar issues)
        ld = rd(svc_start, svc_end)
        month = ld.month

        ck = random.randint(1, NUM_CUSTOMERS)
        try:
            region = int(cl.loc[ck]['REGION_KEY'])
        except (KeyError, TypeError):
            region = REGION_WEST

        # Select topic based on region weights
        weights = region_ticket_weights.get(region, region_ticket_weights[REGION_WEST])
        topics = list(weights.keys())
        topic_weights = list(weights.values())

        # Seasonal adjustment: boost HP in winter, Solar in summer
        adj_weights = list(topic_weights)
        if month in [11, 12, 1, 2]:
            hp_idx = topics.index('Waermepumpe')
            adj_weights[hp_idx] *= 1.8
        elif month in [6, 7, 8]:
            sol_idx = topics.index('Solar')
            adj_weights[sol_idx] *= 1.5

        topic = random.choices(topics, weights=adj_weights)[0]
        cat = dict(ticket_types)[topic]
        desc = random.choice(desc_map[topic])

        if 'defekt' in desc or 'Stoerung' in desc or 'Beschwerde' in desc or 'nicht' in desc:
            sent = 'Negativ'
            pri = random.choices(['Niedrig', 'Mittel', 'Hoch', 'Kritisch'], weights=[0.1, 0.3, 0.4, 0.2])[0]
        elif 'Lob' in desc:
            sent = 'Positiv'
            pri = 'Niedrig'
        else:
            sent = random.choices(['Positiv', 'Neutral', 'Negativ'], weights=[0.15, 0.65, 0.20])[0]
            pri = random.choices(['Niedrig', 'Mittel', 'Hoch', 'Kritisch'], weights=[0.3, 0.5, 0.15, 0.05])[0]

        # East region: higher negative sentiment (growing pains)
        if region == REGION_EAST and sent == 'Neutral' and random.random() < 0.25:
            sent = 'Negativ'
            pri = random.choices(['Mittel', 'Hoch', 'Kritisch'], weights=[0.4, 0.4, 0.2])[0]

        rdd = random.randint(0, 14) if pri in ['Niedrig', 'Mittel'] else random.randint(0, 7)
        svl.append({
            'LOG_ID': lid, 'CUSTOMER_KEY': ck,
            'LOG_DATE': ds(ld), 'TOPIC': topic, 'CATEGORY': cat,
            'DESCRIPTION': desc, 'SENTIMENT': sent,
            'CHANNEL': random.choice(['Telefon', 'Email', 'Chat', 'App']),
            'PRIORITY': pri,
            'RESOLUTION_DATE': ds(ld + timedelta(days=rdd)),
            'AGENT_KEY': random.randint(1, 200)
        })

    svdf = pd.DataFrame(svl)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.SERVICE_LOGS").collect()
    session.write_pandas(svdf, "SERVICE_LOGS", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"service_logs: {len(svdf):,} rows")

    # =========================================================================
    # 5. FINANCE_TRANSACTIONS (30,000 rows)
    # =========================================================================
    fin_start = today - timedelta(days=4 * 365)
    fin_end = today - timedelta(days=1)
    fl = []

    for tid in range(1, 30001):
        td = rd(fin_start, fin_end)
        ak = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
        amt = round(random.uniform(50, 5000) if ak == 1 else random.uniform(10, 2000), 2)
        aps = random.choices(['Approved', 'Pending', 'Rejected'], weights=[0.85, 0.10, 0.05])[0]
        fl.append({
            'TRANSACTION_ID': tid, 'DATE': ds(td), 'ACCOUNT_KEY': ak,
            'DEPARTMENT_KEY': random.randint(10, 40), 'VENDOR_KEY': random.randint(1, 200),
            'PRODUCT_KEY': random.randint(1, 15), 'CUSTOMER_KEY': random.randint(1, NUM_CUSTOMERS),
            'AMOUNT': amt, 'APPROVAL_STATUS': aps,
            'PROCUREMENT_METHOD': random.choice(['Vertrag', 'Ausschreibung', 'Direktvergabe']),
            'APPROVER_ID': random.randint(1, 1000) if aps != 'Pending' else None,
            'APPROVAL_DATE': ds(td + timedelta(days=random.randint(1, 7))) if aps != 'Pending' else None,
            'PURCHASE_ORDER_NUMBER': f"PO-{random.randint(100000, 999999)}" if random.random() > 0.3 else None,
            'CONTRACT_REFERENCE': f"VTR-{td.year}-{random.randint(1000, 9999)}" if random.random() > 0.4 else None
        })

    fdf = pd.DataFrame(fl)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.FINANCE_TRANSACTIONS").collect()
    session.write_pandas(fdf, "FINANCE_TRANSACTIONS", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"finance_transactions: {len(fdf):,} rows")

    # =========================================================================
    # 6. MARKETING_CAMPAIGN_FACT (16,000 rows)
    # =========================================================================
    ml = []
    for fid in range(1, 16001):
        ml.append({
            'CAMPAIGN_FACT_ID': fid, 'DATE': ds(rd(fin_start, fin_end)),
            'CAMPAIGN_KEY': random.randint(1, 100), 'PRODUCT_KEY': random.randint(1, 15),
            'CHANNEL_KEY': random.choice([600, 601, 602, 603, 604, 605]),
            'REGION_KEY': random.choice([400, 401, 402, 403]),
            'SPEND': round(random.uniform(50, 500), 2),
            'LEADS_GENERATED': random.randint(5, 100),
            'IMPRESSIONS': random.randint(100, 15000)
        })

    mdf = pd.DataFrame(ml)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.MARKETING_CAMPAIGN_FACT").collect()
    session.write_pandas(mdf, "MARKETING_CAMPAIGN_FACT", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"marketing_campaign_fact: {len(mdf):,} rows")

    # =========================================================================
    # 7. HR_EMPLOYEE_FACT (~7,000 rows)
    # =========================================================================
    hrl = []
    hid = 1

    for _, emp in employee_df.iterrows():
        ek = int(emp['EMPLOYEE_KEY'])
        try:
            hd = date.fromisoformat(str(emp['HIRE_DATE'])[:10])
        except (ValueError, TypeError):
            hd = today - timedelta(days=1000)

        # Stable department/job based on employee key (not random each snapshot)
        dept_key = 10 + (hash(f"dept_{ek}") % 31)
        job_key = 800 + (hash(f"job_{ek}") % 16)
        loc_key = 900 + (hash(f"loc_{ek}") % 12)

        sal = 35000 + (hash(f"salary_{ek}") % 50000)
        lft = (hash(f"left_{ek}") % 100) < 15
        pl = hd + timedelta(days=180)
        ld = None
        if lft and pl < today:
            lr = (today - pl).days
            if lr > 0:
                ld = pl + timedelta(days=hash(f"leave_day_{ek}") % lr)

        cd = hd
        promotion_count = 0
        while cd < today:
            att = 1 if ld and cd >= ld else 0
            hrl.append({
                'HR_FACT_ID': hid, 'DATE': ds(cd), 'EMPLOYEE_KEY': ek,
                'DEPARTMENT_KEY': dept_key,
                'JOB_KEY': job_key + promotion_count,  # Advance job level on promotion
                'LOCATION_KEY': loc_key,
                'SALARY': sal, 'ATTRITION_FLAG': att
            })
            hid += 1
            if att == 1:
                break
            cd += timedelta(days=random.randint(180, 360))
            # Promotion: 15% chance per period (realistic career progression)
            if random.random() < 0.15:
                sal = int(sal * random.uniform(1.05, 1.15))
                promotion_count = min(promotion_count + 1, 5)
            elif random.random() < 0.08:
                sal = int(sal * random.uniform(1.02, 1.04))  # Cost of living raise

    hdf = pd.DataFrame(hrl)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.HR_EMPLOYEE_FACT").collect()
    session.write_pandas(hdf, "HR_EMPLOYEE_FACT", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"hr_employee_fact: {len(hdf):,} rows")

    # =========================================================================
    # 8. SF_ACCOUNTS (20,000 rows)
    # =========================================================================
    sal_list = []
    for _, c in customer_df.iterrows():
        ck = int(c['CUSTOMER_KEY'])
        sal_list.append({
            'ACCOUNT_ID': f"ACC{ck:06d}", 'ACCOUNT_NAME': c['CUSTOMER_NAME'],
            'CUSTOMER_KEY': ck, 'INDUSTRY': c['CUSTOMER_TYPE'], 'VERTICAL': 'Energy',
            'BILLING_STREET': c['ADDRESS'], 'BILLING_CITY': c['CITY'],
            'BILLING_STATE': c['STATE'], 'BILLING_POSTAL_CODE': c['ZIP'],
            'ACCOUNT_TYPE': random.choice(['Kunde', 'Interessent', 'Partner']),
            'ANNUAL_REVENUE': random.randint(0, 500000) if c['CUSTOMER_TYPE'] == 'Privatkunde' else random.randint(100000, 5000000),
            'EMPLOYEES': 1 if c['CUSTOMER_TYPE'] == 'Privatkunde' else random.choice([5, 10, 25, 50, 100]),
            'CREATED_DATE': ds(rd(today - timedelta(days=5 * 365), today - timedelta(days=2 * 365)))
        })

    sadf = pd.DataFrame(sal_list)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.SF_ACCOUNTS").collect()
    session.write_pandas(sadf, "SF_ACCOUNTS", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"sf_accounts: {len(sadf):,} rows")

    # =========================================================================
    # 9. SF_OPPORTUNITIES (50,000 rows)
    # =========================================================================
    stages = ['Closed Won', 'Closed Lost', 'Verhandlung', 'Angebot', 'Qualifizierung', 'Interessent']
    leads = ['Webseite', 'Empfehlung', 'Messe', 'Telefonakquise', 'Partner', 'Social Media']
    opp_start = today - timedelta(days=5 * 365)
    opp_end = today - timedelta(days=1)
    opl = []

    for i in range(1, 50001):
        cd = rd(opp_start, opp_end)
        st = random.choices(stages, weights=[0.25, 0.15, 0.15, 0.20, 0.15, 0.10])[0]
        pb = 100.0 if st == 'Closed Won' else (0.0 if st == 'Closed Lost' else random.uniform(10, 80))
        opl.append({
            'OPPORTUNITY_ID': f"OPP{i:08d}",
            'SALE_ID': i if st == 'Closed Won' and i <= NUM_CONTRACTS else None,
            'ACCOUNT_ID': f"ACC{random.randint(1, NUM_CUSTOMERS):06d}",
            'OPPORTUNITY_NAME': f"Opportunity {i}", 'STAGE_NAME': st,
            'AMOUNT': round(random.uniform(500, 50000), 2),
            'PROBABILITY': round(pb, 1),
            'CLOSE_DATE': ds(cd + timedelta(days=random.randint(30, 180))),
            'CREATED_DATE': ds(cd),
            'LEAD_SOURCE': random.choice(leads),
            'TYPE': random.choice(['Neukunde', 'Bestandskunde - Upgrade', 'Bestandskunde - Zusatzprodukt']),
            'CAMPAIGN_ID': random.randint(1, 16000) if random.random() > 0.3 else None
        })

    odf = pd.DataFrame(opl)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.SF_OPPORTUNITIES").collect()
    session.write_pandas(odf, "SF_OPPORTUNITIES", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"sf_opportunities: {len(odf):,} rows")

    # =========================================================================
    # 10. SF_CONTACTS (75,000 rows)
    # =========================================================================
    cnl = []
    for i in range(1, 75001):
        cd = rd(opp_start, opp_end)
        fn = f"Vorname{i % 5000}"
        ln = f"Nachname{i % 8000}"
        cnl.append({
            'CONTACT_ID': f"CON{i:08d}",
            'OPPORTUNITY_ID': f"OPP{random.randint(1, 50000):08d}",
            'ACCOUNT_ID': f"ACC{random.randint(1, NUM_CUSTOMERS):06d}",
            'FIRST_NAME': fn, 'LAST_NAME': ln,
            'EMAIL': f"{fn.lower()}.{ln.lower()}@{random.choice(['gmail.com', 'web.de', 'gmx.de', 't-online.de', 'outlook.de'])}",
            'PHONE': f"+49 {random.randint(151, 179)} {random.randint(1000000, 9999999)}",
            'TITLE': random.choice(['Hausbesitzer', 'Eigentuemer', 'Geschaeftsfuehrer', 'Facility Manager', 'Technischer Leiter']),
            'DEPARTMENT': random.choice(['Privat', 'Verwaltung', 'Technik', 'Einkauf']),
            'LEAD_SOURCE': random.choice(leads),
            'CAMPAIGN_NO': random.randint(1, 16000) if random.random() > 0.4 else None,
            'CREATED_DATE': ds(cd)
        })

    cdf = pd.DataFrame(cnl)
    session.sql("TRUNCATE TABLE EPOWER_DEMO.EPOWER_GOLD.SF_CONTACTS").collect()
    session.write_pandas(cdf, "SF_CONTACTS", database="EPOWER_DEMO", schema="EPOWER_GOLD", overwrite=False)
    results.append(f"sf_contacts: {len(cdf):,} rows")

    return f"Domain data generated (anchored to {today}):\n" + "\n".join(results)
