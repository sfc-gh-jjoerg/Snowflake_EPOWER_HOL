# Prompt for Gemini Image Generation — EPOWER Energy Intelligence Wimmel Picture

Create a detailed, colorful **Wimmel-style illustration** (busy scene / "Wimmelbild") for the **EPOWER Energy Intelligence Demo** — a Snowflake-powered AI platform for a German energy retail company. The style should be friendly, modern, slightly playful vector art with clean lines and vivid colors — similar to a tech company infographic crossed with a Where's Waldo scene. Landscape format (16:9).

## Central Element — The Snowflake Platform (heart of the picture)

In the center, place a large glowing building or hub labeled **"Snowflake AI Data Cloud"** with the Snowflake logo/snowflake icon. This is the data & AI brain. Inside or around it, show three visible layers stacked like floors:
- **Bronze layer** (copper/brown tint) — raw data flowing in: IoT sensor signals, API data streams, documents - arrows between data items in the bronze layer as this layer is used as landing zone
- **Silver layer** (silver/grey tint) — cleaning & transformation: small dbt logos, data being enriched and aggregated
- **Gold layer** (gold tint) — polished business data: charts, KPIs, semantic models glowing with structure

On top of the Snowflake hub, place a glowing **Snowflake Intelligence Agent** — a friendly AI assistant character (robot / holographic) friendly looking figure receiving questions from Business Users in both **German and English**, e.g. "Zeige Strompreis vs. Batterie-Ladezustand" and "Show VPP margins by price zone". The agent has access to tools for retrieval visualized through arms:
- Left arm reaches to **Semantic Views** (7 glowing data lenses labeled Sales, Billing, Service, Customer, HR, VPP, Market Prices) — representing text-to-SQL
- Right arm reaches to **Cortex Search** (a magnifying glass over stacked documents with a "9" badge) — representing Hybrid Search on PDFs and service docs
- There is also a connection downward from Snowflake Intelligence to a glowing **MCP Server** portal (labeled "MCP — 15 Tools") — a universal plug/socket where external AI clients can connect to the platform and its tools

## Left Side — The Energy World (physical reality)

Top-left: A **German residential neighborhood** with:
- Houses with **solar panels on rooftops** and **battery storage units** in garages (labeled "EPOWER VPP")
- An **EPOWER gateway device** (small IoT box) on one house, sending data signals (dotted lines) toward the Snowflake hub
- A **heat pump** next to one house (no gas connection!)
- An **EV charging wallbox** with an electric car plugged in
- A **smart meter** on a house wall showing kWh readings
- Small labels: "Prosumer", "Bidirectional Energy Flow" with arrows going both to and from the grid
- A **70/30 coin-split icon** near a battery — showing 70% flowing to the homeowner and 30% to EPOWER (the VPP revenue share)

Top-left corner: **Wind turbines** and a **solar farm** in the background landscape

Bottom-left: A **traditional customer** area:
- Houses connected to the grid only (no solar, no battery)
- A **power line / distribution grid** connecting them to the main grid, but it should still look modern
- Label: "Consumer — Grid Only"

## Right Side — The Business Operations

Top-right: **EPOWER Headquarters** — a modern office building with the **EPOWER** logo. Inside, show:
- A **customer service center** with agents at screens, with service ticket bubbles (some red/negative sentiment, some green/positive)
- A **sales dashboard** on a wall screen showing charts
- An **HR department** corner with employee data

Mid-right: **VPP Monitor Dashboard** (Module 2) — a large screen or monitor showing the operational dashboard:
- A **map of Germany** with 14 VPP cluster dots color-coded (green = exporting, red = importing)
- Timeseries charts showing battery SOC and electricity prices (inverse correlation visible)
- Label: "VPP Monitor — Snowflake App Runtime"
- Small note: "Next.js • snow app deploy • No Docker"

Below that: **Customer Portal 'Mein EPOWER'** (Module 3) — a tablet showing self-service portal with meter reading submission

Bottom-right: A **control room / operations center** with:
- Large screens showing **day-ahead electricity prices** as a time-series chart (with high/low price zones colored red/green)
- A **battery charge/discharge diagram** showing the VPP strategy: "Buy Low → Store → Sell High"
- Revenue split visualization: **70% Customer / 30% EPOWER**
- Label: "Virtual Power Plant Control"

## Bottom Center — The Data Pipeline

Show a visible **data flow pipeline** running along the bottom:
1. **Energy-Charts API** (a cloud with "Fraunhofer ISE" label) sending **real EPEX day-ahead prices** into the Snowflake hub
2. **IoT telemetry signals** (from the EPOWER gateways) flowing as data streams — label "~17.5M rows / 60 days"
3. **Domain Data**: Sales, Billing, Service, HR, Customer
4. A **clock/schedule icon** labeled "Daily Task 17:00 CET" showing the automated refresh cycle: prices → telemetry → sales → billing → service → dbt
5. **dbt logo** with arrows showing Bronze → Silver → Gold transformation — label "16 dbt Models, Medallion Architecture + Semantic Views"
6. The word **"EPOWER_DataTeam"** on a small operations panel showing: Stored Procs, Tasks, dbt-project

## Scattered Throughout (Wimmel details)

- Small **Cortex AI** sparkle icons near insights being generated
- A person asking a question in natural language to a screen, getting a chart back
- A **Git logo** connected to the Snowflake workspace (showing code sync — "Workspace from Git")
- An **MCP plug icon** near a laptop running an external AI client (Cursor or Claude Desktop), connected back to the Snowflake hub
- Cute details: a cat on a solar panel, a bird on a wind turbine, a dog near a heat pump, kids on bikes
- Some speech bubbles in German: "Wie hoch ist der Stromverbrauch?", "Welche Kunden haben Wärmepumpen?"
- A small sign: "Making Enterprise Data AI-Ready"
- Another sign: "From Data to Decisions — Grounded in Governed Data"
- A **demo script clipboard** labeled "demo_flow.md — 5 Questions, 3 Acts" held by a presenter character
- Real-world company logos (subtle, small) near VPP houses: "1KOMMA5°", "Sonnen" — hinting at real-world counterparts

## Color Palette

- Snowflake blue (#29B5E8) as the primary accent
- Energy green for renewable/solar elements
- Warm copper/bronze, cool silver, rich gold for the medallion layers
- German-inspired architectural details (half-timbered houses, red brick)
- Bright, optimistic, professional but approachable

## Text Elements to Include

- "EPOWER — Retail Energy Services" (top banner)
- "Snowflake Intelligence & Cortex AI Agents" (center)
- "Making Enterprise Data AI-Ready" (as a banner or sign)
- "From Data to Decisions — Grounded in Governed Data" (near the agent)
- "Virtual Power Plant", "Semantic Views", "Cortex Search", "dbt Pipelines", "MCP Server"
- "9 Search Services", "7 Semantic Views", "15 MCP Tools"
- Mix of German and English labels throughout

## DO NOT Include

Generic cloud computing imagery, abstract data visualizations without context, or any elements unrelated to the energy retail / Snowflake AI narrative. No two-phase or heuristic references — all telemetry is price-reactive using real market data.
