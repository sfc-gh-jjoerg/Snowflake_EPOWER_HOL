# Module 3: Snowflake Postgres — Customer Self-Service Portal

**Extend the EPOWER demo with a transactional Postgres backend, connected to Snowflake analytics via pg_lake and Apache Iceberg.**

---

## Motivation

The EPOWER base demo (Module 1) is purely analytical: data lives in Snowflake, transformed by dbt, queried by the Intelligence Agent. But real enterprises don't start with analytics — they start with **operational systems** that generate data. The question every data team faces:

> "How do we get data from our application databases into our analytical platform — without building and maintaining ETL pipelines?"

Module 3 answers this with Snowflake Postgres + pg_lake: a managed PostgreSQL that natively writes Apache Iceberg tables, readable by Snowflake without any middleware.

---

## The Business Case: "Mein EPOWER"

Every energy retailer in Germany needs a digital customer portal. Regulatory requirements (Marktkommunikation, BDEW processes) and customer expectations demand self-service: meter readings, tariff management, billing inquiries, and program enrollments.

**"Mein EPOWER"** is the customer-facing web application serving 20,000 residential and business customers. It handles:

| Feature | What Customers Do |
|---------|------------------|
| **Meter Readings** | Submit monthly electricity and gas meter readings (Zählerstandsmeldung) |
| **Tariff Switching** | Request product changes (e.g., Strom Basis → Ökostrom 100%) |
| **Service Requests** | Open support tickets, report issues, ask billing questions |
| **VPP Enrollment** | Sign up for (or opt out of) the EPOWER Virtual Power Plant program |
| **Account Management** | Update preferences, change notification settings, view history |

---

## Why Postgres?

### The Standard Web Application Pattern

The portal uses the most common backend architecture in software:

```
Browser → React Frontend → REST API (Node.js / Python) → PostgreSQL
```

This pattern is used by millions of applications worldwide — from startups to enterprises. PostgreSQL is the #1 choice for web application backends because it provides:

- **Low-latency point reads** — "Show my last 6 meter readings" returns in <10ms
- **ACID transactions** — A tariff switch either completes fully or rolls back entirely
- **Constraint enforcement** — A meter reading cannot be lower than the previous one
- **Concurrent access** — Hundreds of customers using the portal simultaneously
- **Row-level locking** — Two processes updating the same order don't conflict
- **Session management** — Login state, CSRF tokens, preferences with millisecond reads

### Why Not Snowflake for the Portal Backend?

Snowflake is designed for **analytical workloads**: scanning millions of rows, aggregating data, running complex joins across large datasets. It is not designed for:

- Sub-second single-row lookups by primary key
- Hundreds of concurrent INSERT/UPDATE operations per second
- Mutable state with frequent row-level changes
- Session management requiring millisecond response times
- Constraint-checked form submissions

**Both are needed.** Postgres handles the operational workload; Snowflake handles the analytical workload. The bridge between them is pg_lake.

---

## Architecture

### Data Flow

```
Customer (Browser)
    │
    ▼
React Frontend
    │
    ▼
REST API (application server)
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│  SNOWFLAKE POSTGRES                                           │
│                                                               │
│  Operational Tables          Activity Log                     │
│  ┌──────────────────┐       ┌───────────────────────────┐    │
│  │ portal_users     │       │ portal_activity_log       │    │
│  │ meter_readings   │ ───►  │ (append-only: one row     │    │
│  │ tariff_orders    │       │  per user action)         │    │
│  │ service_requests │       └─────────────┬─────────────┘    │
│  └──────────────────┘                     │                   │
│                               pg_incremental (every 1 min)    │
│                                           ▼                   │
│                               ┌───────────────────────┐       │
│                               │ Iceberg table         │       │
│                               │ (object storage)      │       │
│                               └───────────┬───────────┘       │
└───────────────────────────────────────────┼───────────────────┘
                                            │
                                 Catalog Integration
                                 (auto-refresh 30s)
                                            ▼
┌───────────────────────────────────────────────────────────────┐
│  SNOWFLAKE                                                    │
│                                                               │
│  EPOWER_BRONZE                                                │
│  └── PORTAL_ACTIVITY_LOG (Iceberg table)                      │
│              │                                                │
│              ▼                                                │
│  EPOWER_GOLD                                                  │
│  └── MART_PORTAL_ENGAGEMENT (daily metrics)                   │
│              │                                                │
│              ▼                                                │
│  PORTAL_SEMANTIC_VIEW → Cortex Agent (portal_analyst tool)    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### What Stays in Postgres vs. What Flows to Snowflake

| Data | Stays in Postgres? | Flows to Snowflake? | Reasoning |
|------|-------------------|--------------------| ----------|
| User sessions & auth | ✅ | ❌ | Ephemeral, security-sensitive, no analytical value |
| Meter readings (transactional) | ✅ | ❌ | Billing pipeline already feeds Snowflake; portal is just the input channel |
| Tariff orders (mutable state) | ✅ | ❌ | Status changes frequently; Postgres handles the lifecycle |
| Service requests (mutable) | ✅ | ❌ | Open/closed status managed in Postgres |
| **Portal activity log** | ✅ | **✅** | Append-only, denormalized, time-partitioned — perfect for Iceberg |

The activity log is deliberately designed as the **analytics export layer**: every user action generates one immutable, self-contained record with all context (customer, region, type, timestamp, details). It never needs to be updated, making it ideal for incremental replication.

---

## Snowflake Platform Features

### Snowflake Postgres

Fully managed PostgreSQL running inside the Snowflake platform.

- **No infrastructure**: No EC2 instances, no RDS, no patching, no backup configuration
- **Standard connectivity**: Any Postgres client works — `psql`, JDBC, SQLAlchemy, Django ORM, Rails ActiveRecord
- **Auto-suspend/resume**: Saves credits when the portal has no traffic
- **Integrated**: Lives in the same account as your Snowflake warehouse, governed by the same RBAC

### pg_lake

Open-source Postgres extension (Apache 2.0 license) created by the Crunchy Data team (now at Snowflake). It adds native Iceberg support to Postgres:

```sql
-- Create an Iceberg table — data stored in object storage, metadata in Postgres
CREATE TABLE my_analytics_table (
    id BIGINT,
    event_time TIMESTAMPTZ,
    payload JSONB
) USING iceberg;
```

Key capabilities:
- **Postgres acts as the Iceberg catalog** — no external catalog service needed
- **Full Postgres transaction semantics** — writes to Iceberg are transactional
- **Standard SQL** — INSERT, COPY, and queries work as expected
- **Query external data** — read Parquet, CSV, JSON directly from S3/Azure/GCS

### pg_incremental

Automated incremental pipelines inside Postgres:

```sql
SELECT incremental.create_time_interval_pipeline(
    pipeline_name   := 'sync_to_iceberg',
    time_interval   := '1 minute',
    source_table    := 'activity_log',
    start_time      := (SELECT min(event_time) FROM activity_log),
    command         := $$
        INSERT INTO activity_log_iceberg
        SELECT * FROM activity_log
        WHERE event_time >= $1 AND event_time < $2
    $$
);
```

Key properties:
- **Exactly-once semantics** — each time interval is processed once, no duplicates
- **Backfill on creation** — processes all historical intervals immediately
- **Continuous** — after backfill, processes new intervals as they complete
- **Built on pg_cron** — no external scheduler needed

### Catalog Integration

Snowflake connects to the Postgres-managed Iceberg catalog:

```sql
CREATE CATALOG INTEGRATION my_postgres_catalog
  CATALOG_SOURCE    = SNOWFLAKE_POSTGRES
  TABLE_FORMAT      = ICEBERG
  CATALOG_NAMESPACE = 'public'
  REST_CONFIG = (
    POSTGRES_INSTANCE = 'MY_INSTANCE'
    CATALOG_NAME      = 'postgres'
  )
  ENABLED = TRUE;
```

Then create an Iceberg table that reads from it:

```sql
CREATE ICEBERG TABLE my_snowflake_table
    CATALOG = 'my_postgres_catalog'
    CATALOG_TABLE_NAME = 'my_iceberg_table_in_postgres';

ALTER ICEBERG TABLE my_snowflake_table SET AUTO_REFRESH = TRUE;
```

### The Zero-ETL Value Proposition

Traditional approach:
```
Postgres → CDC tool (Debezium) → Kafka → Connector → Staging → dbt → Analytics
```

With Snowflake Postgres + pg_lake:
```
Postgres → pg_lake (Iceberg) → Snowflake reads directly
```

No Kafka, no Debezium, no Fivetran, no Airbyte, no staging tables, no scheduled extracts. The data flows through open standards (Iceberg/Parquet on object storage) with no proprietary middleware.

---

## Data Model

### Portal Schema (Postgres)

```sql
-- Mutable operational tables (serve the web application)
portal_users          -- 20K rows, frequent UPDATEs (last_login, preferences)
meter_readings        -- ~15K rows/month, INSERT with validation
tariff_orders         -- ~3K rows/month, status lifecycle
service_requests      -- ~5K rows/month, open/close tracking

-- Analytics export (append-only, replicated to Snowflake)
portal_activity_log   -- ~60K rows/60 days, one per user action
```

### Activity Log Schema

Each portal action produces one log entry:

| Column | Type | Description |
|--------|------|-------------|
| `activity_id` | BIGSERIAL | Auto-incrementing primary key |
| `customer_key` | INT | Links to customer_dim in Snowflake |
| `event_time` | TIMESTAMPTZ | When the action occurred |
| `event_type` | TEXT | LOGIN, METER_READING, TARIFF_CHANGE, SERVICE_REQUEST |
| `event_detail` | JSONB | Flexible payload (meter value, product name, ticket subject) |
| `city` | TEXT | Denormalized for analytics (no joins needed in Snowflake) |
| `region` | TEXT | Nord, Süd, West, Ost |
| `customer_type` | TEXT | Privatkunde, Kleingewerbe, Gewerbekunde |

### Gold Layer (Snowflake)

The `MART_PORTAL_ENGAGEMENT` table aggregates daily:

| Column | Description |
|--------|-------------|
| `activity_date` | Day |
| `region` | Geographic region |
| `customer_type` | Customer segment |
| `event_type` | Action type |
| `event_count` | Total events |
| `unique_customers` | Distinct active customers |

---

## Demo Questions

After deployment, the Intelligence Agent can answer portal engagement questions using the `portal_analyst` tool:

| Question | What It Tests |
|----------|---------------|
| "How many customers used the portal this week?" | Basic engagement |
| "Welche Region hat die höchste Portal-Nutzung?" | Regional comparison (German) |
| "Show me the trend of meter reading submissions over the last 30 days" | Time-series |
| "What are the most popular tariff switches?" | Tariff change analysis |
| "Compare portal engagement between residential and business customers" | Segment comparison |
| "Which customers submit meter readings but never changed their tariff?" | Cross-tool (portal + sales) |

---

## Prerequisites

- Module 1 (`epower_hol_main.ipynb`) must be fully deployed
- Snowflake Postgres must be enabled in your account
- `EPOWER_ROLE` with appropriate privileges (inherited from Module 1 setup)

---

## How to Run

1. Open `03-postgres-zero-etl/hol-module3.ipynb` in the Snowflake Workspace
2. Select the `EPOWER_COMPUTE` warehouse
3. **Run All** cells (~10 minutes)

The notebook creates the Postgres instance, seeds data, sets up pg_lake replication, connects Snowflake via catalog integration, builds the Gold mart and Semantic View, and updates the Intelligence Agent.

---

## Relationship to Module 1

| | Module 1 (epower_hol_main.ipynb) | Module 3 (hol-module3.ipynb) |
|---|---|---|
| **Focus** | Data engineering + Agentic AI | Operational OLTP + zero-ETL replication |
| **Data source** | CSV files, external API | Snowflake Postgres (web app backend) |
| **Key Snowflake features** | dbt, Semantic Views, Cortex Agent, Cortex Search | Snowflake Postgres, pg_lake, Iceberg, Catalog Integration |
| **Standalone?** | Yes | No — requires Module 1 for customer/product data |
| **Runtime** | ~15 minutes | ~10 minutes |
| **Agent tools after** | 12 tools (7 analyst + 4 search + chart) | 13 tools (+portal_analyst) |

---

## Cleanup

Module 3 has **dependency constraints** that require a specific cleanup order. A network policy attached to a Postgres instance cannot be dropped until it is explicitly detached.

**Option A: Use the cleanup notebook** (recommended)

1. Run Postgres cleanup first (in psql):
   ```bash
   psql service=my_epower_portal -f cleanup-module3-postgres.sql
   ```
2. Open `cleanup-module3.ipynb` in the Workspace and run all cells

**Option B: Use the SQL script**

1. Run `cleanup-module3-postgres.sql` in psql
2. Run `cleanup-module3-snowflake.sql` in Snowsight (requires ACCOUNTADMIN)

**Dependency order (critical):**

| Step | Action | Why |
|------|--------|-----|
| 1 | Drop data objects (Iceberg table, mart table, semantic view, stage) | No dependencies — safe to drop first |
| 2 | Drop catalog integration | References the Postgres instance |
| 3 | Detach network policy: `ALTER POSTGRES INSTANCE MY_EPOWER_PORTAL UNSET NETWORK_POLICY` | **Must happen before step 5** |
| 4 | Drop Postgres instance | Irreversible — all Postgres data is deleted |
| 5 | Drop network policy and network rule | Only works after detaching in step 3 |
| 6 | Restore agent to Module 1 state | Removes `portal_analyst` tool |

> **Common error:** `"Policy EPOWER_PG_POLICY cannot be dropped as it is associated with one or more entities"` — you need to detach the policy from the Postgres instance first (step 3). The cleanup notebook handles this automatically with an exception-safe `BEGIN...END` block.

**Post-cleanup:** Also remove the psql connection configuration:

```bash
# Remove from ~/.pg_service.conf: the [my_epower_portal] section
# Remove from ~/.pgpass: the corresponding line
```

---

## References

- [Introducing pg_lake](https://www.snowflake.com/en/engineering-blog/pg-lake-postgres-lakehouse-integration/) — Snowflake Engineering Blog
- [Sync Data from Postgres to Snowflake with Iceberg and pg_lake](https://www.snowflake.com/en/developers/guides/sync-data-from-postgres-to-snowflake-with-iceberg-and-pg-lake/) — Developer Guide
- [pg_lake GitHub Repository](https://github.com/Snowflake-Labs/pg_lake) — Source code (Apache 2.0)
- [Building a True Lakehouse with Snowflake Postgres and pg_lake](https://medium.com/snowflake/building-a-true-lakehouse-via-snowflake-postgres-and-pg-lake-4c798c6fe5f7) — Tutorial

---

*EPOWER Module 3 — Snowflake Postgres + pg_lake — Powered by Snowflake*
