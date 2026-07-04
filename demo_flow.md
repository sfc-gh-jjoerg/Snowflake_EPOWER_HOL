# EPOWER Energy Intelligence Demo — Demo Flow

**EPOWER Energie Deutschland** — 20,000 customers, 360° energy strategy. At the center: the **ePulse Virtual Power Plant (VPP)** with ~4,050 home batteries that charge when electricity is cheap and discharge when it's expensive. Revenue split: 70% customer / 30% EPOWER.

**The Demo Story:** EPOWER has deployed 3 domain-specific AI agents — each tailored to a different team's needs. Instead of one monolithic chatbot that tries to do everything, each team gets a purpose-built assistant that speaks their language, knows their KPIs, and delivers actionable insights.

---

## Act 1 — The Commercial Team's Morning

> **Agent: EPOWER Commercial**
> *Audience: Sales manager reviewing business performance*

### Q1 — Business Overview

> EN: *"Give me an overview of our business: revenue by product category and region, contract values by customer segment."*
>
> DE: *"Überblick über unser Geschäft: Umsatz nach Produktkategorie und Region, Vertragswerte nach Kundensegment."*

| What it shows | Agent routes to `energy_sales_analyst` — a single natural language question generates a multi-dimensional business summary |
|---------------|-----|
| **Insight** | Commercial customers are only 7% of the base but 6x contract value. South dominates solar revenue. East is growing fastest. |

### Q2 — Cross-Domain Customer Intelligence

> EN: *"Which high-consumption customers don't have solar yet? What does our product documentation recommend for them?"*
>
> DE: *"Welche Kunden mit hohem Verbrauch haben noch keine Solaranlage? Was empfiehlt unsere Produktdokumentation?"*

| What it shows | Agent combines SQL (`customer_energy_analyst`) with RAG (`product_docs_search`) in one answer |
|---------------|-----|
| **Insight** | North customers appear disproportionately (lowest solar adoption) — regional sales opportunity. Agent synthesizes data + documents. |

### Q3 — Service Quality Check

> EN: *"Which regions have the most negative service tickets? Derive concrete actions."*
>
> DE: *"Welche Regionen haben die meisten negativen Service-Tickets? Leite konkrete Maßnahmen ab."*

| What it shows | Agent goes beyond data reporting — delivers recommendations, not just numbers |
|---------------|-----|
| **Insight** | East stands out (installation growing pains). Winter peak in heat pump complaints visible. Agent proposes actions. |

---

## Act 2 — The Operations Team's Control Room

> **Agent: EPOWER Operations**
> *Audience: Energy trader monitoring the VPP fleet*

### Q4 — Price-Battery Correlation (the "Wow" Moment)

> EN: *"Show electricity spot price vs. battery state-of-charge for the last 7 days. Is the VPP reacting to the market?"*
>
> DE: *"Zeige Strompreis vs. Batterie-Ladezustand der letzten 7 Tage. Reagiert das VPP auf den Markt?"*

| What it shows | Agent correlates two data sources (VPP telemetry + market prices) and visualizes the relationship |
|---------------|-----|
| **Insight** | Inverse correlation as a chart — proof that 4,050 batteries autonomously react to real EPEX prices. The VPP works. |

### Q5 — Regional Cluster Deep-Dive

> EN: *"Compare average solar yield and net grid flow between Munich Metro, Hamburg Metro, and Rhein-Ruhr clusters. Which cluster exports the most?"*
>
> DE: *"Vergleiche die durchschnittliche Solarleistung und den Netzfluss zwischen den Clustern Munich Metro, Hamburg Metro und Rhein-Ruhr. Welches Cluster exportiert am meisten?"*

| What it shows | Agent uses `CLUSTER_NAME` and `COMPASS_REGION` dimensions — granular fleet analytics down to metro-region level |
|---------------|-----|
| **Insight** | Southern clusters (high solar irradiation) are net exporters; northern clusters (wind-heavy, lower solar) import more. Urban vs. rural performance gap visible. |

**Follow-up options:**
- EN: *"Which cluster has the highest heat pump consumption?"* / DE: *"Welches Cluster hat den höchsten Wärmepumpenverbrauch?"*
- EN: *"Compare battery SOC between urban and rural clusters"* / DE: *"Vergleiche den Batterie-Ladezustand zwischen urbanen und ländlichen Standorten"*
- EN: *"What does the VPP program guide say about dispatch priorities?"* / DE: *"Was sagt das VPP-Programm über Dispatch-Prioritäten?"* (triggers RAG)

---

## Act 3 — The HR Partner's Check-In

> **Agent: EPOWER People**
> *Audience: HR business partner reviewing workforce metrics*

### Q6 — Workforce Snapshot

> EN: *"How is our attrition rate distributed across departments? Which teams should I focus on?"*
>
> DE: *"Wie verteilt sich unsere Fluktuationsrate über die Abteilungen? Auf welche Teams sollte ich mich konzentrieren?"*

| What it shows | A completely separate agent with its own persona — demonstrates data isolation and specialized vocabulary |
|---------------|-----|
| **Insight** | Agent speaks HR language (attrition rate, FTE, span of control). Identifies high-risk departments and suggests retention analysis. |

---

## Act 4 — The Boardroom (All Agents Converge)

> **Agent: EPOWER Intelligence (monolithic)**
> *Audience: Executive wanting a cross-domain summary*

### Q7 — Executive Strategy

> EN: *"Executive summary: revenue trends, VPP performance, customer satisfaction, and workforce — with three actions for next quarter."*
>
> DE: *"Executive Summary: Umsatz, VPP-Performance, Kundenzufriedenheit, Personal — und drei Maßnahmen fürs nächste Quartal."*

| What it shows | The monolithic agent orchestrates across 5 tools in one answer — demonstrating why both patterns (focused + broad) have value |
|---------------|-----|
| **Insight** | Agent aggregates sales, VPP, service, and HR data into a strategic recommendation. Shows that the monolith is still valuable for cross-cutting questions that span multiple domains. |

---

## Summary

| # | Agent | Domains | Cross-Domain | RAG | Action-Oriented |
|---|-------|---------|:---:|:---:|:---:|
| 1 | Commercial | Sales, Customers | | | |
| 2 | Commercial | Customers, Product Docs | x | x | |
| 3 | Commercial | Service | | | x |
| 4 | Operations | VPP, Market Prices | x | | |
| 5 | Operations | VPP (Clusters) | | | |
| 6 | People | HR | | | |
| 7 | Intelligence | Sales, VPP, Service, HR | x | x | x |

---

## Demo Tips

- **Start with Commercial** (Q1-Q3) — it's the most relatable business context
- **Q4 is the "wow" moment** — the price/battery chart proves the VPP works with real market data
- **Switch agents visibly** — the transition from Commercial → Operations → People tells the story of "right agent for the right team"
- **Q7 wraps up** — the monolith shows both patterns have value; focused agents for daily work, broad agent for executive synthesis
- **Language flexibility** — ask in English or German mid-demo to show the agent adapts seamlessly (no configuration needed)
- **Follow-ups** after any question: "Break down by region" / "Aufschlüsselung nach Region", "Show as chart" / "Zeige als Chart", "Explain the VPP program" / "Erkläre das VPP-Programm" (triggers RAG)

---

## Technical Components

| Component | Details |
|-----------|---------|
| **Agents** | 4 total: `EPOWER_AGENT` (12 tools), `EPOWER_OPS_AGENT` (4), `EPOWER_COMMERCIAL_AGENT` (8), `EPOWER_PEOPLE_AGENT` (2) |
| **Semantic Views** | 7 (Sales, Billing, Service, Customer Energy, HR, VPP Telemetry, Market Prices) |
| **Cortex Search** | 9 services (4 document RAG + 5 column lookup) |
| **Database** | `EPOWER_DEMO` (Medallion: Bronze → Silver → Gold) |
| **MCP Server** | `EPOWER_MCP_SERVER` (15 tools) |

---

## Data Characteristics

| Dimension | Expected Pattern |
|-----------|-----------------|
| **Regions** | South = Solar champion, North = Heat pump-strong, West = E-Mobility/Commercial, East = Growth + installation challenges |
| **VPP Clusters** | 14 metro/rural clusters. Urban: higher device density. Rural: higher solar yield per device. |
| **Segments** | Commercial: 6x contract value, 3-6 contracts. Residential: 1-3 contracts |
| **Time Trends** | YoY growth, solar peak in spring, heat pump peak in autumn |
| **Service** | East: negative sentiment cluster. Winter: heat pump complaints +80% |

---

*EPOWER Energy Intelligence Demo — Powered by Snowflake Cortex*
