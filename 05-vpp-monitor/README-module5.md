# Module 5 — EPOWER VPP Monitor (Snowflake App)

Real-time Virtual Power Plant performance dashboard deployed as a **Snowflake App** via Snowpark Container Services (SPCS). Demonstrates how to build, deploy, and maintain a production-grade Next.js web application that runs entirely inside Snowflake's infrastructure.

## What This Module Demonstrates

| Capability | Description |
|------------|-------------|
| **Snowflake App Runtime** | Build and deploy containerized web apps with a single CLI command |
| **Server-side data access** | API routes query Snowflake directly using injected session tokens |
| **Dark-mode dashboard** | Modern React UI with Tailwind CSS and Recharts |
| **Parameterized views** | Pre-aggregated SQL views that keep query latency low |
| **Zero-credential deployment** | No database passwords in code — SPCS handles auth |

---

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

Run `01-agentic-ai-foundation/epower_hol_main.ipynb` first. This module depends on:

- `EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY`
- `EPOWER_DEMO.EPOWER_GOLD.MART_DAY_AHEAD_PRICES`
- `EPOWER_DEMO.EPOWER_GOLD.MART_VPP_PRICE_OPTIMIZATION`
- `EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_DIM`

Additionally, the following views must exist (created by `sql/create_views.sql`):

- `EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES`
- `EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_ACTIONS`
- `EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_KPI`

---

## Required Privileges

### One-time Account Setup (ACCOUNTADMIN)

Snowflake App Runtime requires a one-time **App Development Setup** in Snowsight:

1. Go to **Settings** (bottom-left) → **Account** → **Apps**
2. Click **Begin Setup**
3. Under "What roles will be making apps?" — select the role used by your deploy connection (e.g., `SYSADMIN`)
4. Under "Resources" — pick **Quick start** (creates `SNOWFLAKE_APPS` database + `SNOWFLAKE_APPS_QUERY_WH`)
5. Click **Execute Setup**

> This only grants the selected role the ability to *deploy* apps. The app's runtime queries execute as the logged-in user's role (e.g., `EPOWER_ROLE`), so data access is governed by existing RBAC — not the deploy role.

### Additional grants

Run these as `ACCOUNTADMIN` if not already in place:

```sql
USE ROLE ACCOUNTADMIN;

-- Allow usage of the compute pool that runs the container
GRANT USAGE ON COMPUTE POOL SYSTEM_COMPUTE_POOL_CPU TO ROLE SYSADMIN;

-- Allow the service to bind an HTTPS endpoint (public URL)
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE SYSADMIN;
```

> Replace `SYSADMIN` with your deploying role if different. These grants only need to be run once per account.

---

## Understanding SPCS and Snowflake App Runtime

### What is SPCS?

**Snowpark Container Services (SPCS)** is Snowflake's managed container platform. It allows you to run Docker containers inside Snowflake's security perimeter — on Snowflake-managed compute pools — with direct access to your data, governed by the same roles and privileges as SQL queries.

Key SPCS concepts:

| Concept | Description |
|---------|-------------|
| **Compute Pool** | A set of VM nodes (e.g., `CPU_X64_XS`) that run your containers. Similar to a Kubernetes node pool. |
| **Service** | A running container with an HTTPS endpoint, bound to a compute pool. Your app runs as a service. |
| **Image Repository** | A private Docker registry inside Snowflake (one per schema) that stores your container images. |
| **External Access Integration (EAI)** | A policy that allows containers to make outbound network calls (e.g., to npm registry during build). |
| **Session Token** | A file (`/snowflake/session/token`) injected into every SPCS container, providing OAuth credentials for Snowflake access with the invoking user's role. |

### What Snowflake App Runtime Abstracts Away

Traditionally, deploying to SPCS requires:
1. Writing a Dockerfile
2. Building a Docker image (for linux/amd64)
3. Pushing the image to `<account>.registry.snowflakecomputing.com/<db>/<schema>/<repo>`
4. Writing a service specification YAML
5. Running `CREATE SERVICE` with endpoint bindings and compute pool references
6. Managing DNS and HTTPS certificates

**Snowflake App Runtime eliminates all of this.** You write your Next.js application, and the `snow app deploy` CLI command handles:

```
Your Code (Next.js)
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  snow app deploy                                             │
│  ┌───────────┐  ┌──────────────┐  ┌─────────────────────┐    │
│  │ 1. Upload │→ │ 2. Remote    │→ │ 3. Create/Update    │    │
│  │    code   │  │    Docker    │  │    SPCS Service     │    │
│  │    to     │  │    build on  │  │    with endpoint    │    │
│  │    stage  │  │    compute   │  │    bindings + DNS   │    │
│  │           │  │    pool      │  │                     │    │
│  └───────────┘  └──────────────┘  └─────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
Live HTTPS URL → https://<app>-<account>.snowflakecomputing.app
```

**What you provide:**
- `app.yml` — app metadata (title, description, icon)
- `snowflake.yml` — deployment configuration (which compute pool, which warehouse)
- Source code (your `src/` directory)

**What the runtime provides:**
- Dockerfile generation from your `package.json`
- Multi-stage Docker build (optimized for Next.js standalone output)
- Image push to the account's artifact repository
- Service creation with health checks and auto-restart
- HTTPS endpoint with TLS termination
- Session token injection for Snowflake authentication

### How Authentication Works

```
Browser → HTTPS → SPCS Service (your Next.js app)
                       │
                       │ API route reads /snowflake/session/token
                       │
                       ▼
               Snowflake SDK connects with OAuth token
                       │
                       ▼
               Executes SQL as the invoking user's role
```

No passwords, no connection strings, no secrets management. The token is refreshed automatically by the runtime.

---

## Setup

### 1. Create the backend views

```sql
-- Run in Snowsight or via SnowSQL:
-- (see sql/create_views.sql for the full script)

USE ROLE EPOWER_ROLE;
USE WAREHOUSE EPOWER_COMPUTE;
USE SCHEMA EPOWER_DEMO.EPOWER_GOLD;

-- Creates: V_VPP_MONITOR_TIMESERIES, V_VPP_MONITOR_ACTIONS, V_VPP_MONITOR_KPI
```

### 2. Initialize the app

```bash
cd 05-vpp-monitor

# Configure deployment (creates/updates snowflake.yml)
snow app setup --app-name="EPOWER_VPP_MONITOR"

# Install dependencies (for local dev only)
npm install
```

### 3. Deploy to Snowflake

```bash
snow app deploy
```

This takes 2-5 minutes on first deploy (builds the container image remotely). Subsequent deploys are faster due to layer caching.

### 4. Open the app

```bash
snow app open
```

Or find the URL in the deploy output.

---

## Local Development

For local development without SPCS:

```bash
# Set environment variables
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-user"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_WAREHOUSE="EPOWER_COMPUTE"

# Install and run
npm install
npm run dev
```

Open http://localhost:3000. The app detects it's not in SPCS (no `/snowflake/session/token` file) and falls back to password authentication.

---

## Architecture

```
Browser (Dark Mode Dashboard)
       │
       │  fetch /api/kpis, /api/timeseries, /api/actions
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Next.js App (SPCS Container)                                    │
│  ├── src/app/page.tsx            ← React dashboard (client-side) │
│  ├── src/app/api/kpis/route.ts   ← Server-side, queries Snowflake│
│  ├── src/app/api/timeseries/     ← Server-side, queries Snowflake│
│  └── src/app/api/actions/        ← Server-side, queries Snowflake│
│                                                                  │
│  Authentication: /snowflake/session/token (OAuth)                │
└──────────────────────────────────────────────────────────────────┘
       │
       │  Snowflake SDK (snowflake-sdk)
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  EPOWER_DEMO.EPOWER_GOLD                                         │
│  ├── V_VPP_MONITOR_TIMESERIES   (capacity + prices, hourly)     │
│  ├── V_VPP_MONITOR_ACTIONS      (battery actions, aggregated)   │
│  └── V_VPP_MONITOR_KPI          (summary metrics)               │
│                                                                  │
│  Base tables:                                                    │
│  ├── MART_VPP_CAPACITY_HOURLY   (5,760 rows)                    │
│  ├── MART_DAY_AHEAD_PRICES      (5,760 rows)                    │
│  └── MART_VPP_PRICE_OPTIMIZATION (23M rows → pre-aggregated)    │
└──────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
05-vpp-monitor/
├── app.yml                       # App metadata (title, description, icon)
├── snowflake.yml                 # SPCS deployment configuration
├── package.json                  # Node.js dependencies
├── next.config.js                # Next.js config (standalone output)
├── tailwind.config.js            # Dark-mode theme with energy palette
├── tsconfig.json                 # TypeScript configuration
├── postcss.config.js             # PostCSS for Tailwind
├── sql/
│   └── create_views.sql          # Backend views DDL (run before deploying)
├── src/
│   ├── app/
│   │   ├── layout.tsx            # Root layout (dark HTML class)
│   │   ├── page.tsx              # Main dashboard page
│   │   ├── globals.css           # Tailwind imports + custom utilities
│   │   └── api/
│   │       ├── kpis/route.ts     # KPI summary endpoint
│   │       ├── timeseries/route.ts # Time-series endpoint
│   │       └── actions/route.ts  # Battery actions + margins endpoint
│   ├── components/
│   │   ├── FilterBar.tsx         # Region, type, date range filters
│   │   ├── KpiCard.tsx           # Metric card with colored accent
│   │   ├── PriceCapacityChart.tsx # Dual-axis line/area chart
│   │   ├── BatteryActionsChart.tsx # Stacked bar chart
│   │   └── RevenueChart.tsx      # Margin comparison bar chart
│   └── lib/
│       └── snowflake.ts          # Snowflake SDK connection helper
├── public/
│   └── icon.svg                  # App icon
└── README-module5.md             # This file
```

---

## Maintaining the App

### Update code and redeploy

```bash
# Edit files, then:
snow app deploy
```

The runtime detects code changes, rebuilds the image, and rolls out a new service version (zero-downtime if the health check passes).

### View logs

```bash
snow app events --last 200
```

Shows container stdout/stderr — useful for debugging API route errors or connection issues.

### Check status

```bash
snow app open --print-only   # Get the URL without opening browser
```

### Teardown

```bash
snow app teardown
```

This drops the SPCS service and associated resources. It does **not** drop the SQL views or base tables.

### Suspend and resume (cost control)

The app runs on a **Snowflake-managed shared compute pool** (`APP_SERVICE_*`). While running, it consumes approximately **0.02-0.03 credits/hour** (~0.5-0.7 credits/day, or roughly $1-2/day depending on your contract).

To stop costs without destroying the app:

```sql
ALTER APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR SUSPEND;
```

Suspending stops your container and de-schedules it from the shared pool. You are no longer billed. The managed pool's underlying VMs are Snowflake's concern — other services may share the same infrastructure.

To resume:

```sql
ALTER APPLICATION SERVICE SNOWFLAKE_APPS.PUBLIC.EPOWER_VPP_MONITOR RESUME;
```

Or simply open the app URL — since `auto_resume` is enabled, accessing the endpoint automatically resumes the service. Cold-start takes ~30-60 seconds.

| State | Credits/hour | What happens |
|-------|-------------|--------------|
| Running | ~0.03 | Container active, serving requests |
| Suspended | 0 | Container stopped, no billing, URL returns an error page |
| Auto-resuming | ~0.03 | Triggered by URL access, ~30-60s startup |

### Full cleanup

```sql
-- Remove views
USE ROLE EPOWER_ROLE;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_TIMESERIES;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_ACTIONS;
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.V_VPP_MONITOR_KPI;
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
| Infra | SPCS Compute Pool | Managed container execution inside Snowflake |

---

## Comparison: Traditional SPCS vs. Snowflake App Runtime

| Aspect | Traditional SPCS | Snowflake App Runtime |
|--------|-----------------|----------------------|
| Dockerfile | Write manually | Generated from package.json |
| Docker build | Local (requires amd64) | Remote (on compute pool) |
| Image push | Manual `docker push` to registry | Automatic |
| Service spec | Write YAML, `CREATE SERVICE` | Automatic from snowflake.yml |
| Endpoint DNS | Manual `CREATE SERVICE` with endpoints | Automatic HTTPS URL |
| TLS certificates | Managed by Snowflake (both) | Same |
| Code updates | Rebuild image, push, `ALTER SERVICE` | `snow app deploy` |
| Logs | `CALL SYSTEM$GET_SERVICE_LOGS(...)` | `snow app events` |
| Teardown | `DROP SERVICE`, `DROP COMPUTE POOL`, etc. | `snow app teardown` |

The App Runtime reduces a ~20-step deployment process to **3 steps**: setup, deploy, open.
