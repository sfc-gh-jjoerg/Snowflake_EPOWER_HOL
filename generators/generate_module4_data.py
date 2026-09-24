#!/usr/bin/env python3
"""
EPOWER Module 3 - Synthetic Data Generator
Generates contract cancellations and customer NPS survey data
for the Cortex Code dbt onboarding demo.

Requires: pandas, numpy
Dependencies: reads customer_dim.csv and product_dim.csv from demo_data/structured_data/
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(43)
np.random.seed(43)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_DIR = os.path.join(BASE_DIR, 'demo_data', 'structured_data')
OUTPUT_DIR = INPUT_DIR

print("=" * 60)
print("EPOWER Module 3 - Data Generator")
print("=" * 60)

customer_dim = pd.read_csv(f'{INPUT_DIR}/customer_dim.csv')
product_dim = pd.read_csv(f'{INPUT_DIR}/product_dim.csv')
sales_fact = pd.read_csv(f'{INPUT_DIR}/sales_fact.csv')

NUM_CUSTOMERS = len(customer_dim)
print(f"Loaded {NUM_CUSTOMERS:,} customers, {len(product_dim)} products, {len(sales_fact):,} contracts")
print()

CANCELLATION_REASONS = [
    ('Umzug', 0.30),
    ('Preiserhöhung', 0.22),
    ('Wettbewerber', 0.18),
    ('Unzufriedenheit', 0.12),
    ('Nicht mehr benötigt', 0.10),
    ('Sonstiges', 0.08),
]
reasons = [r[0] for r in CANCELLATION_REASONS]
reason_weights = [r[1] for r in CANCELLATION_REASONS]

CANCELLATION_CHANNELS = ['Email', 'Telefon', 'App', 'Brief']
channel_weights = [0.35, 0.30, 0.25, 0.10]

CHURN_RATE_BY_CATEGORY = {
    'Electricity': 0.07,
    'Gas': 0.06,
    'Solar & Storage': 0.02,
    'Heat Pumps': 0.015,
    'Smart Home': 0.035,
    'E-Mobility': 0.025,
}

print("1. Generating contract_cancellations (~2,500 rows)...")

customer_products = sales_fact.merge(
    product_dim[['product_key', 'category_name']],
    on='product_key',
    how='left'
)

cancellations = []
cancellation_id = 1
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days

seen_customer_product = set()

for _, row in customer_products.iterrows():
    ck = row['customer_key']
    pk = row['product_key']
    cat = row['category_name']

    key = (ck, pk)
    if key in seen_customer_product:
        continue
    seen_customer_product.add(key)

    churn_rate = CHURN_RATE_BY_CATEGORY.get(cat, 0.10)

    month_factor = 1.0
    if random.random() < churn_rate:
        day_offset = random.randint(0, date_range_days)
        cancel_date = start_date + timedelta(days=day_offset)

        month = cancel_date.month
        if month in [1, 2, 3]:
            if random.random() > 0.6:
                continue
        elif month in [10, 11, 12]:
            if random.random() > 0.8:
                continue

        if cat in ('Electricity', 'Gas'):
            reason = random.choices(reasons, weights=reason_weights)[0]
        elif cat in ('Solar & Storage', 'Heat Pumps'):
            reason = random.choices(
                reasons,
                weights=[0.40, 0.05, 0.05, 0.20, 0.25, 0.05]
            )[0]
        else:
            reason = random.choices(reasons, weights=reason_weights)[0]

        channel = random.choices(CANCELLATION_CHANNELS, weights=channel_weights)[0]

        retention_offered = random.random() < 0.60
        retention_accepted = retention_offered and random.random() < 0.25

        cancellations.append({
            'cancellation_id': cancellation_id,
            'customer_key': ck,
            'product_key': pk,
            'cancellation_date': cancel_date.strftime('%Y-%m-%d'),
            'reason': reason,
            'channel': channel,
            'retention_offered': retention_offered,
            'retention_accepted': retention_accepted,
        })
        cancellation_id += 1

cancellations_df = pd.DataFrame(cancellations)
cancellations_df.to_csv(f'{OUTPUT_DIR}/contract_cancellations.csv', index=False)
print(f"   Generated {len(cancellations_df):,} cancellation records")

reason_counts = cancellations_df['reason'].value_counts()
for r, c in reason_counts.items():
    print(f"   - {r}: {c:,} ({c/len(cancellations_df)*100:.1f}%)")

product_churn = cancellations_df.merge(product_dim[['product_key', 'category_name']], on='product_key')
cat_churn = product_churn['category_name'].value_counts()
print(f"   Cancellations by category:")
for cat, cnt in cat_churn.items():
    print(f"   - {cat}: {cnt:,}")

print()

NPS_CATEGORIES = [
    'Gesamtzufriedenheit',
    'Kundenservice',
    'Produkt',
    'Installation',
    'Preis-Leistung',
    'App & Digital',
]

NPS_COMMENTS = {
    'Gesamtzufriedenheit': {
        'high': ['Sehr zufrieden mit EPOWER', 'Kann ich nur weiterempfehlen', 'Top Anbieter', 'Alles bestens', 'Rundum zufrieden'],
        'mid': ['Im Großen und Ganzen okay', 'Könnte besser sein', 'Durchschnittlich', 'Nichts Besonderes'],
        'low': ['Bin enttäuscht', 'Erwartungen nicht erfüllt', 'Würde nicht erneut wählen', 'Schlechte Erfahrung'],
    },
    'Kundenservice': {
        'high': ['Sehr freundliche Mitarbeiter', 'Schnelle Hilfe erhalten', 'Kompetente Beratung', 'Problemlos gelöst'],
        'mid': ['Lange Wartezeit am Telefon', 'Musste mehrfach anrufen', 'Service war in Ordnung'],
        'low': ['Niemand erreichbar', 'Unfreundlich am Telefon', 'Keine Lösung erhalten', 'Beschwerde ignoriert'],
    },
    'Produkt': {
        'high': ['Solaranlage läuft einwandfrei', 'Wärmepumpe spart enorm', 'Wallbox perfekt installiert', 'Smart Meter sehr nützlich'],
        'mid': ['Funktioniert wie erwartet', 'Leistung könnte besser sein', 'Ganz okay'],
        'low': ['Störungen häufig', 'Qualität mangelhaft', 'Nicht wie versprochen', 'Defekt nach kurzer Zeit'],
    },
    'Installation': {
        'high': ['Installation top organisiert', 'Schnell und sauber', 'Handwerker sehr professionell', 'Termingerecht fertig'],
        'mid': ['Kleine Verzögerung', 'War okay, nichts Besonderes', 'Hat etwas gedauert'],
        'low': ['Termin dreimal verschoben', 'Unsaubere Arbeit', 'Nachbesserung nötig', 'Chaos bei der Installation'],
    },
    'Preis-Leistung': {
        'high': ['Fairer Preis', 'Gutes Preis-Leistungs-Verhältnis', 'Günstiger als erwartet', 'Preis stimmt'],
        'mid': ['Etwas teuer', 'Preis ist okay', 'Vergleichbar mit anderen'],
        'low': ['Zu teuer', 'Versteckte Kosten', 'Preiserhöhung nicht akzeptabel', 'Nicht transparent'],
    },
    'App & Digital': {
        'high': ['App funktioniert super', 'Übersichtliches Portal', 'Einfache Bedienung', 'Verbrauch immer im Blick'],
        'mid': ['App stürzt manchmal ab', 'Design veraltet', 'Funktioniert meistens'],
        'low': ['App nicht nutzbar', 'Login funktioniert nicht', 'Keine Echtzeit-Daten', 'Sehr langsam'],
    },
}

NUM_SURVEYS = 5000
print(f"2. Generating customer_surveys ({NUM_SURVEYS:,} rows)...")

cancelled_customers = set(cancellations_df['customer_key'].unique())

surveys = []
survey_start = datetime(2024, 1, 1)
survey_end = datetime(2025, 12, 31)
survey_range_days = (survey_end - survey_start).days

for i in range(1, NUM_SURVEYS + 1):
    customer_key = random.randint(1, NUM_CUSTOMERS)
    survey_date = survey_start + timedelta(days=random.randint(0, survey_range_days))
    category = random.choice(NPS_CATEGORIES)

    cust_row = customer_dim[customer_dim['customer_key'] == customer_key]
    if len(cust_row) > 0:
        cust_type = cust_row.iloc[0]['customer_type']
    else:
        cust_type = 'Privatkunde'

    if customer_key in cancelled_customers:
        base_nps = random.choices(range(0, 11), weights=[8, 6, 5, 5, 6, 5, 5, 8, 7, 3, 2])[0]
    elif cust_type == 'Gewerbekunde':
        base_nps = random.choices(range(0, 11), weights=[1, 1, 1, 2, 2, 3, 4, 8, 10, 15, 12])[0]
    else:
        base_nps = random.choices(range(0, 11), weights=[2, 1, 1, 2, 3, 4, 5, 10, 12, 15, 10])[0]

    nps_score = max(0, min(10, base_nps))

    has_comment = random.random() < 0.60
    comment = None
    if has_comment:
        if nps_score >= 9:
            comment = random.choice(NPS_COMMENTS[category]['high'])
        elif nps_score >= 7:
            comment = random.choice(NPS_COMMENTS[category]['mid'])
        else:
            comment = random.choice(NPS_COMMENTS[category]['low'])

    surveys.append({
        'survey_id': i,
        'customer_key': customer_key,
        'survey_date': survey_date.strftime('%Y-%m-%d'),
        'nps_score': nps_score,
        'category': category,
        'comment': comment,
    })

surveys_df = pd.DataFrame(surveys)
surveys_df.to_csv(f'{OUTPUT_DIR}/customer_surveys.csv', index=False)
print(f"   Generated {len(surveys_df):,} survey records")

nps_segments = surveys_df['nps_score'].apply(
    lambda x: 'Promoter' if x >= 9 else ('Passive' if x >= 7 else 'Detractor')
)
seg_counts = nps_segments.value_counts()
for seg, cnt in seg_counts.items():
    print(f"   - {seg}: {cnt:,} ({cnt/len(surveys_df)*100:.1f}%)")

avg_nps = surveys_df['nps_score'].mean()
print(f"   Average NPS score: {avg_nps:.1f}")

print()
print("=" * 60)
print("Module 3 data generation complete!")
print(f"  contract_cancellations.csv: {len(cancellations_df):,} rows")
print(f"  customer_surveys.csv:       {len(surveys_df):,} rows")
print("=" * 60)
