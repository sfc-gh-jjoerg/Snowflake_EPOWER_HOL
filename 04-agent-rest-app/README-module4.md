# EPOWER Assistant — Streamlit Workspace App

Interactive dashboard and AI chat interface for the EPOWER Energy Intelligence Demo.
Demonstrates the **Cortex Agent REST API** with streaming responses inside a Streamlit container-runtime app.

## Features

| Tab | Description |
|-----|-------------|
| **Dashboard** | Sales KPIs, monthly revenue trends, product category breakdown, VPP fleet status (solar/battery/grid), and day-ahead electricity prices |
| **Agent Chat** | Natural-language chat with selectable domain-specific agents via streaming SSE. Agent selector switches between Operations, Commercial, People, and the all-in-one agent. Supports text, tables, and chart responses. Optional REST payload viewer |

## Prerequisites

Run the `01-agentic-ai-foundation/epower_hol_main.ipynb` notebook first. This app depends on:

- `EPOWER_DEMO.EPOWER_GOLD.SALES_FACT`
- `EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM` / `PRODUCT_CATEGORY_DIM` / `REGION_DIM`
- `EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY`
- `EPOWER_DEMO.EPOWER_GOLD.MART_DAY_AHEAD_PRICES`
- `EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT` (monolithic, all domains)
- `EPOWER_DEMO.EPOWER_GOLD.EPOWER_OPS_AGENT` (VPP operations & energy market)
- `EPOWER_DEMO.EPOWER_GOLD.EPOWER_COMMERCIAL_AGENT` (sales, billing, service)
- `EPOWER_DEMO.EPOWER_GOLD.EPOWER_PEOPLE_AGENT` (HR & workforce)

## Setup (Snowsight Workspace)

1. Open your workspace in Snowsight
2. Click **+ Add new** → **Streamlit app**
3. Select **Run on container** in the dialog
4. Set **Compute pool**: `SYSTEM_COMPUTE_POOL_CPU`
5. Set **Query warehouse**: `EPOWER_COMPUTE`
6. Replace the generated starter files with the contents of this folder:
   - `streamlit_app.py` — main application code
   - `.streamlit/config.toml` — theme configuration
   - `snowflake.yml` — deployment settings
7. **Delete** the auto-generated `pyproject.toml` (not needed; the container base image includes all required packages)
8. Click **Run**

The first start takes 1-2 minutes while the container initializes.

## Runtime Configuration

| Setting | Value |
|---------|-------|
| Runtime | `SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` |
| Compute pool | `SYSTEM_COMPUTE_POOL_CPU` |
| Query warehouse | `EPOWER_COMPUTE` |
| Python | 3.11 |
| Dependencies | None (base image provides streamlit, requests, pandas, snowflake-snowpark-python) |

## Architecture

```
Browser → Streamlit Container (SPCS)
              │
              ├── SQL queries → EPOWER_COMPUTE warehouse → EPOWER_GOLD tables
              │
              └── REST API (SSE) → Cortex Agent(s) → Semantic Views / Cortex Search
                                     │                  └── EPOWER_COMPUTE warehouse
                                     ├── EPOWER_AGENT (all 12 tools)
                                     ├── EPOWER_OPS_AGENT (VPP + prices + energy docs)
                                     ├── EPOWER_COMMERCIAL_AGENT (sales + billing + service)
                                     └── EPOWER_PEOPLE_AGENT (HR)
```

The app authenticates to the Agent REST API using the container's session token (`/snowflake/session/token`) with OAuth bearer authentication.

## File Structure

```
04-agent-rest-app/
├── streamlit_app.py          # Main app (dashboard + chat)
├── snowflake.yml             # Container runtime deployment config
├── .streamlit/
│   └── config.toml           # Theme (EPOWER blue branding)
└── README-module4.md         # This file
```

## Cleanup

To remove the Streamlit app:

1. In Snowsight, navigate to **Projects » Streamlit**
2. Find `EPOWER_ASSISTANT` and click the **...** menu → **Drop**

Or via SQL:

```sql
USE ROLE EPOWER_ROLE;
DROP STREAMLIT IF EXISTS EPOWER_DEMO.EPOWER_GOLD.EPOWER_ASSISTANT;
```

No other objects are created by Module 4 — the app only reads from existing tables and calls the existing agents. The full cleanup script (`01-agentic-ai-foundation/epower_cleanup.sql`) handles this automatically when dropping the `EPOWER_DEMO` database.

---

## Multi-Agent Architecture

The app includes an **Agent Selector** dropdown in the Chat tab:

| Agent | Focus | Tools |
|-------|-------|-------|
| EPOWER Intelligence | All domains (monolithic) | 12 tools |
| Operations | VPP fleet, energy market, energy policy docs | 4 tools |
| Commercial | Sales, billing, service, product/service docs | 8 tools |
| People | HR workforce analytics | 2 tools |

Switching agents resets the conversation thread. Each agent has specialized instructions and vocabulary tuned to its audience (energy traders vs. sales managers vs. HR partners).

---

## Deploying to Other Users

After testing, click **Deploy** in the workspace toolbar to publish the app as a STREAMLIT object. In the deploy dialog, add roles that should have access (e.g., `EPOWER_ROLE`).
