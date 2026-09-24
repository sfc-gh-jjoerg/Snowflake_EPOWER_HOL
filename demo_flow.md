# EPOWER Energy Intelligence Demo — Demo Flow

**EPOWER** is a German energy provider with 20,000 customers pursuing a 360-degree energy strategy: Supply, Generate, Store, Heat, Drive, Optimize. The centerpiece is the **EPOWER Virtual Power Plant (VPP)** — ~4,050 residential battery systems that charge when electricity is cheap and discharge when prices are high. Revenue is split 70% customer / 30% EPOWER.

**Duration:** 15-20 minutes | **Agent:** `EPOWER_AGENT` in Snowflake Intelligence (Cowork)

---

## Act 1 — Enterprise Intelligence in Cowork (~10 min)

> Open **Snowflake Intelligence** (Cowork) and select `EPOWER_AGENT`.
> The monolithic agent has 12 tools spanning sales, billing, service, HR, VPP fleet, energy market, and document search.

### Q1 — Business Overview

> EN: *"Revenue overview by product category — which verticals are growing fastest?"*
>
> DE: *"Umsatzuebersicht nach Produktkategorie — welche Bereiche wachsen am staerksten?"*

| What it shows | The agent routes to `energy_sales_analyst`, generates a chart from natural language |
|---------------|---|
| **Talking point** | "One question, one chart — no SQL, no dashboard builder. The semantic view defines the business vocabulary; the agent translates intent to precise SQL." |
| **Expected insight** | Solar and battery storage lead revenue. Commercial customers are only 7% of the base but drive ~6x contract value. |

### Q2 — VPP Financial Performance (New Capability)

> EN: *"Show the VPP fleet margin by price zone — is our arbitrage strategy profitable?"*
>
> DE: *"Zeige die VPP-Marge nach Preiszone — ist unsere Arbitrage-Strategie profitabel?"*

| What it shows | Routes to `vpp_analyst` — the enriched semantic view now includes financial metrics (margins, costs, revenue) alongside telemetry |
|---------------|---|
| **Talking point** | "The VPP semantic view combines telemetry AND price optimization data. One tool answers both operational and financial questions about the fleet." |
| **Expected insight** | HIGH price zone has highest export revenue and positive margins. NEGATIVE zone shows high import (charging) at zero or negative cost — the fleet charges when producers pay us to take electricity. |

### Q3 — The "Wow" Chart (German, Real Market Data)

> *"Zeige Strompreis vs. Batterie-Ladezustand der letzten 7 Tage als Chart"*
>
> (Switch to German mid-demo — the agent adapts seamlessly)

| What it shows | Dual-axis chart with real EPEX day-ahead prices and battery SOC. Visible inverse correlation. |
|---------------|---|
| **Talking point** | "These are real electricity prices from the EPEX DE-LU market, fetched daily via API. 4,050 home batteries autonomously react to market signals — high prices, low SOC (discharging); low prices, high SOC (charging). The VPP works." |
| **Expected insight** | Clear inverse pattern. The agent produces the chart AND explains the correlation in German. |

### Q4 — Cross-Domain Intelligence (SQL + RAG)

> EN: *"Which high-consumption customers without solar have the most negative service tickets? What does our product documentation recommend for upsell?"*
>
> DE: *"Welche Kunden mit hohem Verbrauch ohne Solar haben die meisten negativen Service-Tickets? Was empfiehlt unsere Produktdokumentation?"*

| What it shows | Agent invokes 3 tools in one answer: `customer_energy_analyst` (consumption by product), `service_analyst` (ticket sentiment), `product_docs_search` (RAG over product guides) |
|---------------|---|
| **Talking point** | "This is the real power of agentic AI — the agent doesn't just query a table. It combines structured data from two different sources AND retrieves relevant product documentation to build a recommendation. SQL + RAG in one answer." |
| **Expected insight** | North region appears disproportionately (lowest solar adoption). Agent synthesizes a recommendation combining data patterns with product documentation. |

### Q5 — Executive Summary (Cross-Domain Closer)

> *"Executive summary: Umsatz, VPP-Performance, Servicelage — mit drei konkreten Massnahmen fuers naechste Quartal"*

| What it shows | Agent orchestrates 4+ tools (sales, VPP, service, HR) into a strategic recommendation |
|---------------|---|
| **Talking point** | "One question, five data domains, three concrete actions. This is what a purpose-built enterprise agent can do — not just analytics, but strategy." |
| **Expected insight** | Revenue growth in solar, VPP margins positive, service quality improving. Actions: expand solar in North, optimize VPP dispatch in low-price clusters, address East region installation complaints. |

---

## Act 2 — VPP Monitor Dashboard (~5 min)

> Switch to the **VPP Monitor** app (Module 2). Open the URL from `SHOW APPLICATION SERVICES` or the Snowflake Apps section.

### What to Show

1. **Geographic cluster map** — 14 VPP clusters across Germany, color-coded by net energy flow. Export clusters (green) vs. import clusters (red).
2. **Timeseries view** — hourly battery SOC, solar yield, and grid flow overlaid with electricity prices. Same correlation as Q3 but as a dedicated operational dashboard.
3. **Action breakdown** — CHARGE/DISCHARGE/SELF_CONSUME distribution by cluster.

### Talking Points

- "This is a **Next.js app deployed via Snowflake App Runtime** — `snow app deploy`, no Docker images, no container registry, no CI/CD pipeline. From code to live URL in one command."
- "It queries the **same Gold layer** the agent uses — same dbt models, same semantic consistency. Different UX for different users: the operations team needs a dashboard, the executive asks Cowork."
- "The 4 backend views powering this dashboard are **managed by dbt** alongside the data models — one `dbt run` builds everything."

---

## Act 3 — Behind the Scenes (3-5 min, optional)

> Quick technical walkthrough for deeper audiences. Show the notebook or explain the architecture verbally.

### Key Architecture Points

| Layer | What | How |
|-------|------|-----|
| **Data Pipeline** | Bronze -> Silver -> Gold (medallion) | dbt on Snowflake — `EXECUTE DBT PROJECT` |
| **Semantic Layer** | 7 semantic views (all domains) | dbt `semantic_view` materialization via `dbt_semantic_view` package |
| **Two-Phase dbt** | Tables first, semantic views second | `--exclude tag:semantic` then `--select tag:semantic` (search services must exist first) |
| **AI Layer** | 4 agents (1 monolithic + 3 domain-specific) | Cortex Agent with text-to-SQL + RAG tools |
| **Search** | 9 Cortex Search services | 4 document RAG + 5 high-cardinality column lookup |
| **Daily Refresh** | Prices + telemetry + sales + billing + service + dbt | Snowflake Task at 17:00 CET |
| **External Access** | MCP Server with 15 tools | Cortex Code, Claude Desktop, external AI clients |
| **Enterprise Sources** | Customer data (Salesforce), billing (SAP), HR (Workday) | Zero-copy connectors / Openflow CDC (simulated in lab) |

### For Hands-on Lab Participants

The notebook (`01-agentic-ai-foundation/epower_hol_main.ipynb`) walks through each layer step by step:

| Section | What you learn |
|---------|---------------|
| 1-2 | Snowflake role-based access, warehouse setup |
| 3 | Star schema data model, dimension/fact tables |
| 4 | External API access from Snowflake (Energy-Charts API) |
| 5 | IoT data generation with price-reactive patterns |
| 6 | dbt on Snowflake — native dbt, package management, two-phase execution |
| 7 | Cortex Search + Semantic Views — the AI-ready layer |
| 8 | Document parsing and RAG pipeline |
| 9 | Cortex Agent architecture — monolithic vs. domain-specific |
| 10 | MCP Server — exposing AI capabilities to external tools |
| 11 | Task scheduling and incremental data refresh |

---

## Demo Tips

- **Q3 is the "wow" moment** — the price/battery chart proves the VPP works with real market data. Time your pause here.
- **Switch to German for Q3 and Q5** — it's natural for a German energy company and shows the agent adapts without configuration.
- **Q4 is the "enterprise AI" moment** — SQL + RAG in one answer. Emphasize that no pre-built dashboard could do this.
- **Don't over-explain the technical stack** during Act 1 — let the questions speak. Save architecture for Act 3 or follow-up.
- **Follow-up prompts** after any question: "Break this down by region" / "Zeige das als Chart" / "What does the VPP program guide say about this?" (triggers RAG)

---

## Data Characteristics (for Q&A)

| Dimension | Pattern |
|-----------|---------|
| **Regions** | South = solar champion, North = heat pump-strong, West = commercial/e-mobility, East = fastest growth + installation challenges |
| **VPP Clusters** | 14 metro/rural clusters. Urban: higher density. Rural: higher solar yield per device |
| **Customer Segments** | Commercial: 6x contract value (7% of base). Residential: 1-3 contracts |
| **Price Zones** | NEGATIVE (charge for free), LOW (charge), MEDIUM (self-consume), HIGH (discharge for profit) |
| **Battery Actions** | MAX_CHARGE, CHARGE, SELF_CONSUME, DISCHARGE — mapped to price zones |
| **Margin Split** | 70% customer / 30% EPOWER — visible in VPP financial metrics |

---

*EPOWER Energy Intelligence Demo — Powered by Snowflake*
