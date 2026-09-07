# dbt Projects on Snowflake — Concepts Guide

Reference: EPOWER Energy Demo (`epower_dbt/`)

---

## 1. What is dbt?

dbt (data build tool) is a transformation framework. It does **not** extract or load data — it transforms data that's already in your warehouse using SQL SELECT statements. Each SELECT is called a **model** and dbt handles the orchestration: dependency resolution, materialization, testing, and documentation.

On Snowflake, dbt runs **natively** as a first-class object — no external CLI, CI/CD server, or separate compute required.

| Traditional dbt | dbt on Snowflake |
|----------------|-----------------|
| Runs on a local machine or CI server | Runs inside Snowflake (`EXECUTE DBT PROJECT`) |
| Deployed via git + CI/CD | Deployed as a Snowflake object from a Workspace (`CREATE DBT PROJECT`) |
| Scheduled via Airflow, cron, dbt Cloud | Scheduled via Snowflake Tasks |
| Separate access control | Inherits Snowflake RBAC |

---

## 2. Core Concepts

### Models

A **model** is a single `.sql` file containing a SELECT statement. When dbt runs, it wraps that SELECT in a `CREATE TABLE AS SELECT`, `MERGE`, or `CREATE VIEW` depending on the materialization strategy. Models can reference other models with `{{ ref('model_name') }}` — dbt uses these references to build a **DAG** (directed acyclic graph) and run models in the correct dependency order.

In EPOWER, we have 7 models:

```
stg_devices              → fct_epulse_telemetry → mart_vpp_capacity_hourly
                                                → mart_vpp_price_optimization → mart_vpp_cluster_map
stg_day_ahead_prices     → mart_day_ahead_prices ↗
```

### Sources

A **source** is a table that already exists in the warehouse (not created by dbt). Declared in `sources.yml`, referenced in SQL with `{{ source('source_name', 'table_name') }}`. Sources tell dbt where raw data lives without dbt managing it.

EPOWER sources (in `models/sources.yml`):
- `epower_bronze.raw_epulse_iot_telemetry` — raw IoT readings
- `epower_bronze.raw_day_ahead_prices` — raw EPEX API responses
- `epower_bronze.epulse_devices` — device registry
- `epower_gold.customer_dim`, `vpp_cluster_dim`, etc. — pre-loaded dimension tables

### Materializations

How dbt physically stores a model's result in Snowflake:

| Strategy | SQL Generated | When to Use |
|----------|--------------|-------------|
| **table** | `CREATE OR REPLACE TABLE AS SELECT` | Full rebuild every run. Simple, deterministic. Good for small-to-medium tables or when source data can change retroactively. |
| **incremental** | `MERGE INTO target USING (new_rows) ON key` | Only processes new/changed rows. Efficient for large, append-heavy tables. Requires a watermark column and `unique_key`. |
| **view** | `CREATE OR REPLACE VIEW AS SELECT` | No storage cost, recomputed on every query. Good for light transformations. |

EPOWER materialization choices:

| Model | Materialization | Why |
|-------|----------------|-----|
| `stg_devices` | table | Small (~5K rows), device registry rarely changes |
| `fct_epulse_telemetry` | **incremental** | Large (grows ~130K rows/day), append-only source |
| `stg_day_ahead_prices` | **incremental** | Append-only daily price feed |
| `mart_day_ahead_prices` | table | Small (96 rows/day x 66 days), enrichment only |
| `mart_vpp_capacity_hourly` | table | Aggregation reduces millions of rows to ~21K |
| `mart_vpp_price_optimization` | **incremental** | Large result set, append-only when telemetry is incremental |
| `mart_vpp_cluster_map` | table | Small aggregation of price optimization mart |

### Incremental Models — How They Work

An incremental model has three parts:

```sql
-- 1. Config block: tells dbt this is incremental + dedup key
{{ config(materialized='incremental', unique_key='start_time') }}

-- 2. The SELECT: same as any model
SELECT ... FROM {{ source('epower_bronze', 'raw_day_ahead_prices') }} r

-- 3. The filter: only applied on incremental runs (not first run)
{% if is_incremental() %}
WHERE r.fetch_date > (SELECT MAX(fetch_date) FROM {{ this }})
{% endif %}
```

- **First run** (or `--full-refresh`): `is_incremental()` = false, no WHERE filter, full table created
- **Subsequent runs**: `is_incremental()` = true, only new rows selected, then MERGED into existing table using `unique_key`

`{{ this }}` refers to the model's own existing table — dbt uses it to find the watermark (MAX of the timestamp column).

### Tests

Tests are data quality assertions declared in `schema.yml` files:

```yaml
columns:
  - name: customer_key
    tests:
      - unique      # no duplicate values
      - not_null    # no NULLs
```

Run via `EXECUTE DBT PROJECT ... ARGS = 'test'`. Each test generates a SELECT that returns failing rows — if any rows come back, the test fails.

### Macros

Macros are reusable Jinja functions in the `macros/` folder. EPOWER has one critical macro:

**`generate_schema_name.sql`** — overrides dbt's default schema naming. Without it, a model with `+schema: EPOWER_SILVER` would land in `EPOWER_OPS_EPOWER_SILVER` (target schema + custom schema concatenated). The macro makes it land in exactly `EPOWER_SILVER`:

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}          -- no custom schema → use default (EPOWER_OPS)
    {%- else -%}
        {{ custom_schema_name }}     -- custom schema → use it exactly as-is
    {%- endif -%}
{%- endmacro %}
```

---

## 3. Config Files

### `dbt_project.yml` — Project Configuration

The central config file. Defines the project name, paths, and **hierarchical model settings**:

```yaml
name: epower_analytics          # project name (used in model paths)
version: '1.0.0'
profile: default                # which profiles.yml entry to use
model-paths: ["models"]         # where to find .sql model files
macro-paths: ["macros"]         # where to find .sql macro files

models:
  epower_analytics:             # must match project name
    epulse_vpp:                 # folder name → config inheritance
      staging:
        +schema: EPOWER_SILVER  # all models in this folder → EPOWER_SILVER schema
        +materialized: table    # default materialization for this folder
      marts:
        +schema: EPOWER_GOLD
        +materialized: table
    energy_market_data:
      staging:
        +schema: EPOWER_SILVER
        +materialized: incremental
      marts:
        +schema: EPOWER_GOLD
        +materialized: table
```

**Config inheritance**: folder-level settings apply to all models in that folder. A model can override with a `{{ config(...) }}` block in its SQL file (like `fct_epulse_telemetry` overriding from `table` to `incremental`).

### `profiles.yml` — Connection Configuration

Defines how dbt connects to Snowflake:

```yaml
default:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "placeholder"      # replaced at deploy time
      user: "placeholder"         # replaced at deploy time
      role: EPOWER_ROLE
      database: EPOWER_DEMO
      warehouse: EPOWER_COMPUTE
      schema: EPOWER_OPS          # default schema (for models without +schema)
      threads: 4                  # parallel model execution
```

When deployed as a Snowflake object (`CREATE DBT PROJECT`), the connection details are handled by Snowflake itself — the placeholders in `profiles.yml` are overridden by the session context.

### `sources.yml` — Source Declarations

Located at `models/sources.yml`. Maps logical source names to physical Snowflake tables:

```yaml
sources:
  - name: epower_bronze           # logical name used in {{ source('epower_bronze', ...) }}
    database: EPOWER_DEMO
    schema: EPOWER_BRONZE
    tables:
      - name: raw_epulse_iot_telemetry
      - name: raw_day_ahead_prices
      - name: epulse_devices
```

### `schema.yml` — Model Documentation & Tests

One per folder, describes columns and attaches tests:

```yaml
models:
  - name: stg_day_ahead_prices
    description: Day-ahead prices flattened from API JSON (incremental)
    columns:
      - name: start_time
        tests: [unique, not_null]
      - name: price_eur_mwh
        tests: [not_null]
```

---

## 4. Folder Structure

```
epower_dbt/
├── dbt_project.yml                          # Project config (name, paths, materializations)
├── profiles.yml                             # Connection config (role, warehouse, database)
├── macros/
│   └── generate_schema_name.sql             # Schema naming override
└── models/
    ├── sources.yml                          # Source table declarations
    ├── energy_market_data/                  # Domain: electricity market prices
    │   ├── staging/                         # → EPOWER_SILVER schema
    │   │   ├── stg_day_ahead_prices.sql     #   Flatten JSON → 15-min intervals (incremental)
    │   │   └── schema.yml                   #   Tests & docs
    │   └── marts/                           # → EPOWER_GOLD schema
    │       ├── mart_day_ahead_prices.sql    #   Add EUR/kWh, hour_of_day, day_of_week
    │       └── schema.yml
    └── epulse_vpp/                          # Domain: Virtual Power Plant telemetry
        ├── staging/                         # → EPOWER_SILVER schema
        │   ├── stg_devices.sql              #   Device registry + customer context (table)
        │   ├── fct_epulse_telemetry.sql     #   Telemetry + device JOIN (incremental)
        │   └── schema.yml
        └── marts/                           # → EPOWER_GOLD schema
            ├── mart_vpp_capacity_hourly.sql #   Fleet aggregation by region/hour
            ├── mart_vpp_price_optimization.sql # Arbitrage: telemetry x prices (incremental)
            ├── mart_vpp_cluster_map.sql     #   Geographic cluster aggregation
            └── schema.yml
```

**Naming conventions:**
- `stg_` = staging models (clean/enrich raw data)
- `fct_` = fact models (event-grain, typically large)
- `mart_` = mart models (aggregated, business-ready)

**The `models/` folder IS the pipeline definition.** Each `.sql` file is a node in the DAG. The folder hierarchy (`energy_market_data/staging/`, `epulse_vpp/marts/`) determines which config settings from `dbt_project.yml` apply (schema, materialization).

---

## 5. Pipelines

### One project, two pipelines, one convergence point

The EPOWER dbt project contains **two data pipelines** that converge:

**Pipeline 1 — Energy Market Data:**
```
RAW_DAY_AHEAD_PRICES (Bronze, VARIANT JSON)
    → stg_day_ahead_prices (Silver, incremental)
        Flattens JSON arrays via LATERAL FLATTEN
        Converts unix timestamps to TIMESTAMP_NTZ
    → mart_day_ahead_prices (Gold, table)
        Adds EUR/kWh conversion, hour_of_day, day_of_week
```

**Pipeline 2 — VPP Telemetry:**
```
EPULSE_DEVICES + CUSTOMER_DIM (Bronze/Gold sources)
    → stg_devices (Silver, table)
        Enriches device registry with customer name, city, region, cluster

RAW_EPULSE_IOT_TELEMETRY (Bronze)
    → fct_epulse_telemetry (Silver, incremental)
        JOINs raw telemetry with stg_devices for customer context
    → mart_vpp_capacity_hourly (Gold, table)
        Hourly aggregation: solar yield, battery SOC, net grid by region
```

**Convergence — the key business model:**
```
fct_epulse_telemetry + mart_day_ahead_prices
    → mart_vpp_price_optimization (Gold, incremental)
        JOINs telemetry with prices
        Classifies price zones (NEGATIVE/LOW/MEDIUM/HIGH)
        Maps battery actions (MAX_CHARGE/CHARGE/DISCHARGE/SELF_CONSUME)
        Calculates arbitrage margins (70% customer / 30% EPOWER)
    → mart_vpp_cluster_map (Gold, table)
        Geographic cluster aggregation for map visualization
```

### What does each mart model represent?

**`mart_day_ahead_prices`** — An entry represents a single **15-minute price interval** on the German day-ahead electricity market (EPEX Spot, DE-LU bidding zone). Each row contains the delivery date, start/end time of the interval, the wholesale price in both EUR/MWh (market unit) and EUR/kWh (consumer unit), plus derived time dimensions (hour of day, day of week) for pattern analysis. Example question it answers: *"What was the average electricity price on weekday mornings vs weekends?"*

**`mart_vpp_capacity_hourly`** — An entry represents the **aggregated VPP fleet status for one hour in one region and cluster**. It shows how many VPP-enrolled devices were active, their combined and average battery state-of-charge, total and average solar generation, and the net grid flow (positive = fleet is importing from grid, negative = fleet is exporting to grid). Example question: *"How much solar power did the southern cluster generate at noon today, and was the fleet importing or exporting?"*

**`mart_vpp_price_optimization`** — An entry represents **one customer's battery performance for one hour**, joined with the market price for that hour. Each row contains the customer's average solar yield, battery SOC, heat pump consumption, and grid import/export — plus the day-ahead price, a price zone classification (NEGATIVE / LOW / MEDIUM / HIGH), the corresponding battery action (MAX_CHARGE / CHARGE / DISCHARGE / SELF_CONSUME), and the calculated financial impact: import cost, export revenue, net margin, and the 70/30 split between customer and EPOWER. This is the core business model — it quantifies whether the VPP arbitrage strategy is profitable. Example question: *"How much revenue did VPP customers in the Hamburg cluster earn from battery discharge during high-price hours last week?"*

**`mart_vpp_cluster_map`** — An entry represents **one VPP cluster's aggregated status for one hour**. It rolls up `mart_vpp_price_optimization` by geographic cluster, showing active device count, average battery SOC, average solar yield, total grid import/export, net energy flow, and the average market price. Designed for geographic map visualization — each row is one dot on the map at one point in time. Example question: *"Which clusters were net exporters during the price spike yesterday afternoon?"*

### Can a dbt project have multiple pipelines?

Yes. A dbt project is a **collection of models** organized into a single DAG. The DAG can have multiple independent branches (separate pipelines) that may or may not converge. In EPOWER:

- `stg_day_ahead_prices` and `stg_devices` have **no dependency on each other** — they run in parallel
- `mart_vpp_price_optimization` depends on **both** pipeline branches — it's the convergence point
- dbt resolves the full DAG and runs models in the correct order, parallelizing where possible (up to `threads: 4`)

You could split these into two separate dbt projects, but there's no advantage — having them in one project lets dbt manage the cross-pipeline dependency (`mart_vpp_price_optimization` joining data from both branches) automatically.

---

## 6. DAG Visualization

```
  SOURCES (Bronze/Gold)            STAGING (Silver)                 MARTS (Gold)
  =====================            ================                 ===========

  ┌────────────────────┐       ┌─────────────────────┐
  │ epulse_devices     │──────>│ stg_devices         │
  │ customer_dim       │       │   (table)           │
  └────────────────────┘       └─────────┬───────────┘
                                         │
                                         v
  ┌────────────────────┐       ┌─────────────────────┐       ┌─────────────────────────────┐
  │ raw_epulse_iot_    │──────>│ fct_epulse_telemetry│──┬───>│ mart_vpp_capacity_hourly    │
  │ telemetry          │       │   (incremental)     │  │    │   (table)                   │
  └────────────────────┘       └─────────────────────┘  │    └─────────────────────────────┘
                                                        │
                                                        │    ┌─────────────────────────────┐
                                                        ├───>│ mart_vpp_price_optimization │
                                                        │    │   (incremental)             │
  ┌────────────────────┐       ┌─────────────────────┐  │    │                             │
  │ raw_day_ahead_     │──────>│ stg_day_ahead_prices│──┤    │  telemetry x prices         │
  │ prices             │       │   (incremental)     │  │    └──────────────┬──────────────┘
  └────────────────────┘       └──────────┬──────────┘  │                   │
                                          │             │                   v
                                          v             │    ┌─────────────────────────────┐
                               ┌─────────────────────┐  │    │ mart_vpp_cluster_map        │
                               │ mart_day_ahead_     │──┘    │   (table)                   │
                               │ prices (table)      │       └─────────────────────────────┘
                               └─────────────────────┘
```

---

## 7. Deploying & Running on Snowflake

### Deploy from Workspace

```sql
CREATE OR REPLACE DBT PROJECT EPOWER_DEMO.EPOWER_OPS.EPOWER_ANALYTICS_PROJECT
    FROM 'snow://workspace/USER$JOCHEN.PUBLIC."my_workspace"/versions/live/epower_dbt';
```

This reads the dbt project files from a Snowflake Workspace and registers them as a managed object.

### Run & Test

```sql
-- Materialize all models (equivalent to `dbt run`)
EXECUTE DBT PROJECT EPOWER_DEMO.EPOWER_OPS.EPOWER_ANALYTICS_PROJECT ARGS = 'run';

-- Run data quality tests (equivalent to `dbt test`)
EXECUTE DBT PROJECT EPOWER_DEMO.EPOWER_OPS.EPOWER_ANALYTICS_PROJECT ARGS = 'test';

-- Full refresh (rebuild all incremental models from scratch)
EXECUTE DBT PROJECT EPOWER_DEMO.EPOWER_OPS.EPOWER_ANALYTICS_PROJECT ARGS = 'run --full-refresh';
```

### Schedule via Task

```sql
CREATE OR REPLACE TASK EPOWER_DEMO.EPOWER_OPS.TASK_DAILY_DATA_REFRESH
    WAREHOUSE = EPOWER_COMPUTE
    SCHEDULE = 'USING CRON 0 17 * * * Europe/Berlin'
AS
    BEGIN
        CALL EPOWER_DEMO.EPOWER_OPS.FETCH_DAY_AHEAD_PRICES(CURRENT_DATE() + 1);
        CALL EPOWER_DEMO.EPOWER_OPS.GENERATE_DAILY_TELEMETRY();
        EXECUTE DBT PROJECT EPOWER_DEMO.EPOWER_OPS.EPOWER_ANALYTICS_PROJECT ARGS = 'run';
    END;

ALTER TASK EPOWER_DEMO.EPOWER_OPS.TASK_DAILY_DATA_REFRESH RESUME;
```

The task orchestrates the full data lifecycle: **ingest → generate → transform**, running at 17:00 CET daily (after EPEX publishes next-day prices around 13:00 CET).

---

## 8. Key Differences: dbt CLI vs dbt on Snowflake

| Aspect | dbt CLI | dbt on Snowflake |
|--------|---------|-----------------|
| Where code lives | Git repo on local/CI machine | Snowflake Workspace (git-connected) |
| How to deploy | `dbt run` from terminal | `CREATE DBT PROJECT FROM 'snow://workspace/...'` |
| How to execute | `dbt run`, `dbt test` | `EXECUTE DBT PROJECT ... ARGS = 'run'` |
| Compute | Local machine orchestrates, warehouse executes SQL | Warehouse handles everything |
| Scheduling | External (Airflow, cron, dbt Cloud) | Native Snowflake Tasks |
| `profiles.yml` | Real credentials needed | Placeholders — session context used |
| Access control | File-based secrets | Snowflake RBAC (roles, grants) |
| Monitoring | dbt Cloud or external logs | `TASK_HISTORY()`, query history |
