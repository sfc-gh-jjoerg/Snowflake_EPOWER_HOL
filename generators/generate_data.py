#!/usr/bin/env python3
"""
Energy Retail Demo - Synthetic Data Generator
Generates realistic German energy retail data for Snowflake AI Demo

Version 3.0 - Enhanced with:
- 15 products (down from 27) with realistic German energy market pricing
- CAPEX + OPEX columns on product_dim
- Category 'Solar' renamed to 'Solar & Storage'
- 20,000 customers, 80,000 contracts
- Realistic consumption patterns linked to products
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('de_DE')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo_data', 'structured_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_CUSTOMERS = 20000
NUM_CONTRACTS = 80000
NUM_SERVICE_LOGS = 10000

# =============================================================================
# VPP CLUSTER DEFINITIONS
# 9 clusters based on real German metropolitan/regional areas.
# Each cluster has a compass region (backward compat), centroid, and share weight.
# =============================================================================
VPP_CLUSTERS = {
    # fmt: cluster_id: {name, compass_region, centroid_lat, centroid_lng, character, share, solar_multiplier, solar_peak_kw, hp_multiplier, grid_bias}
    # solar_multiplier: relative solar irradiation (1.0 = German average ~1050 kWh/m2/yr)
    # solar_peak_kw: max solar output per device (varies by typical panel size & orientation)
    # hp_multiplier: heat pump demand factor (>1 = colder climate, <1 = milder)
    # grid_bias: tendency to import (+) or export (-) in kW
    'freiburg_oberrhein': {'name': 'Freiburg/Oberrhein',  'compass_region': 'South', 'centroid_lat': 47.99, 'centroid_lng': 7.85,  'character': 'Rural, peak solar irradiation',       'share': 0.05, 'solar_multiplier': 1.35, 'solar_peak_kw': 9.5, 'hp_multiplier': 0.7, 'grid_bias': -1.5},
    'bavaria_south':      {'name': 'Bayern Sued',         'compass_region': 'South', 'centroid_lat': 47.85, 'centroid_lng': 11.90, 'character': 'Rural, high solar yield',              'share': 0.06, 'solar_multiplier': 1.25, 'solar_peak_kw': 8.5, 'hp_multiplier': 0.9, 'grid_bias': -1.0},
    'munich_metro':       {'name': 'Muenchen Metro',      'compass_region': 'South', 'centroid_lat': 48.14, 'centroid_lng': 11.58, 'character': 'Urban, high solar yield',              'share': 0.10, 'solar_multiplier': 1.15, 'solar_peak_kw': 7.5, 'hp_multiplier': 1.0, 'grid_bias': -0.5},
    'stuttgart_metro':    {'name': 'Stuttgart Metro',     'compass_region': 'South', 'centroid_lat': 48.78, 'centroid_lng': 9.18,  'character': 'Suburban, industrial',                 'share': 0.08, 'solar_multiplier': 1.10, 'solar_peak_kw': 7.2, 'hp_multiplier': 1.0, 'grid_bias': -0.3},
    'nuernberg_franken':  {'name': 'Nuernberg/Franken',   'compass_region': 'South', 'centroid_lat': 49.45, 'centroid_lng': 11.08, 'character': 'Urban, moderate solar, industrial',    'share': 0.06, 'solar_multiplier': 1.05, 'solar_peak_kw': 7.0, 'hp_multiplier': 1.1, 'grid_bias': 0.0},
    'frankfurt_main':     {'name': 'Frankfurt/Rhein-Main','compass_region': 'West',  'centroid_lat': 50.11, 'centroid_lng': 8.68,  'character': 'Urban, commercial load',               'share': 0.08, 'solar_multiplier': 0.95, 'solar_peak_kw': 6.5, 'hp_multiplier': 1.0, 'grid_bias': 0.3},
    'koeln_bonn':         {'name': 'Koeln/Bonn',          'compass_region': 'West',  'centroid_lat': 50.94, 'centroid_lng': 6.96,  'character': 'Urban, service-sector, moderate load', 'share': 0.07, 'solar_multiplier': 0.90, 'solar_peak_kw': 6.0, 'hp_multiplier': 1.0, 'grid_bias': 0.5},
    'rhine_ruhr':         {'name': 'Rhein-Ruhr',          'compass_region': 'West',  'centroid_lat': 51.23, 'centroid_lng': 6.78,  'character': 'Urban, industrial high load',          'share': 0.09, 'solar_multiplier': 0.85, 'solar_peak_kw': 5.5, 'hp_multiplier': 1.1, 'grid_bias': 1.0},
    'berlin_metro':       {'name': 'Berlin Metro',        'compass_region': 'East',  'centroid_lat': 52.52, 'centroid_lng': 13.41, 'character': 'Urban, mixed generation',              'share': 0.12, 'solar_multiplier': 0.90, 'solar_peak_kw': 6.0, 'hp_multiplier': 1.2, 'grid_bias': 0.5},
    'leipzig_halle':      {'name': 'Leipzig/Halle',       'compass_region': 'East',  'centroid_lat': 51.34, 'centroid_lng': 12.38, 'character': 'Suburban, growing renewables',         'share': 0.05, 'solar_multiplier': 0.88, 'solar_peak_kw': 5.8, 'hp_multiplier': 1.3, 'grid_bias': 0.7},
    'saxony_east':        {'name': 'Sachsen/Ost',         'compass_region': 'East',  'centroid_lat': 51.05, 'centroid_lng': 13.74, 'character': 'Suburban, mixed generation',           'share': 0.05, 'solar_multiplier': 0.85, 'solar_peak_kw': 5.5, 'hp_multiplier': 1.3, 'grid_bias': 0.8},
    'hamburg_metro':      {'name': 'Hamburg Metro',       'compass_region': 'North', 'centroid_lat': 53.55, 'centroid_lng': 9.99,  'character': 'Urban, coastal wind',                  'share': 0.09, 'solar_multiplier': 0.75, 'solar_peak_kw': 5.0, 'hp_multiplier': 1.1, 'grid_bias': 0.8},
    'bremen_weser':       {'name': 'Bremen/Weser',        'compass_region': 'North', 'centroid_lat': 53.08, 'centroid_lng': 8.80,  'character': 'Urban, port logistics, offshore wind', 'share': 0.05, 'solar_multiplier': 0.70, 'solar_peak_kw': 4.8, 'hp_multiplier': 1.1, 'grid_bias': 0.5},
    'lower_saxony':       {'name': 'Niedersachsen/Nord',  'compass_region': 'North', 'centroid_lat': 52.65, 'centroid_lng': 9.20,  'character': 'Rural, wind-heavy generation',         'share': 0.05, 'solar_multiplier': 0.70, 'solar_peak_kw': 4.5, 'hp_multiplier': 1.0, 'grid_bias': 0.3},
}

# =============================================================================
# PLZ-CITY LOOKUP TABLE
# Real German PLZ-to-city mappings, organized by cluster.
# Used only at generation time to assign geographically correct data.
# =============================================================================
PLZ_CITY_LOOKUP = [
    # freiburg_oberrhein — PLZ prefixes 77, 78, 79
    ('79098', 'Freiburg', 'freiburg_oberrhein'),
    ('79111', 'Freiburg', 'freiburg_oberrhein'),
    ('79312', 'Emmendingen', 'freiburg_oberrhein'),
    ('79539', 'Lörrach', 'freiburg_oberrhein'),
    ('79618', 'Rheinfelden', 'freiburg_oberrhein'),
    ('77652', 'Offenburg', 'freiburg_oberrhein'),
    ('77694', 'Kehl', 'freiburg_oberrhein'),
    ('79761', 'Waldshut-Tiengen', 'freiburg_oberrhein'),
    ('79189', 'Bad Krozingen', 'freiburg_oberrhein'),
    ('79252', 'Stegen', 'freiburg_oberrhein'),
    # munich_metro — PLZ prefixes 80, 81, 82, 85
    ('80331', 'München', 'munich_metro'),
    ('80539', 'München', 'munich_metro'),
    ('80796', 'München', 'munich_metro'),
    ('81241', 'München', 'munich_metro'),
    ('81669', 'München', 'munich_metro'),
    ('81927', 'München', 'munich_metro'),
    ('82031', 'Grünwald', 'munich_metro'),
    ('82049', 'Pullach', 'munich_metro'),
    ('82166', 'Gräfelfing', 'munich_metro'),
    ('85221', 'Dachau', 'munich_metro'),
    ('85354', 'Freising', 'munich_metro'),
    ('85748', 'Garching', 'munich_metro'),
    # hamburg_metro — PLZ prefixes 20, 21, 22
    ('20095', 'Hamburg', 'hamburg_metro'),
    ('20249', 'Hamburg', 'hamburg_metro'),
    ('20357', 'Hamburg', 'hamburg_metro'),
    ('20535', 'Hamburg', 'hamburg_metro'),
    ('21029', 'Hamburg', 'hamburg_metro'),
    ('21073', 'Hamburg', 'hamburg_metro'),
    ('21109', 'Hamburg', 'hamburg_metro'),
    ('22041', 'Hamburg', 'hamburg_metro'),
    ('22143', 'Hamburg', 'hamburg_metro'),
    ('22297', 'Hamburg', 'hamburg_metro'),
    ('22453', 'Hamburg', 'hamburg_metro'),
    # berlin_metro — PLZ prefixes 10, 12, 13, 14
    ('10115', 'Berlin', 'berlin_metro'),
    ('10243', 'Berlin', 'berlin_metro'),
    ('10405', 'Berlin', 'berlin_metro'),
    ('10623', 'Berlin', 'berlin_metro'),
    ('10785', 'Berlin', 'berlin_metro'),
    ('12043', 'Berlin', 'berlin_metro'),
    ('12347', 'Berlin', 'berlin_metro'),
    ('12555', 'Berlin', 'berlin_metro'),
    ('13187', 'Berlin', 'berlin_metro'),
    ('13353', 'Berlin', 'berlin_metro'),
    ('14052', 'Berlin', 'berlin_metro'),
    ('14467', 'Potsdam', 'berlin_metro'),
    # rhine_ruhr — PLZ prefixes 40, 44, 45, 47 (Köln moved to koeln_bonn)
    ('40210', 'Düsseldorf', 'rhine_ruhr'),
    ('40477', 'Düsseldorf', 'rhine_ruhr'),
    ('40589', 'Düsseldorf', 'rhine_ruhr'),
    ('44135', 'Dortmund', 'rhine_ruhr'),
    ('44263', 'Dortmund', 'rhine_ruhr'),
    ('45127', 'Essen', 'rhine_ruhr'),
    ('45239', 'Essen', 'rhine_ruhr'),
    ('47051', 'Duisburg', 'rhine_ruhr'),
    ('42103', 'Wuppertal', 'rhine_ruhr'),
    ('44787', 'Bochum', 'rhine_ruhr'),
    ('45879', 'Gelsenkirchen', 'rhine_ruhr'),
    # koeln_bonn — PLZ prefixes 50, 51, 53 (split from rhine_ruhr)
    ('50667', 'Köln', 'koeln_bonn'),
    ('50823', 'Köln', 'koeln_bonn'),
    ('50937', 'Köln', 'koeln_bonn'),
    ('51065', 'Köln', 'koeln_bonn'),
    ('53111', 'Bonn', 'koeln_bonn'),
    ('53225', 'Bonn', 'koeln_bonn'),
    ('51373', 'Leverkusen', 'koeln_bonn'),
    ('51465', 'Bergisch Gladbach', 'koeln_bonn'),
    ('53840', 'Troisdorf', 'koeln_bonn'),
    ('50126', 'Bergheim', 'koeln_bonn'),
    # frankfurt_main — PLZ prefixes 60, 61, 63, 65
    ('60311', 'Frankfurt am Main', 'frankfurt_main'),
    ('60486', 'Frankfurt am Main', 'frankfurt_main'),
    ('60594', 'Frankfurt am Main', 'frankfurt_main'),
    ('61118', 'Bad Vilbel', 'frankfurt_main'),
    ('61440', 'Oberursel', 'frankfurt_main'),
    ('63065', 'Offenbach am Main', 'frankfurt_main'),
    ('63225', 'Langen', 'frankfurt_main'),
    ('65183', 'Wiesbaden', 'frankfurt_main'),
    ('65428', 'Rüsselsheim', 'frankfurt_main'),
    # nuernberg_franken — PLZ prefixes 90, 91, 95, 96, 97
    ('90402', 'Nürnberg', 'nuernberg_franken'),
    ('90491', 'Nürnberg', 'nuernberg_franken'),
    ('90762', 'Fürth', 'nuernberg_franken'),
    ('91052', 'Erlangen', 'nuernberg_franken'),
    ('91054', 'Erlangen', 'nuernberg_franken'),
    ('96047', 'Bamberg', 'nuernberg_franken'),
    ('97070', 'Würzburg', 'nuernberg_franken'),
    ('95444', 'Bayreuth', 'nuernberg_franken'),
    ('91522', 'Ansbach', 'nuernberg_franken'),
    ('91207', 'Lauf an der Pegnitz', 'nuernberg_franken'),
    # stuttgart_metro — PLZ prefixes 70, 71, 72, 73, 76
    ('70173', 'Stuttgart', 'stuttgart_metro'),
    ('70376', 'Stuttgart', 'stuttgart_metro'),
    ('70563', 'Stuttgart', 'stuttgart_metro'),
    ('71032', 'Böblingen', 'stuttgart_metro'),
    ('71065', 'Sindelfingen', 'stuttgart_metro'),
    ('72070', 'Tübingen', 'stuttgart_metro'),
    ('72764', 'Reutlingen', 'stuttgart_metro'),
    ('73728', 'Esslingen', 'stuttgart_metro'),
    ('76131', 'Karlsruhe', 'stuttgart_metro'),
    ('76227', 'Karlsruhe', 'stuttgart_metro'),
    # bremen_weser — PLZ prefixes 27, 28 (split from lower_saxony)
    ('28195', 'Bremen', 'bremen_weser'),
    ('28355', 'Bremen', 'bremen_weser'),
    ('28203', 'Bremen', 'bremen_weser'),
    ('28719', 'Bremen', 'bremen_weser'),
    ('27568', 'Bremerhaven', 'bremen_weser'),
    ('27570', 'Bremerhaven', 'bremen_weser'),
    ('27749', 'Delmenhorst', 'bremen_weser'),
    ('27211', 'Bassum', 'bremen_weser'),
    ('28832', 'Achim', 'bremen_weser'),
    ('27283', 'Verden', 'bremen_weser'),
    # lower_saxony — PLZ prefixes 26, 29, 30, 31 (Bremen moved out)
    ('26122', 'Oldenburg', 'lower_saxony'),
    ('26382', 'Wilhelmshaven', 'lower_saxony'),
    ('26721', 'Emden', 'lower_saxony'),
    ('29221', 'Celle', 'lower_saxony'),
    ('30159', 'Hannover', 'lower_saxony'),
    ('30449', 'Hannover', 'lower_saxony'),
    ('30559', 'Hannover', 'lower_saxony'),
    ('31134', 'Hildesheim', 'lower_saxony'),
    ('38100', 'Braunschweig', 'lower_saxony'),
    ('49074', 'Osnabrück', 'lower_saxony'),
    # bavaria_south — PLZ prefixes 83, 84, 86, 87
    ('83022', 'Rosenheim', 'bavaria_south'),
    ('83278', 'Traunstein', 'bavaria_south'),
    ('83512', 'Wasserburg am Inn', 'bavaria_south'),
    ('84028', 'Landshut', 'bavaria_south'),
    ('84503', 'Altötting', 'bavaria_south'),
    ('86150', 'Augsburg', 'bavaria_south'),
    ('86368', 'Gersthofen', 'bavaria_south'),
    ('86609', 'Donauwörth', 'bavaria_south'),
    ('87435', 'Kempten', 'bavaria_south'),
    ('87527', 'Sonthofen', 'bavaria_south'),
    # leipzig_halle — PLZ prefixes 04, 06, 07, 99 (split from saxony_east)
    ('04103', 'Leipzig', 'leipzig_halle'),
    ('04229', 'Leipzig', 'leipzig_halle'),
    ('04317', 'Leipzig', 'leipzig_halle'),
    ('06108', 'Halle', 'leipzig_halle'),
    ('06217', 'Merseburg', 'leipzig_halle'),
    ('07743', 'Jena', 'leipzig_halle'),
    ('06844', 'Dessau-Roßlau', 'leipzig_halle'),
    ('99423', 'Weimar', 'leipzig_halle'),
    ('04600', 'Altenburg', 'leipzig_halle'),
    ('06110', 'Halle', 'leipzig_halle'),
    # saxony_east — PLZ prefixes 01, 09 (Leipzig/Halle/Jena moved out)
    ('01067', 'Dresden', 'saxony_east'),
    ('01187', 'Dresden', 'saxony_east'),
    ('01309', 'Dresden', 'saxony_east'),
    ('09111', 'Chemnitz', 'saxony_east'),
    ('09112', 'Chemnitz', 'saxony_east'),
    ('02625', 'Bautzen', 'saxony_east'),
    ('08056', 'Zwickau', 'saxony_east'),
    ('01796', 'Pirna', 'saxony_east'),
    ('02826', 'Görlitz', 'saxony_east'),
    ('01662', 'Meißen', 'saxony_east'),
]

# Build a cluster-indexed lookup for fast sampling
_CLUSTER_PLZ_MAP = {}
for _plz, _city, _cid in PLZ_CITY_LOOKUP:
    _CLUSTER_PLZ_MAP.setdefault(_cid, []).append((_plz, _city))

# Legacy compat: map compass regions to region keys
REGION_KEYS = {'North': 400, 'South': 401, 'West': 402, 'East': 403}

# Keep GERMAN_CITIES for backward compat (location_dim, vendor_dim)
GERMAN_CITIES = {
    'North': [
        ('Hamburg', '20', 1850000), ('Bremen', '28', 570000),
        ('Hannover', '30', 535000), ('Oldenburg', '26', 170000),
    ],
    'South': [
        ('München', '80', 1490000), ('Stuttgart', '70', 635000),
        ('Augsburg', '86', 300000), ('Karlsruhe', '76', 310000),
    ],
    'West': [
        ('Köln', '50', 1080000), ('Düsseldorf', '40', 620000),
        ('Dortmund', '44', 590000), ('Essen', '45', 580000),
    ],
    'East': [
        ('Berlin', '10', 3650000), ('Dresden', '01', 560000),
        ('Leipzig', '04', 600000), ('Chemnitz', '09', 245000),
    ],
}

def get_city_weights(region):
    cities = GERMAN_CITIES[region]
    populations = [c[2] for c in cities]
    total = sum(populations)
    return [p / total for p in populations]

def generate_german_zip(city_prefix):
    """Legacy fallback for vendor_dim generation."""
    return f"{city_prefix}{random.randint(100, 999)}"

def pick_cluster():
    """Pick a cluster weighted by household share."""
    cluster_ids = list(VPP_CLUSTERS.keys())
    weights = [VPP_CLUSTERS[c]['share'] for c in cluster_ids]
    return random.choices(cluster_ids, weights=weights)[0]

def pick_plz_city(cluster_id):
    """Sample a real (PLZ, city) pair from a cluster."""
    return random.choice(_CLUSTER_PLZ_MAP[cluster_id])

def generate_german_street():
    street_types = ['Straße', 'Weg', 'Allee', 'Platz', 'Ring', 'Gasse']
    street_names = [
        'Haupt', 'Bahnhof', 'Goethe', 'Schiller', 'Mozart', 'Beethoven',
        'Linden', 'Eichen', 'Birken', 'Rosen', 'Tannen', 'Kirch',
        'Markt', 'Rathaus', 'Schul', 'Park', 'Wald', 'Berg', 'Tal', 'See',
        'Sonnen', 'Mond', 'Stern', 'Blumen', 'Wiesen', 'Heide', 'Brunnen'
    ]
    return f"{random.choice(street_names)}{random.choice(street_types)} {random.randint(1, 150)}"

print("=" * 60)
print("EPOWER Energy Retail Demo - Data Generator v3.0")
print("=" * 60)
print(f"Generating data for {NUM_CUSTOMERS:,} customers...")
print()

print("1. Generating product_category_dim...")
product_categories = pd.DataFrame({
    'category_key': [1, 2, 3, 4, 5, 6],
    'category_name': ['Electricity', 'Gas', 'Solar & Storage', 'Heat Pumps', 'Smart Home', 'E-Mobility'],
    'vertical': ['Energy', 'Energy', 'Future Energy', 'Future Energy', 'Smart Home', 'E-Mobility']
})
product_categories.to_csv(f'{OUTPUT_DIR}/product_category_dim.csv', index=False)

PRODUCTS = [
    #  pk, name,                                     cat_key, cat_name,          vertical,        capex_min, capex_max, opex_min, opex_max
    (  1, 'EPOWER Strom Basis',                       1, 'Electricity',         'Energy',              0,       0,    900,  1200),
    (  2, 'EPOWER Strom Plus',                        1, 'Electricity',         'Energy',              0,       0,   1200,  1500),
    (  3, 'EPOWER Ökostrom 100%',                     1, 'Electricity',         'Energy',              0,       0,   1400,  1800),
    (  4, 'EPOWER Gas Basis',                         2, 'Gas',                 'Energy',              0,       0,   1200,  1800),
    (  5, 'EPOWER Gas Plus',                          2, 'Gas',                 'Energy',              0,       0,   1800,  2400),
    (  6, 'EPOWER Solar S 5kWp',                      3, 'Solar & Storage',     'Future Energy',   12000,   16000,    200,   400),
    (  7, 'EPOWER Solar M 8kWp',                      3, 'Solar & Storage',     'Future Energy',   16000,   22000,    300,   500),
    (  8, 'EPOWER Solar L 12kWp + Speicher 10kWh',    3, 'Solar & Storage',     'Future Energy',   24000,   30000,    400,   600),
    (  9, 'EPOWER Wärmepumpe Luft-Wasser',            4, 'Heat Pumps',          'Future Energy',   18000,   24000,    600,   900),
    ( 10, 'EPOWER Wärmepumpe Sole-Wasser',            4, 'Heat Pumps',          'Future Energy',   28000,   35000,    400,   700),
    ( 11, 'EPOWER Smart Meter',                       5, 'Smart Home',          'Smart Home',          0,       0,      0,     0),
    ( 12, 'EPOWER Home Energy Manager',               5, 'Smart Home',          'Smart Home',        399,     599,     60,   120),
    ( 13, 'EPOWER Wallbox 11kW',                      6, 'E-Mobility',          'E-Mobility',       1400,    1900,      0,     0),
    ( 14, 'EPOWER Wallbox 22kW',                      6, 'E-Mobility',          'E-Mobility',       2200,    3000,      0,     0),
    ( 15, 'EPOWER Autostrom Tarif',                   6, 'E-Mobility',          'E-Mobility',          0,       0,    600,  1200),
]

PRODUCT_PRICING = {p[0]: {'capex_min': p[5], 'capex_max': p[6], 'opex_min': p[7], 'opex_max': p[8]} for p in PRODUCTS}

print("2. Generating product_dim (15 products with CAPEX/OPEX)...")
product_rows = []
for p in PRODUCTS:
    capex = round(random.uniform(p[5], p[6]), 2) if p[6] > 0 else 0
    opex = round(random.uniform(p[7], p[8]), 2) if p[8] > 0 else 0
    product_rows.append({
        'product_key': p[0], 'product_name': p[1], 'category_key': p[2],
        'category_name': p[3], 'vertical': p[4],
        'capex_eur': capex, 'opex_eur_year': opex
    })
product_dim = pd.DataFrame(product_rows)
product_dim.to_csv(f'{OUTPUT_DIR}/product_dim.csv', index=False)

print("3. Generating region_dim...")
region_dim = pd.DataFrame({
    'region_key': [400, 401, 402, 403],
    'region_name': ['North', 'South', 'West', 'East']
})
region_dim.to_csv(f'{OUTPUT_DIR}/region_dim.csv', index=False)

print("4. Generating location_dim...")
locations = []
loc_key = 900
for region, cities in GERMAN_CITIES.items():
    for city, _, _ in cities[:3]:
        locations.append((loc_key, f"{city}, DE"))
        loc_key += 1
location_dim = pd.DataFrame(locations, columns=['location_key', 'location_name'])
location_dim.to_csv(f'{OUTPUT_DIR}/location_dim.csv', index=False)

print("5. Generating department_dim...")
departments = [
    (10, 'Finanzen'), (11, 'Buchhaltung'), (12, 'Controlling'), (13, 'Steuern'),
    (14, 'Revision'), (15, 'Treasury'), (16, 'Einkauf'), (17, 'Recht'),
    (18, 'Compliance'), (19, 'Risikomanagement'), (20, 'Vertrieb Privatkunden'),
    (21, 'Vertrieb Gewerbekunden'), (22, 'Kundenservice'), (23, 'Vertriebssteuerung'),
    (24, 'Partnermanagement'), (25, 'Technischer Vertrieb'), (26, 'Key Account Management'),
    (27, 'Innendienst'), (28, 'Außendienst'), (29, 'Vertriebssupport'),
    (30, 'Marketing'), (31, 'Digital Marketing'), (32, 'Content Marketing'),
    (33, 'Produktmarketing'), (34, 'Markenführung'), (35, 'Event Marketing'),
    (36, 'Marktforschung'), (37, 'Unternehmenskommunikation'), (38, 'Social Media'),
    (39, 'Marketing Operations'), (40, 'Personal'),
]
department_dim = pd.DataFrame(departments, columns=['department_key', 'department_name'])
department_dim.to_csv(f'{OUTPUT_DIR}/department_dim.csv', index=False)

print("6. Generating job_dim...")
jobs = [
    (800, 'Ingenieur', 3), (801, 'Personalleiter', 4), (802, 'Datenanalyst', 2),
    (803, 'Recruiter', 2), (804, 'Finanzspezialist', 3), (805, 'Vertriebsleiter', 4),
    (806, 'Marketing Koordinator', 2), (807, 'Betriebsleiter', 3),
    (808, 'Service-Mitarbeiter', 1), (809, 'IT-Administrator', 2),
    (810, 'Energieberater', 2), (811, 'Techniker Außendienst', 2),
    (812, 'Kundenberater', 1), (813, 'Installateur Solar', 2),
    (814, 'Installateur Wärmepumpe', 2), (815, 'Smart Home Spezialist', 3),
]
job_dim = pd.DataFrame(jobs, columns=['job_key', 'job_title', 'job_level'])
job_dim.to_csv(f'{OUTPUT_DIR}/job_dim.csv', index=False)

print("7. Generating channel_dim...")
channel_dim = pd.DataFrame({
    'channel_key': [600, 601, 602, 603, 604, 605],
    'channel_name': ['Email', 'Webseite', 'Facebook', 'Instagram', 'Google Ads', 'TV']
})
channel_dim.to_csv(f'{OUTPUT_DIR}/channel_dim.csv', index=False)

print("8. Generating account_dim...")
account_dim = pd.DataFrame({
    'account_key': [1, 2, 3],
    'account_name': ['Umsatz', 'Aufwand', 'Wareneinsatz'],
    'account_type': ['Einnahmen', 'Ausgaben', 'Ausgaben']
})
account_dim.to_csv(f'{OUTPUT_DIR}/account_dim.csv', index=False)

print(f"9. Generating customer_dim ({NUM_CUSTOMERS:,} German customers with VPP clusters)...")
customer_types = ['Privatkunde', 'Kleingewerbe', 'Gewerbekunde']
housing_types_private = ['Einfamilienhaus', 'Reihenhaus', 'Wohnung', 'Mehrfamilienhaus']
housing_types_business = ['Gewerbeimmobilie']

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    cluster_id = pick_cluster()
    cluster = VPP_CLUSTERS[cluster_id]
    plz, city = pick_plz_city(cluster_id)
    compass_region = cluster['compass_region']
    
    customer_type = random.choices(customer_types, weights=[0.75, 0.18, 0.07])[0]
    if customer_type == 'Gewerbekunde':
        housing = 'Gewerbeimmobilie'
    elif customer_type == 'Kleingewerbe':
        housing = random.choices(housing_types_private + housing_types_business, weights=[0.3, 0.2, 0.2, 0.1, 0.2])[0]
    else:
        housing = random.choices(housing_types_private, weights=[0.35, 0.20, 0.35, 0.10])[0]
    
    name = fake.company() if customer_type in ['Gewerbekunde', 'Kleingewerbe'] and random.random() > 0.3 else fake.name()
    
    customers.append({
        'customer_key': i,
        'customer_name': name,
        'customer_type': customer_type,
        'housing_type': housing,
        'vertical': 'Energy',
        'address': generate_german_street(),
        'city': city,
        'zip': plz,
        'state': compass_region,
        'cluster_id': cluster_id,
        'region_key': REGION_KEYS[compass_region]
    })
customer_dim = pd.DataFrame(customers)
customer_dim.to_csv(f'{OUTPUT_DIR}/customer_dim.csv', index=False)

print("   Generating vpp_cluster_dim...")
cluster_rows = []
for cid, info in VPP_CLUSTERS.items():
    cluster_rows.append({
        'cluster_id': cid,
        'cluster_name': info['name'],
        'centroid_lat': info['centroid_lat'],
        'centroid_lng': info['centroid_lng'],
        'region_character': info['character'],
        'compass_region': info['compass_region'],
        'solar_multiplier': info['solar_multiplier'],
        'solar_peak_kw': info['solar_peak_kw'],
        'hp_multiplier': info['hp_multiplier'],
        'grid_bias': info['grid_bias']
    })
vpp_cluster_dim = pd.DataFrame(cluster_rows)
vpp_cluster_dim.to_csv(f'{OUTPUT_DIR}/vpp_cluster_dim.csv', index=False)

print("10. Generating vendor_dim...")
vendor_types = [
    ('Installateur', 'Future Energy'), ('Wartungspartner', 'Future Energy'),
    ('Smart Home Partner', 'Smart Home'), ('E-Mobility Partner', 'E-Mobility'),
    ('Lieferant', 'Energy'),
]
vendors = []
for i in range(1, 201):
    region = random.choice(list(GERMAN_CITIES.keys()))
    cities = GERMAN_CITIES[region]
    city, zip_prefix, _ = random.choice(cities)
    vtype, vertical = random.choice(vendor_types)
    vendor_suffixes = ['GmbH', 'AG', 'KG', 'e.K.', 'UG']
    vendor_names = ['Solar', 'Energie', 'Wärme', 'Klima', 'Haustechnik', 'Elektro', 'Power', 'Green', 'Eco', 'Smart', 'Tech', 'Service']
    vendor_name = f"{fake.last_name()} {random.choice(vendor_names)} {random.choice(vendor_suffixes)}"
    
    vendors.append({
        'vendor_key': i, 'vendor_name': vendor_name, 'vendor_type': vtype, 'vertical': vertical,
        'address': generate_german_street(), 'city': city, 'state': region, 'zip': generate_german_zip(zip_prefix)
    })
vendor_dim = pd.DataFrame(vendors)
vendor_dim.to_csv(f'{OUTPUT_DIR}/vendor_dim.csv', index=False)

print("11. Generating employee_dim...")
employees = []
for i in range(1, 1001):
    hire_date = fake.date_between(start_date='-10y', end_date='-6m')
    employees.append({'employee_key': i, 'employee_name': fake.name(), 'gender': random.choice(['M', 'F']), 'hire_date': hire_date.strftime('%Y-%m-%d')})
employee_dim = pd.DataFrame(employees)
employee_dim.to_csv(f'{OUTPUT_DIR}/employee_dim.csv', index=False)

print("12. Generating sales_rep_dim...")
sales_reps = []
for i in range(1, 501):
    hire_date = fake.date_between(start_date='-8y', end_date='-3m')
    sales_reps.append({'sales_rep_key': i, 'rep_name': fake.name(), 'hire_date': hire_date.strftime('%Y-%m-%d')})
sales_rep_dim = pd.DataFrame(sales_reps)
sales_rep_dim.to_csv(f'{OUTPUT_DIR}/sales_rep_dim.csv', index=False)

print("13. Generating campaign_dim...")
campaign_names = [
    ('Grüner Strom Aktion', 'Neukundengewinnung'), ('Wärmepumpen Förderung 2024', 'Produktlaunch'),
    ('Solar Frühlings-Rabatt', 'Upsell'), ('Smart Home Einführungsangebot', 'Produktlaunch'),
    ('E-Mobility Bonus', 'Neukundengewinnung'), ('Ökostrom für alle', 'Markenbekanntheit'),
    ('Wintercheck Heizung', 'Kundenbindung'), ('Energiespar-Challenge', 'Engagement'),
    ('Nachbarschafts-Empfehlung', 'Empfehlung'), ('Business Energy Paket', 'Lead-Generierung'),
]
campaigns = []
for i, (name, objective) in enumerate(campaign_names, 1):
    campaigns.append({'campaign_key': i, 'campaign_name': name, 'objective': objective})
for i in range(11, 101):
    campaigns.append({'campaign_key': i, 'campaign_name': f"Energie Kampagne {i}", 'objective': random.choice(['Neukundengewinnung', 'Kundenbindung', 'Upsell', 'Lead-Generierung'])})
campaign_dim = pd.DataFrame(campaigns)
campaign_dim.to_csv(f'{OUTPUT_DIR}/campaign_dim.csv', index=False)

print(f"14. Generating sales_fact ({NUM_CONTRACTS:,} contracts)...")
electricity_products = [1, 2, 3]
gas_products = [4, 5]
solar_products = [6, 7, 8]
heatpump_products = [9, 10]
smarthome_products = [11, 12]
emobility_products = [13, 14, 15]

all_customers = list(range(1, NUM_CUSTOMERS + 1))
random.shuffle(all_customers)

num_solar = int(NUM_CUSTOMERS * 0.70)
num_heatpump = int(NUM_CUSTOMERS * 0.70)
num_overlap = int(NUM_CUSTOMERS * 0.60)

solar_customers = set(all_customers[:num_solar])
heatpump_pool = all_customers[:num_overlap] + all_customers[num_solar:num_solar + (num_heatpump - num_overlap)]
heatpump_customers = set(heatpump_pool)

gas_customers = set(all_customers) - heatpump_customers

print(f"   - Pre-assigned Solar customers: {len(solar_customers):,}")
print(f"   - Pre-assigned Heat Pump customers: {len(heatpump_customers):,}")
print(f"   - Overlap (both): {len(solar_customers & heatpump_customers):,}")
print(f"   - Pre-assigned Gas customers (non-HP): {len(gas_customers):,}")

contracts = []
start_date, end_date = datetime(2022, 1, 1), datetime(2025, 12, 31)
contract_id = 1

customer_lookup = customer_dim.set_index('customer_key')

for cust in solar_customers:
    c = customer_lookup.loc[cust]
    product_key = random.choice(solar_products)
    pr = PRODUCT_PRICING[product_key]
    contracts.append({
        'sale_id': contract_id, 'date': fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d'),
        'customer_key': cust, 'product_key': product_key, 'sales_rep_key': random.randint(1, 500),
        'region_key': c['region_key'], 'vendor_key': random.randint(1, 200),
        'amount': round(random.uniform(pr['capex_min'], pr['capex_max']), 2), 'units': 1
    })
    contract_id += 1

for cust in heatpump_customers:
    c = customer_lookup.loc[cust]
    product_key = random.choice(heatpump_products)
    pr = PRODUCT_PRICING[product_key]
    contracts.append({
        'sale_id': contract_id, 'date': fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d'),
        'customer_key': cust, 'product_key': product_key, 'sales_rep_key': random.randint(1, 500),
        'region_key': c['region_key'], 'vendor_key': random.randint(1, 200),
        'amount': round(random.uniform(pr['capex_min'], pr['capex_max']), 2), 'units': 1
    })
    contract_id += 1

for cust in gas_customers:
    c = customer_lookup.loc[cust]
    product_key = random.choice(gas_products)
    pr = PRODUCT_PRICING[product_key]
    contracts.append({
        'sale_id': contract_id, 'date': fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d'),
        'customer_key': cust, 'product_key': product_key, 'sales_rep_key': random.randint(1, 500),
        'region_key': c['region_key'], 'vendor_key': random.randint(1, 200),
        'amount': round(random.uniform(pr['opex_min'], pr['opex_max']), 2), 'units': random.randint(10000, 25000)
    })
    contract_id += 1

remaining_contracts = NUM_CONTRACTS - len(contracts)
for _ in range(remaining_contracts):
    customer_key = random.randint(1, NUM_CUSTOMERS)
    c = customer_lookup.loc[customer_key]
    housing = c['housing_type']
    is_hp = customer_key in heatpump_customers

    if is_hp:
        product_type = random.choices(['electricity', 'smarthome', 'emobility', 'electricity'], weights=[0.55, 0.20, 0.15, 0.10])[0]
    else:
        product_type = random.choices(['electricity', 'gas', 'smarthome', 'emobility', 'electricity'], weights=[0.40, 0.25, 0.15, 0.12, 0.08])[0]

    if product_type == 'electricity':
        product_key = random.choice(electricity_products)
        pr = PRODUCT_PRICING[product_key]
        amount, units = round(random.uniform(pr['opex_min'], pr['opex_max']), 2), random.randint(2000, 6000)
    elif product_type == 'gas':
        product_key = random.choice(gas_products)
        pr = PRODUCT_PRICING[product_key]
        amount, units = round(random.uniform(pr['opex_min'], pr['opex_max']), 2), random.randint(10000, 25000)
    elif product_type == 'smarthome':
        product_key = random.choice(smarthome_products)
        pr = PRODUCT_PRICING[product_key]
        capex = random.uniform(pr['capex_min'], pr['capex_max']) if pr['capex_max'] > 0 else 0
        amount, units = round(capex, 2), 1
    else:
        product_key = random.choice(emobility_products)
        pr = PRODUCT_PRICING[product_key]
        if pr['capex_max'] > 0:
            amount = round(random.uniform(pr['capex_min'], pr['capex_max']), 2)
        else:
            amount = round(random.uniform(pr['opex_min'], pr['opex_max']), 2)
        units = 1

    contracts.append({
        'sale_id': contract_id, 'date': fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d'),
        'customer_key': customer_key, 'product_key': product_key, 'sales_rep_key': random.randint(1, 500),
        'region_key': c['region_key'], 'vendor_key': random.randint(1, 200),
        'amount': round(amount, 2), 'units': units
    })
    contract_id += 1

sales_fact = pd.DataFrame(contracts)
sales_fact.to_csv(f'{OUTPUT_DIR}/sales_fact.csv', index=False)

print("15. Generating customer_products (product ownership tracking)...")
customer_products = []
cp_id = 1

customer_product_map = {}

for _, contract in sales_fact.iterrows():
    customer_key = contract['customer_key']
    product_key = contract['product_key']
    contract_date = contract['date']
    
    if customer_key not in customer_product_map:
        customer_product_map[customer_key] = set()
    
    if product_key not in customer_product_map[customer_key]:
        customer_product_map[customer_key].add(product_key)
        product_info = product_dim[product_dim['product_key'] == product_key].iloc[0]
        
        customer_products.append({
            'customer_product_id': cp_id,
            'customer_key': customer_key,
            'product_key': product_key,
            'category_key': product_info['category_key'],
            'category_name': product_info['category_name'],
            'acquisition_date': contract_date,
            'status': random.choices(['Active', 'Inactive'], weights=[0.95, 0.05])[0]
        })
        cp_id += 1

customer_products_df = pd.DataFrame(customer_products)
customer_products_df.to_csv(f'{OUTPUT_DIR}/customer_products.csv', index=False)

customers_with_heatpumps = set(customer_products_df[customer_products_df['category_name'] == 'Heat Pumps']['customer_key'].unique())
customers_with_solar = set(customer_products_df[customer_products_df['category_name'] == 'Solar & Storage']['customer_key'].unique())
customers_with_emobility = set(customer_products_df[customer_products_df['category_name'] == 'E-Mobility']['customer_key'].unique())

print(f"   - Customers with Heat Pumps: {len(customers_with_heatpumps):,}")
print(f"   - Customers with Solar: {len(customers_with_solar):,}")
print(f"   - Customers with E-Mobility: {len(customers_with_emobility):,}")

print("16. Generating billing_history (with realistic consumption based on products)...")
billing = []
bill_id = 1

billing_customers = list(range(1, min(NUM_CUSTOMERS + 1, 10001)))

for customer_key in billing_customers:
    customer = customer_dim[customer_dim['customer_key'] == customer_key].iloc[0]
    housing = customer['housing_type']
    
    base_kwh_e = {'Einfamilienhaus': 4200, 'Reihenhaus': 3200, 'Wohnung': 2000, 'Mehrfamilienhaus': 2800, 'Gewerbeimmobilie': 12000}.get(housing, 3000)
    base_kwh_g = {'Einfamilienhaus': 16000, 'Reihenhaus': 12000, 'Wohnung': 6000, 'Mehrfamilienhaus': 10000, 'Gewerbeimmobilie': 30000}.get(housing, 15000)
    
    has_heatpump = customer_key in customers_with_heatpumps
    has_solar = customer_key in customers_with_solar
    has_emobility = customer_key in customers_with_emobility
    
    is_migrating = has_heatpump and random.random() < 0.05
    if has_heatpump and not is_migrating:
        hp_install_year = random.choice([2022, 2023])
    elif is_migrating:
        hp_install_year = random.choice([2024, 2025])
    else:
        hp_install_year = None
    
    if has_heatpump:
        base_kwh_e += random.randint(3500, 5500)
    
    if has_emobility:
        base_kwh_e += random.randint(2000, 3500)
    
    if has_solar:
        base_kwh_e = int(base_kwh_e * random.uniform(0.5, 0.7))
    
    for year in [2023, 2024, 2025]:
        for month in range(1, 13):
            if year == 2025 and month > 6:
                continue
            
            if has_heatpump and not is_migrating:
                uses_gas = False
            elif is_migrating:
                uses_gas = (year < hp_install_year) or (year == hp_install_year and month <= 6)
            else:
                uses_gas = True
            
            seasonal_e = {1: 1.3, 2: 1.3, 3: 1.1, 11: 1.2, 12: 1.4, 6: 0.75, 7: 0.7, 8: 0.7}.get(month, 1.0)
            seasonal_g = {1: 1.8, 2: 1.7, 3: 1.4, 4: 0.8, 5: 0.4, 6: 0.2, 7: 0.15, 8: 0.15, 9: 0.3, 10: 0.7, 11: 1.3, 12: 1.6}.get(month, 1.0)
            
            if has_heatpump and not uses_gas:
                kwh_e = int((base_kwh_e) / 12 * seasonal_e * random.uniform(0.85, 1.15))
            else:
                kwh_e_base = base_kwh_e - (random.randint(3500, 5500) if has_heatpump else 0)
                kwh_e = int(max(kwh_e_base, 2000) / 12 * seasonal_e * random.uniform(0.85, 1.15))
            kwh_g = int(base_kwh_g / 12 * seasonal_g * random.uniform(0.80, 1.20))
            
            billing.append({
                'billing_id': bill_id, 
                'customer_key': customer_key, 
                'billing_date': f"{year}-{month:02d}-15",
                'billing_type': 'Electricity', 
                'consumption_kwh': kwh_e, 
                'amount': round(kwh_e * random.uniform(0.30, 0.40) + 12.50, 2),
                'payment_status': random.choices(['Bezahlt', 'Offen', 'Überfällig'], weights=[0.88, 0.08, 0.04])[0]
            })
            bill_id += 1
            
            if uses_gas:
                if kwh_g > 50:
                    billing.append({
                        'billing_id': bill_id, 
                        'customer_key': customer_key, 
                        'billing_date': f"{year}-{month:02d}-15",
                        'billing_type': 'Gas', 
                        'consumption_kwh': kwh_g, 
                        'amount': round(kwh_g * random.uniform(0.09, 0.13) + 8.90, 2),
                        'payment_status': random.choices(['Bezahlt', 'Offen', 'Überfällig'], weights=[0.88, 0.08, 0.04])[0]
                    })
                    bill_id += 1

billing_history = pd.DataFrame(billing)
billing_history.to_csv(f'{OUTPUT_DIR}/billing_history.csv', index=False)

print(f"17. Generating service_logs ({NUM_SERVICE_LOGS:,} tickets)...")
ticket_types = [
    ('Smart Meter', 'Installation', ['Smart Meter Installation angefragt', 'Smart Meter defekt', 'Smart Meter Ablesung fehlerhaft', 'Smart Meter zeigt keine Daten', 'Smart Meter App funktioniert nicht']),
    ('Rechnung', 'Abrechnung', ['Rechnungsfrage', 'Unstimmigkeit in Rechnung', 'Zahlungsplan angefragt', 'Abschlag zu hoch', 'Abschlag anpassen', 'Gutschrift angefragt']),
    ('Wärmepumpe', 'Technisch', ['Wärmepumpe Störung', 'Wartung angefragt', 'Effizienz zu niedrig', 'Wärmepumpe läuft nicht', 'Geräuschentwicklung zu hoch', 'Fehlercode E01 angezeigt']),
    ('Solar', 'Technisch', ['Solaranlage Ertrag niedrig', 'Wechselrichter Fehler', 'Monitoring nicht verfügbar', 'Solaranlage produziert nicht', 'Einspeisevergütung Frage']),
    ('Tarif', 'Vertrag', ['Tarifwechsel angefragt', 'Kündigung', 'Umzug melden', 'Vertragsverlängerung', 'Preisgarantie Frage', 'Ökostrom Umstellung']),
    ('Wallbox', 'E-Mobility', ['Wallbox Installation angefragt', 'Wallbox defekt', 'Ladekarte Probleme', 'Wallbox lädt nicht', 'App-Verbindung unterbrochen']),
    ('Allgemein', 'Service', ['Allgemeine Anfrage', 'Beschwerde', 'Lob', 'Informationsanfrage', 'Kontaktdaten ändern']),
    ('Speicher', 'Technisch', ['Batteriespeicher Störung', 'Speicher lädt nicht', 'Kapazität gesunken']),
]
sentiments, priorities = ['Positiv', 'Neutral', 'Negativ'], ['Niedrig', 'Mittel', 'Hoch', 'Kritisch']

service_logs = []
for log_id in range(1, NUM_SERVICE_LOGS + 1):
    log_date = fake.date_between(start_date=datetime(2023, 1, 1), end_date=datetime(2025, 6, 30))
    topic, category, descriptions = random.choice(ticket_types)
    description = random.choice(descriptions)
    
    if 'defekt' in description or 'Störung' in description or 'Beschwerde' in description or 'nicht' in description:
        sentiment = 'Negativ'
        priority = random.choices(priorities, weights=[0.1, 0.3, 0.4, 0.2])[0]
    elif 'Lob' in description:
        sentiment = 'Positiv'
        priority = 'Niedrig'
    else:
        sentiment = random.choices(sentiments, weights=[0.15, 0.65, 0.20])[0]
        priority = random.choices(priorities, weights=[0.3, 0.5, 0.15, 0.05])[0]
    
    resolution_days = random.randint(0, 14) if priority in ['Niedrig', 'Mittel'] else random.randint(0, 7)
    
    service_logs.append({
        'log_id': log_id, 
        'customer_key': random.randint(1, NUM_CUSTOMERS), 
        'log_date': log_date.strftime('%Y-%m-%d'),
        'topic': topic, 
        'category': category, 
        'description': description, 
        'sentiment': sentiment,
        'channel': random.choice(['Telefon', 'Email', 'Chat', 'App']), 
        'priority': priority,
        'resolution_date': (log_date + timedelta(days=resolution_days)).strftime('%Y-%m-%d'), 
        'agent_key': random.randint(1, 200)
    })
service_logs_df = pd.DataFrame(service_logs)
service_logs_df.to_csv(f'{OUTPUT_DIR}/service_logs.csv', index=False)

print("18. Generating finance_transactions...")
finance_transactions = []
for txn_id in range(1, 30001):
    txn_date = fake.date_between(start_date=datetime(2022, 1, 1), end_date=datetime(2025, 6, 30))
    account_key = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
    amount = round(random.uniform(50, 5000) if account_key == 1 else random.uniform(10, 2000), 2)
    approval_status = random.choices(['Approved', 'Pending', 'Rejected'], weights=[0.85, 0.10, 0.05])[0]
    
    finance_transactions.append({
        'transaction_id': txn_id, 'date': txn_date.strftime('%Y-%m-%d'), 'account_key': account_key,
        'department_key': random.randint(10, 40), 'vendor_key': random.randint(1, 200),
        'product_key': random.randint(1, 15), 'customer_key': random.randint(1, NUM_CUSTOMERS),
        'amount': amount, 'approval_status': approval_status,
        'procurement_method': random.choice(['Vertrag', 'Ausschreibung', 'Direktvergabe']),
        'approver_id': random.randint(1, 1000) if approval_status != 'Pending' else '',
        'approval_date': (txn_date + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d') if approval_status != 'Pending' else '',
        'purchase_order_number': f"PO-{random.randint(100000, 999999)}" if random.random() > 0.3 else '',
        'contract_reference': f"VTR-{random.randint(2020, 2025)}-{random.randint(1000, 9999)}" if random.random() > 0.4 else ''
    })
finance_df = pd.DataFrame(finance_transactions)
finance_df.to_csv(f'{OUTPUT_DIR}/finance_transactions.csv', index=False)

print("19. Generating marketing_campaign_fact...")
marketing_facts = []
for fact_id in range(1, 16001):
    fact_date = fake.date_between(start_date=datetime(2022, 1, 1), end_date=datetime(2025, 6, 30))
    marketing_facts.append({
        'campaign_fact_id': fact_id, 'date': fact_date.strftime('%Y-%m-%d'),
        'campaign_key': random.randint(1, 100), 'product_key': random.randint(1, 15),
        'channel_key': random.choice([600, 601, 602, 603, 604, 605]), 'region_key': random.choice([400, 401, 402, 403]),
        'spend': round(random.uniform(50, 500), 2), 'leads_generated': random.randint(5, 100), 'impressions': random.randint(100, 15000)
    })
marketing_df = pd.DataFrame(marketing_facts)
marketing_df.to_csv(f'{OUTPUT_DIR}/marketing_campaign_fact.csv', index=False)

print("20. Generating hr_employee_fact...")
hr_facts = []
hr_id = 1
for emp_key in range(1, 1001):
    emp = employee_dim[employee_dim['employee_key'] == emp_key].iloc[0]
    hire_date = datetime.strptime(emp['hire_date'], '%Y-%m-%d')
    current_date, salary = hire_date, random.randint(35000, 85000)
    left = random.random() < 0.15
    potential_leave = hire_date + timedelta(days=180)
    leave_date = None
    if left and potential_leave < datetime(2025, 6, 30):
        leave_date = fake.date_between(start_date=potential_leave, end_date=datetime(2025, 6, 30))
    
    while current_date < datetime(2025, 7, 1):
        attrition = 1 if leave_date and current_date.date() >= leave_date else 0
        hr_facts.append({
            'hr_fact_id': hr_id, 'date': current_date.strftime('%Y-%m-%d'), 'employee_key': emp_key,
            'department_key': random.randint(10, 40), 'job_key': random.choice([800,801,802,803,804,805,806,807,808,809,810,811,812,813,814,815]),
            'location_key': random.randint(900, 911), 'salary': salary, 'attrition_flag': attrition
        })
        hr_id += 1
        if attrition == 1: break
        current_date += timedelta(days=random.randint(180, 360))
        if random.random() < 0.1: salary = int(salary * random.uniform(1.03, 1.10))
hr_df = pd.DataFrame(hr_facts)
hr_df.to_csv(f'{OUTPUT_DIR}/hr_employee_fact.csv', index=False)

print("21. Generating sf_accounts...")
sf_accounts = []
for i in range(1, NUM_CUSTOMERS + 1):
    customer = customer_dim[customer_dim['customer_key'] == i].iloc[0]
    sf_accounts.append({
        'account_id': f"ACC{i:06d}", 'account_name': customer['customer_name'], 'customer_key': i,
        'industry': customer['customer_type'], 'vertical': 'Energy', 'billing_street': customer['address'],
        'billing_city': customer['city'], 'billing_state': customer['state'], 'billing_postal_code': customer['zip'],
        'account_type': random.choice(['Kunde', 'Interessent', 'Partner']),
        'annual_revenue': random.randint(0, 500000) if customer['customer_type'] == 'Privatkunde' else random.randint(100000, 5000000),
        'employees': 1 if customer['customer_type'] == 'Privatkunde' else random.choice([5, 10, 25, 50, 100]),
        'created_date': fake.date_between(start_date=datetime(2020, 1, 1), end_date=datetime(2023, 12, 31)).strftime('%Y-%m-%d')
    })
sf_accounts_df = pd.DataFrame(sf_accounts)
sf_accounts_df.to_csv(f'{OUTPUT_DIR}/sf_accounts.csv', index=False)

print("22. Generating sf_opportunities...")
sf_opportunities = []
stages = ['Closed Won', 'Closed Lost', 'Verhandlung', 'Angebot', 'Qualifizierung', 'Interessent']
lead_sources = ['Webseite', 'Empfehlung', 'Messe', 'Telefonakquise', 'Partner', 'Social Media']
for i in range(1, 50001):
    created_date = fake.date_between(start_date=datetime(2021, 1, 1), end_date=datetime(2025, 6, 30))
    stage = random.choices(stages, weights=[0.25, 0.15, 0.15, 0.20, 0.15, 0.10])[0]
    probability = 100.0 if stage == 'Closed Won' else (0.0 if stage == 'Closed Lost' else random.uniform(10, 80))
    close_date = created_date + timedelta(days=random.randint(30, 180))
    sale_id = i if stage == 'Closed Won' and i <= NUM_CONTRACTS else ''
    
    sf_opportunities.append({
        'opportunity_id': f"OPP{i:08d}", 'sale_id': sale_id, 'account_id': f"ACC{random.randint(1, NUM_CUSTOMERS):06d}",
        'opportunity_name': f"Opportunity {i}", 'stage_name': stage, 'amount': round(random.uniform(500, 50000), 2),
        'probability': round(probability, 1), 'close_date': close_date.strftime('%Y-%m-%d'),
        'created_date': created_date.strftime('%Y-%m-%d'), 'lead_source': random.choice(lead_sources),
        'type': random.choice(['Neukunde', 'Bestandskunde - Upgrade', 'Bestandskunde - Zusatzprodukt']),
        'campaign_id': random.randint(1, 16000) if random.random() > 0.3 else ''
    })
sf_opp_df = pd.DataFrame(sf_opportunities)
sf_opp_df.to_csv(f'{OUTPUT_DIR}/sf_opportunities.csv', index=False)

print("23. Generating sf_contacts...")
sf_contacts = []
titles = ['Hausbesitzer', 'Eigentümer', 'Geschäftsführer', 'Facility Manager', 'Technischer Leiter']
for i in range(1, 75001):
    opp_idx = random.randint(1, 50000)
    sf_contacts.append({
        'contact_id': f"CON{i:08d}", 'opportunity_id': f"OPP{opp_idx:08d}", 'account_id': f"ACC{random.randint(1, NUM_CUSTOMERS):06d}",
        'first_name': fake.first_name(), 'last_name': fake.last_name(),
        'email': f"{fake.first_name().lower()}.{fake.last_name().lower()}@{random.choice(['gmail.com', 'web.de', 'gmx.de', 't-online.de', 'outlook.de'])}",
        'phone': f"+49 {random.randint(151, 179)} {random.randint(1000000, 9999999)}",
        'title': random.choice(titles), 'department': random.choice(['Privat', 'Verwaltung', 'Technik', 'Einkauf']),
        'lead_source': random.choice(lead_sources), 'campaign_no': random.randint(1, 16000) if random.random() > 0.4 else '',
        'created_date': fake.date_between(start_date=datetime(2021, 1, 1), end_date=datetime(2025, 6, 30)).strftime('%Y-%m-%d')
    })
sf_contacts_df = pd.DataFrame(sf_contacts)
sf_contacts_df.to_csv(f'{OUTPUT_DIR}/sf_contacts.csv', index=False)

print()
print("=" * 60)
print("DATA GENERATION COMPLETE!")
print("=" * 60)
print(f"Output directory: {OUTPUT_DIR}")
print()
print("Generated files:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    if f.endswith('.csv'):
        filepath = os.path.join(OUTPUT_DIR, f)
        rows = sum(1 for _ in open(filepath)) - 1
        print(f"  - {f}: {rows:,} rows")

print()
print("Key Statistics:")
print(f"  - Total Customers: {NUM_CUSTOMERS:,}")
print(f"  - Customers with Heat Pumps: {len(customers_with_heatpumps):,}")
print(f"  - Customers with Solar: {len(customers_with_solar):,}")
print(f"  - Customers with E-Mobility: {len(customers_with_emobility):,}")
print(f"  - Total Contracts: {NUM_CONTRACTS:,}")
print(f"  - Total Service Logs: {NUM_SERVICE_LOGS:,}")
