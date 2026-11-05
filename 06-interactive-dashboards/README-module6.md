# Module 6 — Interactive Dashboards with Cortex Code

**Build a two-tab, click-to-explore EPOWER dashboard by talking to Cortex Code. No code, no BI tool, no extracts.**

| | |
|---|---|
| **Prerequisite** | Module 1 completed (semantic views in `EPOWER_DEMO.EPOWER_GOLD`) |
| **Where** | Snowsight » Projects » Workspaces (CoCo in Snowsight) |
| **Role / Warehouse** | `EPOWER_ROLE` / `EPOWER_COMPUTE` |
| **Time** | ~10 min build, ~5 min demo |
| **Feature status** | Snowflake Dashboards — Preview (open to all accounts) |

---

## What Are Snowflake Dashboards?

Snowflake Dashboards are an AI-first BI artifact native to Snowflake:

- **AI-first creation** — describe the dashboard to Cortex Code; it generates tiles, SQL, layout, filters and interactions into a `.dash` file in your Workspace.
- **Interactive charts (chart actions)** — click a bar and the rest of the dashboard filters or highlights to match.
- **Conversational consumption** — viewers open the published dashboard in CoWork and ask follow-up questions on any tile.
- **Native governance** — tiles run live against the warehouse with the *viewer's* privileges (caller's rights). No license, no extract.

### Building Blocks

| Concept | What it is |
|---|---|
| **Tile** | One SQL query rendered as chart (Vega-Lite), table, or markdown. 12-column grid. |
| **Tab** | Named view with its own tiles; filters span all tabs. Only the open tab's queries run. |
| **Filter** | Viewer-side row constraint. Wired into tile SQL via `{{ filter('name') }}`; values are bound as parameters (no SQL injection). |
| **Cascading filter** | Linked dropdowns (Region → Cluster); created via CoCo. |
| **Chart action** | Click/drag interaction: **Filter** (re-runs targets), **Highlight** (dims, instant), Drill-down (early dev). Only via CoCo. |
| **Artifact** | Read-only published copy of the `.dash`, shared with roles, opened in CoWork or Snowsight. |

### Two Rules That Shape This Module

1. **Chart actions only connect tiles that query the same table/view.** Each tab therefore builds on one source: VPP tab → `EPULSE_VPP_SEMANTIC_VIEW`, Commercial tab → `ENERGY_SALES_SEMANTIC_VIEW`.
2. **The VPP semantic view has two unrelated entities** — telemetry (SOC, solar, grid import/export, by `TS`) and price optimization (margins, price, battery action, by `HOUR`). A single tile cannot mix metrics from both. The prompts below keep them in separate tiles.

---

## Build Prompts

Open a Workspace, select **Create » Dashboard** (or start a CoCo chat in the Workspace) and paste the prompts in order. Review each result before the next prompt.

### P1 — Scaffold

```text
Create a dashboard called "EPOWER Energy Command Center" with two tabs:
"VPP Control Room" (default) and "Commercial Pulse".
Use role EPOWER_ROLE and warehouse EPOWER_COMPUTE.
Start each tab with a short markdown header explaining what the tab shows.
```

### P2 — VPP Control Room tiles

```text
On the "VPP Control Room" tab, use only the semantic view
EPOWER_DEMO.EPOWER_GOLD.EPULSE_VPP_SEMANTIC_VIEW. Note: telemetry metrics
(AVG_BATTERY_SOC, TOTAL_GRID_IMPORT, TOTAL_GRID_EXPORT, TOTAL_SOLAR_YIELD) and
price-optimization metrics (TOTAL_VPP_MARGIN, TOTAL_EPOWER_MARGIN, AVG_PRICE,
ACTIVE_VPP_CUSTOMERS) are separate entities - never combine them in one tile.
Add these tiles:
1. Scorecards: Total VPP margin (EUR), EPOWER share (EUR), Active VPP customers,
   Average battery SOC (%).
2. "Margin by cluster": horizontal bar of TOTAL_VPP_MARGIN by CLUSTER_NAME, sorted desc.
3. "Margin by battery action": donut of TOTAL_VPP_MARGIN by BATTERY_ACTION.
4. "When does the VPP earn?": heatmap of TOTAL_VPP_MARGIN by hour of day (from HOUR)
   and PRICE_ZONE.
5. "Grid import vs export by hour of day": line chart, two series, from telemetry by
   hour of day (from TS).
6. "Net producer vs net consumer clusters": bar of TOTAL_GRID_EXPORT minus
   TOTAL_GRID_IMPORT by CLUSTER_NAME (positive = net exporter).
```

### P3 — Commercial Pulse tiles

```text
On the "Commercial Pulse" tab, use only the semantic view
EPOWER_DEMO.EPOWER_GOLD.ENERGY_SALES_SEMANTIC_VIEW. Add:
1. Scorecards: Total revenue, Total contracts, Average contract value.
2. "Monthly revenue trend": line of TOTAL_REVENUE by month of CONTRACT_DATE.
3. "Revenue by product category": bar of TOTAL_REVENUE by CATEGORY_NAME.
4. "Revenue by region": bar of TOTAL_REVENUE by REGION_NAME.
5. "Top 10 sales reps": table with REP_NAME, TOTAL_REVENUE, TOTAL_CONTRACTS.
```

### P4 — Filters

```text
Add dashboard filters:
- A date range filter (default last 90 days) applied to HOUR/TS on the VPP tab
  and CONTRACT_DATE on the Commercial tab.
- A cascading filter "Location": Region -> Cluster for the VPP tab
  (REGION -> CLUSTER_NAME).
- A Customer type multi-select filter applied to both tabs (CUSTOMER_TYPE).
```

### P5 — Chart actions (the interactive part)

```text
Add chart actions:
- VPP tab: clicking a cluster in "Margin by cluster" filters all other VPP tiles to
  that cluster.
- VPP tab: clicking a slice in "Margin by battery action" highlights that action in
  the other tiles that have BATTERY_ACTION (highlight, not filter).
- Commercial tab: clicking a region in "Revenue by region" filters the trend, the
  category chart and the reps table.
- Commercial tab: clicking a category in "Revenue by product category" highlights it.
- Commercial tab: clicking a month in "Monthly revenue trend" zooms the trend into
  that selection (self-filter).
```

> If CoCo reports it can't wire an action, the tile is likely querying a different source. Ask: *"Rewrite that tile to query the same view as the other tiles on this tab."*

### P6 — Live iteration (use during the demo)

```text
Make the monthly revenue trend weekly.
Add a reference line at the average to the margin-by-cluster chart.
Add a "Battery SOC by hour of day" line chart to the VPP tab.
```

---

## Demo Script (~5 min)

| Step | Do | Say |
|---|---|---|
| 1 | Paste **P1–P2** live (or open the prebuilt dashboard) | "No dashboard builder, no SQL. I describe what the ops team needs; CoCo builds it on our governed semantic view." |
| 2 | Point at the heatmap | "The VPP earns in the HIGH price zone from 16:00 to 19:00 — the evening peak. That's arbitrage, visible at a glance." |
| 3 | Point at the grid line chart | "Midday the fleet soaks up cheap solar-hour power, then exports into the evening peak." |
| 4 | **Click** *Muenchen Metro* in Margin by cluster | "Every tile now answers: how is Munich doing? One click, live queries." |
| 5 | **Click** DISCHARGE in the donut | "Highlight, not filter — discharge earns the margin, charging costs. Instant, no re-query." |
| 6 | Switch to Commercial Pulse, **click** South | "Filters persist across tabs. South leads in Solar & Storage — matching its VPP export profile." |
| 7 | Paste a **P6** prompt | "Business asks for weekly? Ten seconds." |
| 8 | Publish, open in **CoWork**, ask on the cluster tile | *"Why is Berlin Metro a net importer while Freiburg exports?"* |
| 9 | Governance | "Viewers see only what their role allows — the dashboard runs with their privileges." |

### Expected Insights (validated against the data)

| Tile | What you'll see |
|---|---|
| Margin by battery action | DISCHARGE carries the margin; CHARGE is negative (cost of buying cheap power) |
| Heatmap | Highest margin: HIGH zone, 16:00–19:00 (peak ~17:00) |
| Grid by hour | Import peaks ~11:00–12:00, export peaks ~17:00–18:00 |
| Net producer clusters | Muenchen Metro, Freiburg/Oberrhein, Stuttgart Metro, Bayern Sued export; Berlin Metro, Rhein-Ruhr, Hamburg Metro import |
| Revenue by category | Heat Pumps and Solar & Storage dominate; South leads Solar & Storage |

> Avoid SOC-by-cluster as a story tile — average SOC is ~51% in every cluster, so the comparison is flat.

---

## Publish and Share

1. In the Workspace, create the dashboard artifact from the `.dash` file.
2. Share with role `EPOWER_ROLE` (or a demo viewer role).
3. Later edits to the `.dash` file can be republished to the same artifact.

---

## Known Limitations (Preview)

- No geospatial map charts — the cluster map stays in [Module 2 (VPP Monitor)](../02-vpp-monitor/README-module2.md).
- Chart actions are CoCo-only (not in the tile editor) and require a shared source per linked tile set.
- Drill-down is in early development; this module uses filter and highlight actions.
- Dashboards run with the viewer's primary role only.

## Cleanup

Delete the dashboard artifact and the `.dash` file in the Workspace. No database objects are created by this module.
