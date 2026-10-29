# Module 4: Cortex Code — Accelerating dbt Development

**Demonstrate how Cortex Code (CoCo) in Snowsight can extend an existing dbt pipeline with new data sources — from raw tables to analytical marts to a natural-language-queryable agent — driven entirely by conversational prompts.**

---

## Motivation

New data sources arrive constantly in any enterprise. A CRM team exports cancellation data. The marketing team starts collecting NPS surveys. The question every data team faces:

> "How fast can we onboard these new sources into our governed analytics pipeline?"

Traditionally this means: analyze the data, understand the schema, design staging models, write SQL transformations, configure dbt, add tests, validate results. Hours of work for a senior data engineer.

With Cortex Code, this becomes a **conversation**. CoCo reads the existing dbt project, understands the conventions, analyzes the new source tables, and generates production-ready dbt models — staging, marts, schema tests — all in minutes.

---

## The Business Case

Two new data domains need to be onboarded into the EPOWER analytics pipeline:

| Source | Description | Rows | Key Metrics |
|--------|-------------|------|-------------|
| **contract_cancellations** | Customer contract cancellations with reasons, retention attempts | ~2,400 | Churn rate, retention success, cancellation reasons |
| **customer_surveys** | NPS satisfaction surveys across 6 categories | 5,000 | NPS score, promoter/detractor ratio, category satisfaction |

Both join naturally with the existing `customer_dim` and `product_dim` — enabling cross-domain analytics like *"Do customers with low NPS scores have higher churn rates?"*

---

## Architecture

```
 EPOWER_BRONZE (Raw)              EPOWER_SILVER (Enriched)          EPOWER_GOLD (Business-Ready)
 ═══════════════════              ════════════════════════          ══════════════════════════════

 contract_cancellations ──►  stg_cancellations ──┬───────────►  mart_customer_churn
                              (+ customer_dim,   │               (by product, region, reason)
                               product_dim)      │
                                                 ├───────────►  mart_customer_health
                                                 │               (combined churn + NPS score)
 customer_surveys ────────►  stg_surveys ────────┼───────────►  mart_nps_analysis
                              (+ customer_dim,   │               (by region, type, category)
                               NPS segment)      │
                                                 └───────────►  mart_customer_health
```

> **Note:** The exact model names and structure may vary depending on what CoCo generates. The above is one expected solution.

---

## What Makes This Module Different

The CoCo prompts in this module are deliberately **business-level**, not prescriptive. Instead of telling CoCo exactly which files to create, join keys to use, or folder structure to follow, the user states the business goal and lets CoCo:

- **Explore** the source tables and discover the schema
- **Analyze** the existing dbt project for conventions
- **Design** the model structure (staging + marts)
- **Generate** SQL, YAML tests, and config updates
- **Create** semantic views and agent tools

This mirrors a realistic workflow where the data engineer knows *what* they want but lets CoCo figure out *how* to implement it.

---

## Snowflake Features Demonstrated

| Feature | Role in This Module |
|---------|-------------------|
| **Cortex Code (CoCo)** | AI-assisted dbt model generation — the star of this module |
| **dbt on Snowflake** | Native dbt project execution via `EXECUTE DBT PROJECT` |
| **Snowsight Workspace** | Integrated IDE where CoCo operates on the dbt project files |
| **Semantic Views** | (Bonus) Extend the agent with customer health analytics |
| **Cortex Agent** | (Bonus) Add new analyst tool for churn + NPS queries |

---

## Notebook Sections

| Section | What we do |
|---------|------------|
| **§1** Prerequisites | Verify Module 1 is deployed |
| **§2** New Source Tables | Create tables for cancellations + surveys |
| **§3** Upload & Ingest | CSV → Stage → COPY INTO → verify |
| **§4** Explore the Data | Quick queries to understand the new sources |
| **§5** The CoCo Challenge | Prompt Cortex Code to extend the dbt pipeline |
| **§6** Verification | Discover and validate what CoCo built |
| **§7** Bonus: AI Layer | Prompt CoCo to create a Semantic View + update the Agent |

---

## Data Design

### contract_cancellations (~2,400 rows)

Churn rates by product category: Electricity 7%, Gas 6%, Solar 2%, etc. German-language cancellation reasons: Umzug, Preiserhöhung, Wettbewerber, Unzufriedenheit, Vertrag abgelaufen, Sonstiges.

| Column | Description |
|--------|-------------|
| `cancellation_id` | Primary key |
| `customer_key` | FK to customer_dim |
| `product_key` | FK to product_dim |
| `cancellation_date` | When the cancellation was processed |
| `reason` | Cancellation reason (German) |
| `channel` | How the cancellation was submitted |
| `retention_offered` | Whether a retention offer was made |
| `retention_accepted` | Whether the customer accepted |

### customer_surveys (5,000 rows)

NPS scores 0-10 across 6 survey categories with German-language comments.

| Column | Description |
|--------|-------------|
| `survey_id` | Primary key |
| `customer_key` | FK to customer_dim |
| `survey_date` | When the survey was completed |
| `nps_score` | 0-10 (0-6 = Detractor, 7-8 = Passive, 9-10 = Promoter) |
| `category` | Survey topic (Gesamtzufriedenheit, Kundenservice, Preis-Leistung, etc.) |
| `comment` | Free-text customer feedback (German) |

---

## Files

| File | Purpose |
|------|---------|
| `hol-module4.ipynb` | Snowsight notebook — the main deliverable |
| `cleanup-module4.sql` | Teardown script to remove Module 4 objects |

---

## CoCo Prompts Used

### Prompt 1: Extend the dbt Pipeline (§5)

```
We just loaded two new tables into EPOWER_DEMO.EPOWER_BRONZE:

- CONTRACT_CANCELLATIONS — tracks when and why customers cancel contracts
- CUSTOMER_SURVEYS — NPS satisfaction surveys with scores and comments

Explore these tables and the existing dbt project, then extend the pipeline
with appropriate staging models and analytical marts. We want to understand
churn patterns and customer satisfaction across our business.
```

### Prompt 2: Create Semantic View (§7)

```
I've just built new mart tables for customer churn and NPS analysis
in EPOWER_GOLD (check what tables exist there with ILIKE '%CHURN%'
or '%NPS%' or '%HEALTH%').
Create a Semantic View called CUSTOMER_HEALTH_SEMANTIC_VIEW in
EPOWER_DEMO.EPOWER_GOLD that covers these marts — include relevant
facts, dimensions, and metrics with German synonyms (this is a
German energy company). Look at the existing semantic views in
EPOWER_GOLD for style reference.
```

### Prompt 3: Update the Agent (§7)

```
Add the new CUSTOMER_HEALTH_SEMANTIC_VIEW as a tool called
customer_health_analyst to the existing EPOWER_AGENT in
EPOWER_DEMO.EPOWER_GOLD. Preserve all existing tools. You can
inspect the current agent definition with DESCRIBE AGENT.
```

---

## Demo Questions for the Agent

| # | Question | What it tests |
|---|----------|---------------|
| 1 | *"What are the top cancellation reasons?"* | Basic churn metric |
| 2 | *"Welche Produktkategorie hat die höchste Kündigungsrate?"* | Category churn (German) |
| 3 | *"What is our overall NPS score?"* | NPS aggregation |
| 4 | *"Compare customer satisfaction between regions"* | Regional NPS comparison |
| 5 | *"How effective are our retention offers?"* | Retention analysis |
| 6 | *"Show me customers with high churn risk and low NPS"* | Cross-domain: churn + NPS combined |

---

## Prerequisites

- Module 1 (`01-agentic-ai-foundation/epower_hol_main.ipynb`) must be fully deployed
- The `epower_dbt` project must exist in your Snowsight workspace
- `EPOWER_ROLE` with appropriate privileges (inherited from Module 1 setup)

---

## How to Run

1. Open `04-dbt-with-cortex-code/hol-module4.ipynb` in the Snowflake Workspace
2. Select the `EPOWER_COMPUTE` warehouse
3. Run §1-§4 to load and explore the new data
4. Follow the CoCo prompts in §5 (in the Snowsight Cortex Code panel)
5. Run §6 to verify what CoCo built
6. (Optional) Follow §7 for Semantic View + Agent extension

**Runtime:** ~15 minutes

---

## Cleanup

Run [`cleanup-module4.sql`](cleanup-module4.sql) in Snowsight (with `EPOWER_ROLE`) to remove all Module 4 objects:

- Source tables in `EPOWER_BRONZE`: `CONTRACT_CANCELLATIONS`, `CUSTOMER_SURVEYS`
- dbt-generated staging models in `EPOWER_SILVER` (e.g., `stg_cancellations`, `stg_surveys`)
- dbt-generated mart tables in `EPOWER_GOLD` (e.g., `mart_customer_churn`, `mart_nps_analysis`, `mart_customer_health`)
- Semantic view: `CUSTOMER_HEALTH_SEMANTIC_VIEW`
- Agent tool: `customer_health_analyst` (removed via `ALTER AGENT ... DROP TOOL`)

> **Note:** The exact objects depend on what Cortex Code generated during §5-§7. The cleanup script uses `IF EXISTS` so it is safe to run even if CoCo chose different model names.

After cleanup, the agent is restored to its Module 3 state (with `portal_analyst`) or Module 1 state (without it, if Module 3 was not deployed).

---

## Relationship to Other Modules

| | Module 1 (01-agentic-ai-foundation) | Module 3 (03-postgres-zero-etl) | Module 4 (04-dbt-with-cortex-code) |
|---|---|---|---|
| **Focus** | Data engineering + Agentic AI | Operational OLTP + zero-ETL | AI-assisted dbt development |
| **Key feature** | dbt, Semantic Views, Cortex Agent | Snowflake Postgres, pg_lake | Cortex Code (CoCo) |
| **Data source** | CSV files, external API | Snowflake Postgres | CSV (cancellations + surveys) |
| **Standalone?** | Yes | Requires Module 1 | Requires Module 1 |
| **Agent tools after** | 12 tools | 13 tools (+portal) | 14 tools (+customer_health) |

---

*EPOWER Module 4 — Cortex Code + dbt — Powered by Snowflake*
