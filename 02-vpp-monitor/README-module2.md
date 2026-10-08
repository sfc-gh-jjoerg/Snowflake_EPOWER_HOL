# Module 2 — EPOWER VPP Monitor (Snowflake App)

A dark-mode Virtual Power Plant performance dashboard deployed as a **Snowflake App** — a Next.js web application running inside Snowflake's container infrastructure. No Docker knowledge, no infrastructure provisioning, no credential management required.

## What This Module Demonstrates

| Capability | Description |
|------------|-------------|
| **Snowflake App Runtime** | Build and deploy containerized web apps with a single CLI command |
| **Server-side data access** | API routes query Snowflake directly using injected session tokens |
| **Dark-mode dashboard** | Modern React UI with Tailwind CSS and Recharts |
| **Parameterized views** | Pre-aggregated SQL views that keep query latency low |
| **Zero-credential deployment** | No database passwords in code — SPCS handles auth |

By completing this module, you'll gain hands-on experience with:

- **Snowflake App Runtime** — deploying a full-stack web app with a single `snow app deploy` command, no Dockerfile needed
- **SPCS Authentication** — zero-credential data access via OAuth session tokens and Snowflake SSO for end users
- **Next.js on Snowflake** — server-side API routes querying Snowflake directly, combined with a React + Recharts + Tailwind CSS frontend

## Features

The dashboard provides five integrated views of VPP fleet performance:

| Section | Metrics |
|---------|---------|
| **KPI Cards** | Active devices, battery SOC %, solar yield (kW), day-ahead price (EUR/MWh), customer margin, EPOWER margin |
| **Time-Series Chart** | Dual-axis: battery SOC + solar yield vs. day-ahead electricity price (daily aggregation, 60-day window) |
| **Battery Actions** | Stacked bar: CHARGE / DISCHARGE / SELF_CONSUME / MAX_CHARGE distribution over time |
| **Revenue Breakdown** | Customer margin vs. EPOWER margin by region |
| **Regional Comparison** | Horizontal bar chart comparing net energy flow across 14 German VPP clusters (green=exporting, red=importing), with a time slider for day/hour selection |

**Filters**: Region (North/South/East/West), Customer Type (Privatkunde/Kleingewerbe/Gewerbekunde), Date Range.

---

## Architecture

```
Browser (Dark Mode Dashboard)
       |
       |  fetch /api/kpis, /api/timeseries, /api/actions, /api/map, /api/map-range
       v
+------------------------------------------------------------------+
|  Next.js App (SPCS Container)                                    |
|  +-- src/app/page.tsx            <- React dashboard (client-side)|
|  +-- src/app/api/kpis/route.ts   <- Server-side, queries SF      |
|  +-- src/app/api/timeseries/     <- Server-side, queries SF      |
|  +-- src/app/api/actions/        <- Server-side, queries SF      |
|  +-- src/app/api/map/            <- Cluster regional data        |
|  +-- src/app/api/map-range/      <- Date/hour bounds for slider  |
|                                                                  |
|  Authentication: /snowflake/session/token (OAuth)                |
+------------------------------------------------------------------+
       |
       |  Snowflake SDK (snowflake-sdk)
       v
+------------------------------------------------------------------+
|  EPOWER_DEMO.EPOWER_GOLD                                         |
|  +-- V_VPP_MONITOR_TIMESERIES   (capacity + prices, hourly)     |
|  +-- V_VPP_MONITOR_ACTIONS      (battery actions, aggregated)   |
|  +-- V_VPP_MONITOR_KPI          (summary metrics)               |
|  +-- V_VPP_MONITOR_MAP          (hourly cluster aggregation)    |
|                                                                  |
|  Base tables:                                                    |
|  +-- MART_VPP_CAPACITY_HOURLY   (5,760 rows)                    |
|  +-- MART_DAY_AHEAD_PRICES      (5,760 rows)                    |
|  +-- MART_VPP_PRICE_OPTIMIZATION (23M rows, pre-aggregated)     |
|  +-- CITY_CLUSTER_MAP            (dbt seed — city-to-cluster)   |
+------------------------------------------------------------------+
```

### File Structure

```
02-vpp-monitor/
+-- app.yml                       # App manifest v2 (deployment config + metadata)
+-- package.json                  # Node.js dependencies
+-- next.config.js                # Next.js config (standalone output)
+-- tailwind.config.js            # Dark-mode theme with energy palette
+-- tsconfig.json                 # TypeScript configuration
+-- postcss.config.js             # PostCSS for Tailwind
+-- sql/
|   +-- cleanup.sql               # Module 2 cleanup script
+-- src/
|   +-- app/
|   |   +-- layout.tsx            # Root layout (dark HTML class)
|   |   +-- page.tsx              # Main dashboard page
|   |   +-- globals.css           # Tailwind imports + custom utilities
|   |   +-- api/
|   |       +-- kpis/route.ts     # KPI summary endpoint
|   |       +-- timeseries/route.ts # Time-series endpoint
|   |       +-- actions/route.ts  # Battery actions + margins endpoint
|   |       +-- map/route.ts      # Regional cluster data endpoint
|   |       +-- map-range/route.ts # Date/hour range for time slider
|   +-- components/
|   |   +-- FilterBar.tsx         # Region, type, date range filters
|   |   +-- KpiCard.tsx           # Metric card with colored accent
|   |   +-- RegionalChart.tsx     # Horizontal bar chart: net flow by cluster
|   |   +-- PriceCapacityChart.tsx # Dual-axis line/area chart
|   |   +-- BatteryActionsChart.tsx # Stacked bar chart
|   |   +-- RevenueChart.tsx      # Margin comparison bar chart
|   |   +-- TimeSlider.tsx        # Day/hour slider for regional chart
|   +-- lib/
|       +-- snowflake.ts          # Snowflake SDK connection helper
+-- public/
|   +-- icon.svg                  # App icon
+-- README-module2.md             # This file
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | Next.js 14 (App Router) | SSR + API routes in one deployable |
| UI | React 18 + Tailwind CSS | Component-based dark-mode dashboard |
| Charts | Recharts | Lightweight, composable, responsive charts |
| Data | Snowflake SDK (Node.js) | Direct Snowflake queries from API routes |
| Auth | SPCS Session Token (OAuth) | Zero-credential server-side authentication |
| Deploy | Snowflake App Runtime | Single-command container deployment |
| Infra | SPCS Managed Compute Pool | Container execution inside Snowflake |

---

## Prerequisites

Before deploying this module, ensure the following are in place:

1. **Module 1 completed** — Run `01-agentic-ai-foundation/epower_hol_main.ipynb` first. This creates the base tables in `EPOWER_DEMO.EPOWER_GOLD` (`MART_VPP_CAPACITY_HOURLY`, `MART_DAY_AHEAD_PRICES`, `MART_VPP_PRICE_OPTIMIZATION`, `CUSTOMER_DIM`). The dbt pipeline (Module 1, Section 6) also creates the four `V_VPP_MONITOR_*` views and the `CITY_CLUSTER_MAP` seed that the dashboard queries.

2. **Paid Snowflake account** — App Runtime is not available on trial accounts.

3. **Snowflake CLI 3.26+** — Required for the `app.yml` v2 manifest format. Install via [Cortex Code Desktop](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop) (bundles the CLI) or standalone:
   ```bash
   brew install snowflake-cli    # macOS
   pip install snowflake-cli     # pip
   snow --version                # must show 3.26.0 or higher
   ```

4. **Snowflake connection configured** — If using Cortex Code, this is handled during setup. Otherwise run `snow connection add` or see the [CLI connection docs](https://docs.snowflake.com/en/developer-guide/snowflake-cli/connecting/configure-cli).

5. **ACCOUNTADMIN access** — Needed once for initial account setup (Step 1).

> **Note:** Unlike Module 1 (which deploys via SQL in Snowsight), Module 2 requires the **Snowflake CLI on your local machine**. App Runtime apps involve a build step (compiling TypeScript, bundling CSS, packaging Node.js) that cannot be expressed as SQL.

---

## Setup

Follow these steps in order. Steps 1-3 are one-time setup; steps 4-5 are the deploy workflow.

### Step 1: One-time Account Setup (ACCOUNTADMIN)

Snowflake App Runtime needs to know **where to deploy apps** on your account. This is configured via a one-time **App Development Setup** in Snowsight, which sets account-level defaults (destination database, schema, warehouse) and grants deploy permissions to selected roles.

**What "Quick start" creates:**
- `SNOWFLAKE_APPS` database — shared location for all deployed apps on the account
- `SNOWFLAKE_APPS_QUERY_WH` warehouse — used by apps for SQL queries at runtime
- Account-level parameters so `snow app setup` and `snow app deploy` resolve these automatically

**Steps:**

1. In Snowsight, switch to the **ACCOUNTADMIN** role (top-left role selector)
2. Go to **Settings** (bottom-left) → **Account** → **Apps**
3. Click **Begin Setup**
4. Under "What roles will be making apps?" — select the role your Snowflake CLI connection uses (e.g., `SYSADMIN`). This becomes the **deploy role**.
5. Under "Resources" — pick **Quick start** (or "Custom" to use an existing database)
6. Click **Execute Setup**

> The deploy role chosen in step 4 is also the role you'll use in Step 2 below for the additional grants. The app's *runtime* queries execute as the logged-in user's role (e.g., `EPOWER_ROLE`), so data access is governed by existing RBAC.

**Reference:** [Account administrator setup for Snowflake App Runtime](https://docs.snowflake.com/en/developer-guide/snowflake-app-runtime/account-admin-setup)

### Step 2: Additional Grants (ACCOUNTADMIN)

Run these in Snowsight as `ACCOUNTADMIN`. Replace `SYSADMIN` with your deploy role if different:

```sql
USE ROLE ACCOUNTADMIN;

-- Allow the deploying role to use the compute pool
GRANT USAGE ON COMPUTE POOL SYSTEM_COMPUTE_POOL_CPU TO ROLE SYSADMIN;

-- Allow the service to expose an HTTPS endpoint
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE SYSADMIN;
```

> These grants only need to be run once per account.

### Step 3: Create Backend Views

The app queries pre-aggregated views managed by dbt. These are created automatically when running the dbt pipeline in Module 1 (Section 6). The view definitions live in `epower_dbt/models/epulse_vpp/presentation/` and the city-cluster mapping is a dbt seed in `epower_dbt/seeds/city_cluster_map.csv`.

This creates four views in `EPOWER_DEMO.EPOWER_GOLD`:
- `V_VPP_MONITOR_TIMESERIES` — hourly capacity + day-ahead prices
- `V_VPP_MONITOR_ACTIONS` — battery action distribution with margins
- `V_VPP_MONITOR_KPI` — summary KPIs by day/region/customer type
- `V_VPP_MONITOR_MAP` — hourly cluster-level aggregation for the geographic chart

### Step 4: Deploy to Snowflake

> **Important:** Your Snowflake CLI connection must use the **deploy role** from Step 1 (e.g., `SYSADMIN`). Check with `snow connection status` — the `role` field must match.

This project uses the `app.yml` v2 manifest format — no `snowflake.yml` needed.

```bash
snow app deploy
```

First deploy takes 3-5 minutes (uploads code, builds remotely, creates service, provisions endpoint). Subsequent deploys are faster (~2 min) due to layer caching.

### Step 5: Open the App

```bash
snow app open
```

This opens the live HTTPS URL in your browser. You'll authenticate via Snowflake SSO, then see the VPP Monitor dashboard.

---

## Maintaining the App

### Update code and redeploy

```bash
snow app deploy
```

The runtime detects changes, rebuilds the image, and rolls out a new version (zero-downtime upgrade).

### View logs

```bash
snow app events --last 200
```

Shows container stdout/stderr — useful for debugging API route errors or connection issues.

### Suspend and resume (cost control)

The app runs on a **Snowflake-managed shared compute pool**. While running, it consumes approximately **0.02-0.03 credits/hour** (~0.5-0.7 credits/day).

```sql
-- Suspend (stops billing)
ALTER APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR SUSPEND;

-- Resume
ALTER APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR RESUME;
```

Or simply open the app URL — since `auto_resume` is enabled, accessing the endpoint automatically resumes the service. Cold-start takes ~30-60 seconds.

| State | Credits/hour | What happens |
|-------|-------------|--------------|
| Running | ~0.03 | Container active, serving requests |
| Suspended | 0 | Container stopped, no billing |
| Auto-resuming | ~0.03 | Triggered by URL access, ~30-60s startup |

### Teardown

```bash
snow app teardown
```

Drops the SPCS service and associated resources. Does **not** drop the SQL views or base tables.

### Full cleanup

To remove everything created by Module 2:

```sql
USE ROLE SYSADMIN;
DROP APPLICATION SERVICE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR;
DROP ARTIFACT REPOSITORY IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_REPO;
DROP STAGE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_CODE;

DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_ACTIONS;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_KPI;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_MAP;
```

> Module 2 cleanup is also included in the main `01-agentic-ai-foundation/epower_cleanup.sql` script.

---

## Local Development (Optional)

For iterating on the UI without deploying each change, you can run the app locally. This requires Snowflake credentials as environment variables since there is no SPCS session token on your machine:

```bash
cd 02-vpp-monitor

# Set environment variables for local Snowflake access
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-user"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_WAREHOUSE="EPOWER_COMPUTE"

# Install dependencies and start dev server
npm install
npm run dev
```

Open http://localhost:3000. The app detects it's not in SPCS (no `/snowflake/session/token` file) and falls back to password authentication. When satisfied with changes, deploy with `snow app deploy`.

---

## How Snowflake App Runtime Works

This section is a reference for understanding the platform — not required to complete the module.

### What Is Snowflake App Runtime?

Snowflake App Runtime lets you deploy **web applications** (Next.js / Node.js) directly onto Snowflake's container infrastructure. Your app runs as a managed container service inside Snowflake's security perimeter, with direct access to your data — no API layers, no data egress, no credential management.

**This is NOT the same as Snowflake Native Apps:**

| | Native App Framework | Snowflake App Runtime |
|---|---|---|
| **Purpose** | Package and distribute apps to other Snowflake accounts via Marketplace | Host web apps on your own Snowflake infrastructure |
| **Technology** | SQL setup scripts + optional Streamlit UI | Next.js / Node.js containers |
| **Distribution** | Cross-account via listings | Within your account (shareable with roles) |
| **Object type** | APPLICATION PACKAGE + APPLICATION | APPLICATION SERVICE |
| **Use case** | Data products for consumers | Internal dashboards, tools, custom UIs |

**Reference:** [Snowflake App Runtime overview](https://docs.snowflake.com/en/developer-guide/snowflake-app-runtime/about-snowflake-app-runtime)

### What Happens When You Deploy

```
Your Code (Next.js + package.json)
       |
       v
+--------------------------------------------------------------+
|  snow app deploy                                             |
|  +----------+   +--------------+   +---------------------+  |
|  | 1. Upload|-> | 2. Remote    |-> | 3. Create/Update    |  |
|  |    code  |   |    Docker    |   |    SPCS Service     |  |
|  |    to    |   |    build on  |   |    with endpoint    |  |
|  |    stage |   |    compute   |   |    bindings + DNS   |  |
|  |          |   |    pool      |   |                     |  |
|  +----------+   +--------------+   +---------------------+  |
+--------------------------------------------------------------+
       |
       v
Live HTTPS URL -> https://<app>-<account>.snowflakecomputing.app
```

**What you provide:**
- `app.yml` — single manifest with deployment config + app metadata
- Source code (your `src/` directory + `package.json`)

**What the runtime provides automatically:**
- Dockerfile generation from your `package.json`
- Remote Docker build on Snowflake compute (no local Docker needed)
- Image storage in a managed artifact repository
- SPCS service creation with health checks and auto-restart
- HTTPS endpoint with TLS termination and SSO authentication
- OAuth session token injection for zero-credential data access

### How Authentication Works

```
Browser -> HTTPS -> SPCS Service (your Next.js app)
                       |
                       | API route reads /snowflake/session/token
                       v
               Snowflake SDK connects with OAuth token
                       |
                       v
               Executes SQL as the logged-in user's role
```

No passwords, no connection strings, no secrets management. The token is injected into the container by the runtime and refreshed automatically.

### Roles & Access Control

App Runtime separates three concerns:

| Concern | Who controls it | What it governs |
|---------|----------------|-----------------|
| **Deploying** | Deploy role (e.g. `SYSADMIN`) | Who can push code via `snow app deploy` |
| **App access** | Any role granted `USAGE` | Who can open the app URL and interact with it |
| **Data access** | Logged-in user's active role | Which tables/views the app can query at runtime |

**Grant another role access to the app:**

```sql
GRANT USAGE ON DATABASE SNOWFLAKE_APPS TO ROLE analyst_role;
GRANT USAGE ON SCHEMA SNOWFLAKE_APPS.PUBLIC TO ROLE analyst_role;
GRANT USAGE ON APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR TO ROLE analyst_role;
```

> Users granted `USAGE` on the app still need `SELECT` on the underlying views (`EPOWER_DEMO.EPOWER_GOLD.*`) for the dashboard to display data.

### App Runtime vs. Traditional SPCS

| Aspect | Traditional SPCS | Snowflake App Runtime |
|--------|-----------------|----------------------|
| Dockerfile | Write manually | Generated from package.json |
| Docker build | Local (requires amd64) | Remote (on managed compute pool) |
| Image push | Manual `docker push` to registry | Automatic |
| Service spec | Write YAML, `CREATE SERVICE` | Automatic from app.yml |
| Endpoint DNS | Manual configuration | Automatic HTTPS URL |
| TLS certificates | Managed by Snowflake | Same |
| Code updates | Rebuild, push, `ALTER SERVICE` | `snow app deploy` |
| Logs | `CALL SYSTEM$GET_SERVICE_LOGS(...)` | `snow app events` |
| Teardown | `DROP SERVICE`, cleanup manually | `snow app teardown` |

### SPCS Concepts (Reference)

| Concept | Description |
|---------|-------------|
| **Compute Pool** | A set of managed VMs that run containers. App Runtime uses shared managed pools — you don't configure them. |
| **Application Service** | Your running container with an HTTPS endpoint. Created by `snow app deploy`. |
| **Artifact Repository** | A private registry inside Snowflake that stores your built images. |
| **Session Token** | A file (`/snowflake/session/token`) injected into every container, providing OAuth credentials scoped to the logged-in user. |

---

## Building This App with Cortex Code

This entire app was built using [Cortex Code Desktop](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop) — Snowflake's AI-powered IDE. Instead of hand-coding 20+ files, the app was generated from a natural-language prompt and iteratively refined through conversation.

### The Prompt

The starting prompt pointed Cortex Code at the existing data and described the desired outcome. Cortex Code explored the schema, discovered the table structures, and proposed the architecture:

> *I have VPP (Virtual Power Plant) data in `EPOWER_DEMO.EPOWER_GOLD` — the key tables are `MART_VPP_PRICE_OPTIMIZATION` (30M rows, hourly battery actions with import/export/margins per customer and city), `MART_VPP_CAPACITY_HOURLY`, `MART_DAY_AHEAD_PRICES`, `CUSTOMER_DIM`, and `VPP_CLUSTER_DIM`.*
>
> *Build a dark-mode VPP monitoring dashboard as a Snowflake App (Next.js on App Runtime). It should show:*
> 1. *KPI cards for active devices, battery SOC, solar yield, spot price, customer savings, and EPOWER revenue*
> 2. *A time-series chart with battery SOC + solar yield vs. day-ahead price*
> 3. *Battery action distribution (charge/discharge/self-consume) over time*
> 4. *Revenue breakdown by region*
> 5. *A regional comparison showing net energy flow per VPP cluster*
> 6. *Filters for region, customer type, and date range*

### What Cortex Code Did

1. **Schema discovery** — Ran `DESCRIBE TABLE` and `SELECT` queries to understand columns, data types, row counts, and value distributions
2. **View design** — Proposed 4 pre-aggregated SQL views to keep dashboard queries fast, plus a `CITY_CLUSTER_MAP` reference table (now a dbt seed) to join cities to VPP clusters
3. **Architecture** — Chose Next.js App Router with separate API routes per endpoint, Recharts for charts, Tailwind CSS for dark-mode styling, and the Snowflake SDK with SPCS OAuth token auth
4. **Code generation** — Produced the full project: scaffold, connection helper, 5 API routes, 7 React components, dashboard page, and deployment manifest

### What Was Generated

| What | Files |
|------|-------|
| **Project scaffold** | `package.json`, `tsconfig.json`, `next.config.js`, `tailwind.config.js`, `postcss.config.js` |
| **Snowflake connection** | `src/lib/snowflake.ts` — SPCS OAuth + local-dev fallback |
| **API routes** | `src/app/api/kpis/`, `timeseries/`, `actions/`, `map/`, `map-range/` — parameterized SQL with filter support |
| **Dashboard page** | `src/app/page.tsx` — state management, filter wiring, parallel data fetching |
| **7 components** | `FilterBar`, `KpiCard`, `PriceCapacityChart`, `BatteryActionsChart`, `RevenueChart`, `RegionalChart`, `TimeSlider` |
| **Styling** | `globals.css`, `layout.tsx` — dark theme with energy-inspired color palette |
| **Backend views** | Managed by dbt — `epower_dbt/models/epulse_vpp/presentation/` (4 views + city-cluster seed) |
| **Deployment manifest** | `app.yml` — v2 manifest with build/install/run config |

### Iterative Refinements

After the initial generation, follow-up prompts refined the app:

- *"Add a time slider to the regional comparison section so I can scrub through hours of a selected day"*
- *"The KPI cards should show German number formatting and EUR currency"*
- *"Add a map-range API endpoint that returns the min/max date and hour range for the time slider"*

Each refinement was a single prompt — Cortex Code modified the relevant files in place, preserving the existing code.

The entire app — 20+ files, ~1,500 lines of TypeScript/React/SQL — was built through conversation, not manual coding. The developer pointed at the data and described the dashboard. Cortex Code explored the schema, designed the view layer, chose the tech stack, and generated the full project.

---

## Live-Erweiterung mit Cortex Code (Demo-Showcase)

Dieses Szenario zeigt, wie mächtig Cortex Code Desktop ist: Eine produktionsreife App wird live um ein neues Feature erweitert und in unter 3 Minuten deployed.

### Szenario: VPP Preis-Signal hinzufügen

Die bestehende App zeigt historische Daten. Wir erweitern sie um eine **Echtzeit-Preis-Ampel**, die den aktuellen Strompreis anzeigt und farblich signalisiert, ob die Batterien gerade laden oder entladen sollten.

**Ergebnis:**
```
+-----------------------------------------------------------+
|  ⚡ VPP Preis-Signal            Aktuell: 87,40 EUR/MWh    |
|                                                           |
|  🔴 HOCH — Batterien entladen (Erlös-Optimierung aktiv)  |
|                                                           |
|  Ø heute: 62,30 EUR/MWh | Ø 7 Tage: 58,10 EUR/MWh      |
+-----------------------------------------------------------+
```

### Demo-Ablauf

**Schritt 1: App zeigen**

Die deployed App im Browser öffnen und kurz die bestehenden Features zeigen (KPIs, Charts, Filter).

```bash
snow app open
```

**Schritt 2: Feature anfordern (in Cortex Code Desktop)**

Prompt an Cortex Code:

> *„Erweitere die VPP Monitor App um eine Preis-Signal-Komponente. Sie soll:*
> - *Den aktuellen Strompreis aus der letzten verfügbaren Stunde anzeigen*
> - *Farblich signalisieren: grün (<40 EUR/MWh = laden), gelb (40-80 = halten), rot (>80 = entladen)*
> - *Den Tagesdurchschnitt und 7-Tage-Durchschnitt als Kontext anzeigen*
> - *Einen neuen API-Endpoint /api/signal erstellen*
> - *Die Komponente oberhalb der KPI-Cards in page.tsx einbinden"*

**Was Cortex Code erzeugt** (3 Dateien):

1. `src/app/api/signal/route.ts` — API-Endpoint: holt aktuellen Preis + Durchschnitte aus `V_VPP_MONITOR_TIMESERIES`
2. `src/components/PriceSignal.tsx` — React-Komponente: farbige Status-Card mit Ampel-Logik
3. `src/app/page.tsx` — Import + Einbindung der neuen Komponente

**Schritt 3: Deploy**

```bash
cd 02-vpp-monitor
snow app deploy
```

Redeploy dauert ~2 Minuten (Layer-Caching). Während der Build läuft, kann man erklären, was im Hintergrund passiert (Remote Docker Build, SPCS Service Update).

**Schritt 4: Ergebnis zeigen**

Browser refreshen — die Preis-Ampel erscheint oberhalb der KPI-Cards.

### Warum dieses Feature ideal für die Live-Demo ist

| Aspekt | Vorteil |
|--------|---------|
| **Umfang** | 3 Dateien, keine neue Library, kein `npm install` |
| **Visuell** | Sofort sichtbar (große farbige Card), kein Scrollen nötig |
| **Geschäftslogik** | Einfache Schwellwerte — jeder versteht die Ampel-Metapher |
| **Kein Risiko** | Nutzt nur bestehende View (`V_VPP_MONITOR_TIMESERIES`), keine Schema-Änderung |
| **Cortex Code zeigt Stärke** | Generiert TypeScript + React + Tailwind + SQL-Query in einem Schritt |

### Fallback bei Problemen

Falls der Deploy fehlschlägt oder zu lange dauert:
- `snow app events --last 50` zeigt die Build-Logs
- Häufigster Fehler: TypeScript-Kompilierung — Cortex Code kann den Fehler direkt fixen
- Alternative: Feature lokal zeigen mit `npm run dev` (localhost:3000), Deploy später

### Vorbereitungs-Checkliste

- [ ] App ist bereits deployed und läuft (`snow app open` funktioniert)
- [ ] Cortex Code Desktop ist geöffnet mit dem `02-vpp-monitor`-Verzeichnis
- [ ] Snowflake CLI Verbindung ist aktiv (`snow connection status`)
- [ ] Terminal ist im richtigen Verzeichnis (`cd 02-vpp-monitor`)
