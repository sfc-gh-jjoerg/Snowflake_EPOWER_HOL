# Module 5: EPOWER VPP Assistant — Agent REST API Demo

A focused Streamlit app demonstrating how to embed the **Cortex Agent REST API** in a web application. The app connects to the VPP Operations Agent and renders streaming responses with tables and charts.

## What This Demonstrates

| Capability | Implementation |
|------------|---------------|
| **Agent REST API** | `POST /api/v2/databases/.../agents/{name}:run` with OAuth bearer auth |
| **Thread management** | Stateful conversations via `/api/v2/cortex/threads` |
| **Streaming SSE** | Real-time token-by-token response rendering |
| **Rich responses** | Tables (DataFrames) and Vega-Lite charts from agent output |
| **Container auth** | Session token from `/snowflake/session/token` — no API keys needed |

## Agent: EPOWER_OPS_AGENT

The app connects to the Operations Agent which has 4 tools:

| Tool | Description |
|------|-------------|
| `vpp_analyst` | VPP fleet telemetry, battery dispatch actions, price zones, arbitrage margins |
| `market_prices_analyst` | Day-ahead electricity prices (EPEX DE-LU) |
| `energy_docs_search` | Energy policies, regulations, subsidies |
| `data_to_chart` | Automatic chart generation |

## Prerequisites

Run the `01-agentic-ai-foundation/epower_hol_main.ipynb` notebook first. The app depends on:
- `EPOWER_DEMO.EPOWER_GOLD.EPOWER_OPS_AGENT`
- `EPOWER_DEMO.EPOWER_GOLD.EPULSE_VPP_SEMANTIC_VIEW`
- `EPOWER_DEMO.EPOWER_GOLD.MARKET_PRICES_SEMANTIC_VIEW`

## Setup (Snowsight Workspace)

1. Open your workspace in Snowsight
2. Click **+ Add new** > **Streamlit app**
3. Select **Run on container** in the dialog
4. Set **Compute pool**: `SYSTEM_COMPUTE_POOL_CPU`
5. Set **Query warehouse**: `EPOWER_COMPUTE`
6. Replace the generated starter files with the contents of this folder:
   - `streamlit_app.py` — main application code
   - `.streamlit/config.toml` — theme configuration
   - `snowflake.yml` — deployment settings
7. **Delete** the auto-generated `pyproject.toml` (not needed)
8. Click **Run**

The first start takes 1-2 minutes while the container initializes.

## Architecture

```
Browser --> Streamlit Container (SPCS)
                |
                +-- REST API (SSE) --> Cortex Agent (EPOWER_OPS_AGENT)
                                           |
                                           +-- vpp_analyst --> EPULSE_VPP_SEMANTIC_VIEW
                                           +-- market_prices_analyst --> MARKET_PRICES_SEMANTIC_VIEW
                                           +-- energy_docs_search --> SEARCH_ENERGY_DOCS
                                           +-- data_to_chart
```

Authentication: The container reads its OAuth session token from `/snowflake/session/token` and passes it as a Bearer token in the `Authorization` header. No API keys or credentials are managed by the app.

## File Structure

```
05-agent-rest-app/
+-- streamlit_app.py          # Agent REST API chat app (~200 lines)
+-- snowflake.yml             # Container runtime deployment config
+-- .streamlit/
|   +-- config.toml           # Theme (EPOWER blue branding)
+-- README-module5.md         # This file
```

## Cleanup

To remove the Streamlit app:

```sql
USE ROLE EPOWER_ROLE;
DROP STREAMLIT IF EXISTS EPOWER_DEMO.EPOWER_GOLD.EPOWER_ASSISTANT;
```

No other objects are created by Module 5. The full cleanup script (`01-agentic-ai-foundation/epower_cleanup.sql`) handles this automatically.

## Suggested Demo Questions

| Question | What it shows |
|----------|--------------|
| "What was the total VPP margin last week?" | Financial metrics from enriched semantic view |
| "Show battery dispatch actions by price zone" | Categorical breakdown with chart |
| "Which clusters export the most during high prices?" | Cluster-level analysis |
| "What are the current day-ahead electricity prices?" | Market data tool selection |

Toggle **Show REST Payloads** in the sidebar to see the raw API request/response JSON for each interaction.
