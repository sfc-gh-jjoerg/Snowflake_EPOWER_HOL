# Module 5 — EPOWER VPP Monitor (Snowflake App)

A dark-mode Virtual Power Plant performance dashboard deployed as a **Snowflake App** — a Next.js web application running inside Snowflake's container infrastructure. No Docker knowledge, no infrastructure provisioning, no credential management required.

## What This Module Demonstrates

| Capability | Description |
|------------|-------------|
| **Snowflake App Runtime** | Build and deploy containerized web apps with a single CLI command |
| **Server-side data access** | API routes query Snowflake directly using injected session tokens |
| **Dark-mode dashboard** | Modern React UI with Tailwind CSS and Recharts |
| **Parameterized views** | Pre-aggregated SQL views that keep query latency low |
| **Zero-credential deployment** | No database passwords in code — SPCS handles auth |

## Features

The dashboard provides three integrated views of VPP fleet performance:

| Section | Metrics |
|---------|---------|
| **KPI Cards** | Active devices, battery SOC %, solar yield (kW), day-ahead price (EUR/MWh), customer margin, EPOWER margin |
| **Time-Series Chart** | Dual-axis: battery SOC + solar yield vs. day-ahead electricity price (daily aggregation, 60-day window) |
| **Battery Actions** | Stacked bar: CHARGE / DISCHARGE / SELF_CONSUME / MAX_CHARGE distribution over time |
| **Revenue Breakdown** | Customer margin vs. EPOWER margin by region |

**Filters**: Region (North/South/East/West), Customer Type (Privatkunde/Kleingewerbe/Gewerbekunde), Date Range.

---

## Prerequisites

Before deploying this module, ensure the following are in place:

1. **Module 1 completed** — Run `01-agentic-ai-foundation/epower_hol_main.ipynb` first. This creates the base tables:
   - `EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY`
   - `EPOWER_DEMO.EPOWER_GOLD.MART_DAY_AHEAD_PRICES`
   - `EPOWER_DEMO.EPOWER_GOLD.MART_VPP_PRICE_OPTIMIZATION`
   - `EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_DIM`

2. **Paid Snowflake account** — App Runtime is not available on trial accounts.

3. **Snowflake CLI 3.19+** — The [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli) (`snow`) is a command-line tool for managing Snowflake resources, including app deployment. Version 3.19+ is required for `snow app` commands — older versions will fail silently or produce confusing errors.

   The easiest way to get started is to install **Cortex Code**, which bundles the Snowflake CLI and handles connection setup for you:
   - [Cortex Code Desktop](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop) — VS Code-based IDE with built-in Snowflake integration
   - [Cortex Code CLI](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli) — terminal-based agent with Snowflake CLI included

   If you prefer to install the Snowflake CLI standalone:
   ```bash
   # macOS (Homebrew)
   brew install snowflake-cli

   # pip
   pip install snowflake-cli
   ```

   **Check your version:**
   ```bash
   snow --version    # must show 3.19.0 or higher
   ```

   **Upgrade:**
   ```bash
   brew upgrade snowflake-cli    # Homebrew
   pip install --upgrade snowflake-cli    # pip
   ```

   > **Tip:** If `snow --version` shows an older version despite upgrading, you may have multiple installations. Run `which snow` to confirm which binary is being used.

4. **Snowflake connection configured** — The Snowflake CLI needs a configured connection to your account. If you're using Cortex Code, this is handled during setup. If you installed the CLI standalone, run `snow connection add` to create a connection, or refer to the [CLI connection docs](https://docs.snowflake.com/en/developer-guide/snowflake-cli/connecting/configure-cli).

5. **ACCOUNTADMIN access** — Needed once for initial account setup (Step 1).

> **Important:** Unlike Modules 1-4 (which deploy via SQL in Snowsight notebooks/worksheets), Module 5 requires the **Snowflake CLI on your local machine**. App Runtime apps involve a build step (compiling TypeScript, bundling CSS, packaging Node.js) that cannot be expressed as SQL — the CLI orchestrates the upload-build-deploy pipeline. There is currently no "deploy from Snowsight" option for App Runtime apps.

### What You'll Learn

By completing this module, you'll gain hands-on experience with:

- **Snowflake App Runtime** — deploying a full-stack web app with a single `snow app deploy` command, no Dockerfile needed
- **SPCS Authentication** — zero-credential data access via OAuth session tokens and Snowflake SSO for end users
- **Next.js on Snowflake** — server-side API routes querying Snowflake directly, combined with a React + Recharts + Tailwind CSS frontend

---

## How Snowflake App Runtime Works

This section explains the platform your app runs on — read this to understand what happens when you deploy.

### What Is Snowflake App Runtime?

Snowflake App Runtime (Public Preview) lets you deploy **web applications** (Next.js / Node.js) directly onto Snowflake's container infrastructure. Your app runs as a managed container service inside Snowflake's security perimeter, with direct access to your data — no API layers, no data egress, no credential management.

**This is NOT the same as Snowflake Native Apps.** The two serve different purposes:

| | Native App Framework | Snowflake App Runtime |
|---|---|---|
| **Purpose** | Package and distribute apps to other Snowflake accounts via Marketplace | Host web apps on your own Snowflake infrastructure |
| **Technology** | SQL setup scripts + optional Streamlit UI | Next.js / Node.js containers |
| **Distribution** | Cross-account via listings | Within your account (shareable with roles) |
| **Object type** | APPLICATION PACKAGE + APPLICATION | APPLICATION SERVICE |
| **Use case** | Data products for consumers | Internal dashboards, tools, custom UIs |

Snowflake App Runtime is the right choice when you need a **custom web application** with full control over the UI (React components, charts, multi-page layouts) that queries Snowflake data directly.

**Reference:** [Snowflake App Runtime overview](https://docs.snowflake.com/en/developer-guide/snowflake-app-runtime/about-snowflake-app-runtime)

### The Problem App Runtime Solves

Traditionally, deploying a web application to Snowpark Container Services (SPCS) requires:
1. Writing a Dockerfile
2. Building a Docker image (for linux/amd64 — not your Mac's ARM chip)
3. Pushing the image to Snowflake's private registry
4. Writing a container service specification YAML
5. Running `CREATE SERVICE` with endpoint bindings and compute pool references
6. Managing DNS and HTTPS certificates
7. Handling credential rotation and OAuth token lifecycle

**Snowflake App Runtime eliminates all of this.** You write your application code (Next.js), and a single command — `snow app deploy` — handles everything else.

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
- `app.yml` — app metadata (title, description, icon)
- `snowflake.yml` — deployment target (generated by `snow app setup`)
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

These are independent — you deploy once with your deploy role, then grant access to as many other roles as needed.

**Grant another role access to the app:**

```sql
GRANT USAGE ON DATABASE SNOWFLAKE_APPS TO ROLE analyst_role;
GRANT USAGE ON SCHEMA SNOWFLAKE_APPS.PUBLIC TO ROLE analyst_role;
GRANT USAGE ON APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR TO ROLE analyst_role;
```

**Additional privileges (optional):**

| Privilege | Effect |
|-----------|--------|
| `USAGE` | Open and use the app |
| `OPERATE` | Suspend, resume, and upgrade the app |
| `MONITOR` | View runtime status and container logs |

> **Note:** Users granted `USAGE` on the app still need appropriate privileges on the underlying tables/views (`EPOWER_DEMO.EPOWER_GOLD.*`) for the dashboard to display data. If a user's role lacks `SELECT` on those views, the app loads but shows empty charts.

### SPCS Concepts (Reference)

| Concept | Description |
|---------|-------------|
| **Compute Pool** | A set of managed VMs that run containers. App Runtime uses shared managed pools — you don't configure them. |
| **Application Service** | Your running container with an HTTPS endpoint. Created by `snow app deploy`. |
| **Artifact Repository** | A private registry inside Snowflake that stores your built images. |
| **Session Token** | A file (`/snowflake/session/token`) injected into every container, providing OAuth credentials scoped to the logged-in user. |

### App Runtime vs. Traditional SPCS

| Aspect | Traditional SPCS | Snowflake App Runtime |
|--------|-----------------|----------------------|
| Dockerfile | Write manually | Generated from package.json |
| Docker build | Local (requires amd64) | Remote (on managed compute pool) |
| Image push | Manual `docker push` to registry | Automatic |
| Service spec | Write YAML, `CREATE SERVICE` | Automatic from snowflake.yml |
| Endpoint DNS | Manual configuration | Automatic HTTPS URL |
| TLS certificates | Managed by Snowflake | Same |
| Code updates | Rebuild, push, `ALTER SERVICE` | `snow app deploy` |
| Logs | `CALL SYSTEM$GET_SERVICE_LOGS(...)` | `snow app events` |
| Teardown | `DROP SERVICE`, cleanup manually | `snow app teardown` |

**The App Runtime reduces a ~20-step deployment process to 3 steps: setup, deploy, open.**

---

## Setup

Follow these steps in order. Steps 1-3 are one-time setup; steps 4-7 are the deploy workflow.

### Step 1: One-time Account Setup (ACCOUNTADMIN)

Snowflake App Runtime needs to know **where to deploy apps** on your account. This is configured via a one-time **App Development Setup** in Snowsight, which sets account-level defaults (destination database, schema, warehouse) and grants deploy permissions to selected roles.

**Why this is needed:** Without this setup, `snow app deploy` falls back to deploying into your personal database (`USER$<username>`). While you can build and test there, apps in personal databases cannot be shared with other roles, and certain operations may fail with confusing errors. The setup ensures a clean, shared destination.

**What "Quick start" creates:**
- `SNOWFLAKE_APPS` database — shared location for all deployed apps on the account
- `SNOWFLAKE_APPS_QUERY_WH` warehouse — used by apps for SQL queries at runtime
- Account-level parameters so `snow app setup` and `snow app deploy` resolve these automatically

> You can also choose "Custom" during setup to point apps at an existing database (e.g., `EPOWER_DEMO`). The `SNOWFLAKE_APPS` name is just the default — it's not a fixed system requirement.

**Steps:**

1. In Snowsight, switch to the **ACCOUNTADMIN** role (top-left role selector)
2. Go to **Settings** (bottom-left) → **Account** → **Apps**
3. Click **Begin Setup**
4. Under "What roles will be making apps?" — select the role your Snowflake CLI connection uses (e.g., `SYSADMIN`). This becomes the **deploy role** — only this role can push code via `snow app deploy`.
5. Under "Resources" — pick **Quick start** (or "Custom" to use an existing database)
6. Click **Execute Setup**

> The deploy role chosen in step 4 is also the role you'll use in Step 2 below for the additional grants. The app's *runtime* queries execute as the logged-in user's role (e.g., `EPOWER_ROLE`), so data access is governed by existing RBAC.

**Reference:** [Account administrator setup for Snowflake App Runtime](https://docs.snowflake.com/en/developer-guide/snowflake-app-runtime/account-admin-setup)

### Step 2: Additional Grants (ACCOUNTADMIN)

Run these in Snowsight as `ACCOUNTADMIN`. Replace `SYSADMIN` with the deploy role you selected in the wizard (Step 1, item 4) if different:

```sql
USE ROLE ACCOUNTADMIN;

-- Allow the deploying role to use the compute pool
GRANT USAGE ON COMPUTE POOL SYSTEM_COMPUTE_POOL_CPU TO ROLE SYSADMIN;

-- Allow the service to expose an HTTPS endpoint
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE SYSADMIN;
```

> These grants only need to be run once per account.

### Step 3: Create Backend Views

The app queries pre-aggregated views that join the VPP data. Open `sql/create_views.sql` in a **Snowsight worksheet** and run all statements.

> The script contains `USE ROLE` and `USE WAREHOUSE` statements which are not permitted via `snow sql`. Running in Snowsight ensures the correct role and context are applied.

This creates three views in `EPOWER_DEMO.EPOWER_GOLD`:
- `V_VPP_MONITOR_TIMESERIES` — hourly capacity + day-ahead prices
- `V_VPP_MONITOR_ACTIONS` — battery action distribution with margins
- `V_VPP_MONITOR_KPI` — summary KPIs by day/region/customer type

### Step 4: Initialize the App

> **Important:** The Snowflake CLI connection you use must be configured with the **deploy role** you selected in Step 1 (e.g., `SYSADMIN`). Check your active connection with `snow connection status` — the `role` field must match. If it doesn't, update your connection (`snow connection set -n <connection> --role SYSADMIN`) or switch connections before proceeding.

```bash
cd 05-vpp-monitor
snow app setup --app-name="EPOWER_VPP_MONITOR"
```

This generates `snowflake.yml` with the deployment configuration resolved from your account's App Development defaults.

### Step 5: Deploy to Snowflake

```bash
snow app deploy
```

First deploy takes 3-5 minutes (uploads code, builds remotely, creates service, provisions endpoint). Subsequent deploys are faster (~2 min) due to layer caching.

### Step 6: Open the App

```bash
snow app open
```

This opens the live HTTPS URL in your browser. You'll authenticate via Snowflake SSO, then see the VPP Monitor dashboard.

---

## Maintaining the App

### Update code and redeploy

```bash
# Edit source files, then:
snow app deploy
```

The runtime detects changes, rebuilds the image, and rolls out a new version (zero-downtime upgrade).

### View logs

```bash
snow app events --last 200
```

Shows container stdout/stderr — useful for debugging API route errors or connection issues.

### Check status

```bash
snow app open --print-only   # Print URL without opening browser
```

### Suspend and resume (cost control)

The app runs on a **Snowflake-managed shared compute pool**. While running, it consumes approximately **0.02-0.03 credits/hour** (~0.5-0.7 credits/day, or roughly $1-2/day depending on your contract).

To stop costs without destroying the app:

```sql
ALTER APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR SUSPEND;
```

To resume:

```sql
ALTER APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR RESUME;
```

Or simply open the app URL — since `auto_resume` is enabled, accessing the endpoint automatically resumes the service. Cold-start takes ~30-60 seconds.

| State | Credits/hour | What happens |
|-------|-------------|--------------|
| Running | ~0.03 | Container active, serving requests |
| Suspended | 0 | Container stopped, no billing, URL shows "service unavailable" |
| Auto-resuming | ~0.03 | Triggered by URL access, ~30-60s startup |

### Teardown

```bash
snow app teardown
```

This drops the SPCS service and associated resources. Does **not** drop the SQL views or base tables.

### Full cleanup

To remove everything created by Module 5 (or run `sql/cleanup.sql`):

```sql
USE ROLE SYSADMIN;
DROP APPLICATION SERVICE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR;
DROP ARTIFACT REPOSITORY IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_REPO;
DROP STAGE IF EXISTS SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR_CODE;

DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_ACTIONS;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_KPI;
```

> Module 5 cleanup is also included in the main `01-agentic-ai-foundation/epower_cleanup.sql` script.

---

## Local Development (Optional)

For iterating on the UI without deploying each change, you can run the app locally. This requires Snowflake credentials as environment variables since there is no SPCS session token on your machine:

```bash
cd 05-vpp-monitor

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

## Architecture

```
Browser (Dark Mode Dashboard)
       |
       |  fetch /api/kpis, /api/timeseries, /api/actions
       v
+------------------------------------------------------------------+
|  Next.js App (SPCS Container)                                    |
|  +-- src/app/page.tsx            <- React dashboard (client-side)|
|  +-- src/app/api/kpis/route.ts   <- Server-side, queries SF      |
|  +-- src/app/api/timeseries/     <- Server-side, queries SF      |
|  +-- src/app/api/actions/        <- Server-side, queries SF      |
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
|                                                                  |
|  Base tables:                                                    |
|  +-- MART_VPP_CAPACITY_HOURLY   (5,760 rows)                    |
|  +-- MART_DAY_AHEAD_PRICES      (5,760 rows)                    |
|  +-- MART_VPP_PRICE_OPTIMIZATION (23M rows, pre-aggregated)     |
+------------------------------------------------------------------+
```

---

## File Structure

```
05-vpp-monitor/
+-- app.yml                       # App metadata (title, description, icon)
+-- snowflake.yml                 # SPCS deployment configuration (generated)
+-- package.json                  # Node.js dependencies
+-- next.config.js                # Next.js config (standalone output)
+-- tailwind.config.js            # Dark-mode theme with energy palette
+-- tsconfig.json                 # TypeScript configuration
+-- postcss.config.js             # PostCSS for Tailwind
+-- sql/
|   +-- create_views.sql          # Backend views DDL (run before deploying)
|   +-- cleanup.sql               # Module 5 cleanup script
+-- src/
|   +-- app/
|   |   +-- layout.tsx            # Root layout (dark HTML class)
|   |   +-- page.tsx              # Main dashboard page
|   |   +-- globals.css           # Tailwind imports + custom utilities
|   |   +-- api/
|   |       +-- kpis/route.ts     # KPI summary endpoint
|   |       +-- timeseries/route.ts # Time-series endpoint
|   |       +-- actions/route.ts  # Battery actions + margins endpoint
|   +-- components/
|   |   +-- FilterBar.tsx         # Region, type, date range filters
|   |   +-- KpiCard.tsx           # Metric card with colored accent
|   |   +-- PriceCapacityChart.tsx # Dual-axis line/area chart
|   |   +-- BatteryActionsChart.tsx # Stacked bar chart
|   |   +-- RevenueChart.tsx      # Margin comparison bar chart
|   +-- lib/
|       +-- snowflake.ts          # Snowflake SDK connection helper
+-- public/
|   +-- icon.svg                  # App icon
+-- README-module5.md             # This file
```

---

## Tech Stack

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
cd 05-vpp-monitor
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
- [ ] Cortex Code Desktop ist geöffnet mit dem `05-vpp-monitor`-Verzeichnis
- [ ] Snowflake CLI Verbindung ist aktiv (`snow connection status`)
- [ ] Terminal ist im richtigen Verzeichnis (`cd 05-vpp-monitor`)
