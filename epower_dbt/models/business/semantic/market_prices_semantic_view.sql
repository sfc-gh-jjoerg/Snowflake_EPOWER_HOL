{{ config(materialized='semantic_view') }}

TABLES (
    PRICES AS {{ ref('stg_day_ahead_prices') }}
        PRIMARY KEY (START_TIME)
        WITH SYNONYMS = ('Strompreise','electricity prices','day-ahead','Boersenpreise','spot prices','Marktpreise','energy market prices')
)

FACTS (
    PRICES.PRICE_EUR_MWH AS PRICE_EUR_MWH
)

DIMENSIONS (
    PRICES.START_TIME AS START_TIME,
    PRICES.END_TIME AS END_TIME,
    PRICES.FETCH_DATE AS FETCH_DATE
)

METRICS (
    PRICES.AVG_PRICE AS AVG(PRICES.PRICE_EUR_MWH),
    PRICES.MAX_PRICE AS MAX(PRICES.PRICE_EUR_MWH),
    PRICES.MIN_PRICE AS MIN(PRICES.PRICE_EUR_MWH)
)
