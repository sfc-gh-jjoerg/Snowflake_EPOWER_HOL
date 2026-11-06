# Module 7: EIS Site & Asset Intelligence (with EIS Flex)

> **Status:** Ready for demo. Setup notebook: [`eis_setup.ipynb`](eis_setup.ipynb). The notebook's **story check** (section 9) shows the exact answers for your run; this README describes the story without fixed numbers, because they depend on the real day-ahead prices.
> **Prerequisite:** Module 1 (`01-agentic-ai-foundation/epower_hol_main.ipynb`) has been run.
> **Independent of:** Modules 2–6.

This module adds a second business unit to the EPOWER story: **EPOWER Infrastructure Solutions (EIS)**. EIS is a fictional B2B energy-infrastructure business in Germany, modelled on how decentralised energy-infrastructure providers operate. EIS finances, builds and runs heat and power assets at customer sites under long-term contracts, and it guarantees their availability and efficiency.

The demo tells one story: **unified OT and IT data → AI grounded in governed data → measurable € impact.**

---

## 1. The EIS Business Case and Domain

### 1.1 The domain: decentralised energy infrastructure
EIS works in the **B2B energy-infrastructure** market. Instead of selling electricity or gas, EIS **plans, finances, builds and operates energy centres on the customer's premises**: hospitals, industrial and chemical parks, housing estates, university campuses and urban district heating networks. The customer buys a **result** (reliable heat, power and cooling at an agreed price), not the plant itself.

**How the business model works:**
- **Long-term contracts (10–20 years):** energy contracting, Energy-as-a-Service or heat-supply agreements. EIS earns an annual service fee plus energy prices.
- **Performance guarantees:** EIS guarantees **availability** (the share of time the units are not in a fault) and **efficiency** of the plants, measured per quarter. Missing a guarantee triggers a **contractual penalty (Pönale)**.
- **Margin drivers:** uptime of the assets, fuel and electricity costs, maintenance cost, and, increasingly, the ability to run flexible assets such as heat pumps against **hourly electricity market prices**.
- **Market trends in Germany:** decarbonisation of heat (heat pumps replacing gas), municipal heat planning, rising electricity price volatility from renewables, and growing reporting duties (ESG/CO₂).

### 1.2 What EIS does

| Area | What EIS does |
|------|---------------|
| **District heating** | Operates heat networks for urban quarters (e.g. Hamburg-Altona) |
| **On-site generation** | CHP plants, large heat pumps, gas boilers and thermal storage at hospitals, industrial parks, housing estates and campuses |
| **Energy contracting** | 10–20 year contracts with **availability and efficiency guarantees**, plus penalties if they're missed |
| **Operations & maintenance** | Field technicians, OEM maintenance manuals, work orders |

**The data challenge:** OT telemetry from many OEM and SCADA systems, contracts stored as PDFs, maintenance data in ERP or field-service tools, and market prices all live in separate systems. No single view answers the question *"Where are we losing money, and why?"*

### 1.3 The business case: three use cases

| Use case | Business question | Before (today) | After (with the EIS agent on Snowflake) | Value lever |
|---|---|---|---|---|
| **1. Guarantee risk** | *Which contracts are at risk, and what is our € exposure?* | Guarantee breaches show up in the quarterly report, after the fact | Risk per contract in €, weeks before quarter end, combining OT data and contract terms | **Avoid penalties** |
| **2. Root cause & fix** | *Why is this unit underperforming, and what should the technician do?* | Faults are reset and restarted; nobody links repeated trips to a degrading asset; the manual is a PDF somewhere | Trend, fault history and open work order plus the procedure and spare part from the OEM manual, in one answer | **Repair faster, less downtime** |
| **3. EIS Flex** | *How much can we save by running heat pumps on cheap power, and where next?* | Heat pumps run whenever heat is needed, at any power price | Heat pumps produce the day's heat in the cheapest hours; storage covers the rest; realised and missed savings plus a ranked onboarding list and tomorrow's schedule | **Lower energy cost, roll-out business case** |

**Why Snowflake:** all three use cases need the **same combination**: structured OT and business data, unstructured documents (contracts, manuals) and external market data, governed in one place and accessible in natural language. That combination is what the demo shows; the individual analyses alone are not new.

**Who benefits:** operations managers (risk, maintenance planning), field service (fix instructions), commercial and energy management (flex savings, onboarding), and management (one view in €).

### 1.4 The assets in an energy centre

| Asset | Produces | Energy source | Part of EIS Flex? |
|---|---|---|---|
| **CHP** (combined heat & power, German *BHKW*) | Electricity and heat at the same time | Gas | No, runs heat-led |
| **Large heat pump** | Heat; 1 part electricity + ambient heat → ~3 parts heat (COP ≈ 3) | Electricity | **Yes**, the price-reactive asset |
| **Gas boiler** | Heat only, for peak load and backup | Gas | No, runs heat-led |
| **Thermal storage** | Stores hot water and releases the heat later | – | **Yes**, the prerequisite |

**Normal operation (heat-led):** each hour, the heat pump covers demand first as base load, then the CHP, then the boiler. In the generated fleet, two heat pumps together roughly match a site's peak demand. That leaves room to produce a day's heat in fewer, cheaper hours.

---

## 2. EIS Flex: Heat Pumps Running on Cheap Power

### 2.1 The idea
EIS Flex applies the same principle as the EPOWER **Virtual Power Plant** (Module 1) to large heat pumps: **use electricity when it is cheap.**

A site needs the same amount of heat every day. Without EIS Flex, the heat pump runs whenever heat is needed and pays whatever the power price is at that moment. **With EIS Flex, the heat pump produces the day's heat in the cheapest hours of the day and fills the thermal storage.** The storage then supplies the heat in the expensive hours.

> **Same heat, bought at the cheapest hours.**

| Asset | Role in EIS Flex |
|-------|------------------|
| **Large heat pump** | The only price-reactive asset. Runs at full load in the cheapest hours of the day |
| **Thermal storage** | The "battery" for heat. Charges when the heat pump produces more than needed, discharges when it produces less |
| **CHP** | Always heat-led (not part of EIS Flex) |
| **Gas boiler** | Backup, unchanged |

### 2.2 The rule
Per site and day:
1. Determine how much heat the heat pump has to deliver that day (the same amount as in normal operation).
2. Rank the day's hours by real EPEX day-ahead price (DE-LU).
3. Run the heat pump at full load in the cheapest hours until the day's amount is produced.
4. The storage balances the difference between production and demand:
   - production > demand → **charge**
   - production < demand → **discharge**

The storage size limits how much heat can be shifted. A small storage means only part of the production moves to cheap hours.

> **Simplifications in the demo model:** per day, at most 85 % of the storage capacity is used for shifting; storage losses are ignored; the state of charge (SOC) is derived from the daily charge/discharge balance. The stricter rules in the storage operating guideline (`docs/om_manual_thermal_storage.md`: 10–95 % SOC, max. 25 % charging per hour, 25 % minimum SOC at hospitals 06:00–22:00) are **not** simulated.

**Example (one day):** the heat pump has to deliver the same amount of heat as always.

| | Hours the heat pump runs | Power price paid | Result |
|---|---|---|---|
| Normal operation | Whenever heat is needed, including expensive hours | The price of each hour, cheap or expensive | Baseline cost |
| **EIS Flex** | The cheapest hours of the day; storage covers the rest | Only the cheapest hours | **Same heat, lower electricity cost** |

The more prices vary during a day, and the larger the storage, the bigger the saving. The demo calculates the exact amounts from the real EPEX prices.

### 2.3 The hard constraint: heat demand is always met
**The hospital must always get its heat.** EIS Flex only shifts *when* the heat pump produces heat, never *how much* heat is delivered. CHP and boiler operation is identical with and without EIS Flex.

### 2.4 Flex vs. baseline fleet
To make the value visible, the EIS fleet is split into two groups:

| Group | Operating mode | Share |
|-------|----------------|-------|
| **EIS Flex sites** | Heat pump runs in the cheapest hours | ~60% of sites |
| **Baseline sites** | Heat pump runs whenever heat is needed, no price signal | ~40% of sites |

Both groups use the same real day-ahead prices. The demo can therefore show two numbers:
- **Realised flex margin:** what EIS Flex sites earned compared with heat-led operation
- **Missed margin:** what the baseline sites *would* have earned if they had been on EIS Flex. This is the business case for rolling it out.

### 2.5 Next-day heat pump schedule
The daily Module 1 task (`TASK_DAILY_DATA_REFRESH`) already loads **tomorrow's** day-ahead prices. A view turns them into an **hourly heat pump schedule per EIS Flex site** for the next day, e.g. *"run the heat pumps at night and around midday; the storage covers the evening peak"*. Expected demand is the average of the same hour over the last 7 days. This needs no new task and no new pipeline.

### 2.6 Where Snowflake fits, and where it doesn't
| Layer | Owner |
|-------|-------|
| Real-time control of plants (seconds) | Plant control system, SCADA or EMS on site. **Not Snowflake.** |
| Trading and market bidding | Trading or optimisation systems |
| **Data unification, analytics, dispatch recommendation, AI agent** | **Snowflake** |

Snowflake is the **decision and recommendation layer** on top of existing OT and optimisation systems. It doesn't replace them. The rule-based schedule could later be extended to mathematical optimisation (e.g. linear programming in Snowpark Python) as a next step.

### 2.7 Key metrics

| Metric | Definition |
|---|---|
| **Flex margin** | Heat pump electricity cost in normal operation minus with EIS Flex, for the same heat (electricity = heat / COP × hourly price) |
| **Realised margin** | Flex margin on sites enrolled in EIS Flex |
| **Missed margin** | Potential flex margin on sites not enrolled (the roll-out business case) |
| **EIS / customer share** | Split of the margin per the contract's EIS Flex clause (typically 60/40 or 70/30; 70 % EIS assumed for sites not enrolled) |
| **COP** | Heat out / electricity in. Heat pump efficiency is stored as COP × 100 (320 = COP 3.2) |

### 2.8 When is a site suitable?
- **Good candidates:** at least one large heat pump, storage of at least ~3 hours of average heat demand, no supply restriction on storage use, and storage that is hardly used today. No new hardware needed: only the operating schedule changes.
- **Less suitable:** no heat pump or very small storage (some sites not enrolled have no heat pump and therefore no potential), little daily price variation, critical-supply sites that must keep a storage reserve, or assets with frequent faults (more starts mean more wear; the heat pump manual limits starts to 6 per hour).

---

## 3. Contract Guarantees and Asset Health

### 3.1 Guarantee logic
Contracts guarantee **availability** (share of time a unit is not in a fault) and **efficiency** per calendar quarter. The demo uses the **rolling last 30 days** as the leading indicator: *"if performance continues like this, this is the quarter's penalty"*.

| Contract basis | Meaning |
|---|---|
| `PER_UNIT` | Every unit in scope must meet the guarantee (e.g. each CHP at the hospital) |
| `AVERAGE` | The average across the units in scope must meet it |
| `SUPPLY` | Measured at heat-supply level (always met in the demo, because heat demand is always covered) |

- **Penalty exposure** = missed percentage points × penalty per point from the contract. Every full or **started** point counts (`CEIL`).
- **Status:** `AT_RISK` = below the guarantee, `WATCH` = less than 1 point headroom, `OK` otherwise.
- The guarantee terms of the hero contracts are also extracted from the contract documents with `AI_EXTRACT` and checked against the contract table.

### 3.2 Asset health score
Per generation unit over the last 30 days, a score from 0 to 100 (lower is worse): it is reduced by unavailability, a **sustained** efficiency decline (only counted with at least 20 days of data and a clear trend, R² ≥ 0.5), fault trips and alarm warnings. `CRITICAL` < 60, `WARNING` < 80, otherwise `GOOD`. For degrading CHP units the view also projects the days until efficiency falls below 85 %.

---

## 4. Architecture (keep it simple)

All EIS objects live in one new schema, **`EPOWER_DEMO.EIS_GOLD`**. There is no EIS Bronze or Silver layer and no dbt changes. Data is generated once in the notebook.

| Object | Type | Purpose |
|--------|------|---------|
| `EIS_SITES` | Table | 120 German B2B sites (hospital, industrial park, housing, district heating, campus), `flex_enabled` |
| `EIS_ASSETS` | Table | ~600 assets (CHP, heat pump, boiler, thermal storage) |
| `EIS_CONTRACTS` | Table | Contract terms, guaranteed availability/efficiency, penalty rates, flex margin share |
| `EIS_PARAMETERS` | Table | Technical parameters (heat pump COP, CHP and boiler efficiency) |
| `EIS_FAULT_EVENTS` | Table | Unplanned outages with fault codes (planted story events + random background faults) |
| `EIS_SITE_DISPATCH_HOURLY` | Table | 60 days hourly per site: heat demand, real day-ahead price, normal vs. EIS Flex heat pump schedule, storage, cost |
| `EIS_ASSET_TELEMETRY` | Table | 60 days hourly per asset: status, heat/power output, efficiency, storage SOC, fault codes |
| `EIS_WORK_ORDERS` | Table | Maintenance history (preventive + corrective) |
| `EIS_DOCS_PARSED` | Table | Parsed documents (`AI_PARSE_DOCUMENT`) |
| `EIS_CONTRACT_CLAUSES` | Table | Guarantee clauses extracted from the contract documents via `AI_EXTRACT` (shown and checked against `EIS_CONTRACTS`) |
| `V_EIS_ASSET_DAILY` | View | Daily KPIs per asset |
| `V_EIS_ASSET_HEALTH` | View | Efficiency drift, fault frequency, health score |
| `V_EIS_GUARANTEE_STATUS` | View | Guaranteed vs. actual, € penalty exposure per contract |
| `V_EIS_FLEX_MARGIN` | View | Realised and missed flex margin (heat pump electricity cost, normal vs. EIS Flex) |
| `V_EIS_DISPATCH_PLAN` | View | Next-day hourly heat pump schedule per Flex site |
| `EIS_OPERATIONS_SEMANTIC_VIEW` | Semantic View | Text-to-SQL over 6 business objects: sites, assets, asset health, guarantees, flex margin, heat pump schedule |
| `SEARCH_EIS_DOCS` | Cortex Search | OEM maintenance manuals, contracts, EIS Flex program guide |
| `EIS_OPERATIONS_AGENT` | Cortex Agent | Registered in CoWork as "EIS Operations" |

**Reused from Module 1 (read-only):** `EPOWER_GOLD.MART_DAY_AHEAD_PRICES`. The same market feed now serves a second business unit.

Planted anomalies make the demo answers come out the same every run:

| Site / asset | Planted anomaly | Story |
|---|---|---|
| Klinikum Hamburg-Nord, CHP-2 | Repeated F-217 trips, steadily falling efficiency, open work order without spare part | Below its availability guarantee → highest penalty exposure; root cause and fix from the OEM manual |
| Chemiepark Leuna, HP-1 | Multi-day H-512 outage | Just above the guarantee → WATCH |
| Campus Universität Kiel, CHP-1 | One longer F-142 outage | Slightly below the guarantee → smaller penalty exposure |
| Wohnquartier München-Riem | Heat pumps + storage, but not in EIS Flex | Among the top onboarding candidates (missed saving) |
| Wärmenetz Hamburg-Altona | EIS Flex with a very large storage tank | Highest realised saving; showcase for the heat pump schedule |

Documents live in [`docs/`](docs/), not in `demo_data/`, so they don't appear in the EPOWER agents' search services:

| Document | Content |
|---|---|
| `contract_klinikum_hamburg_nord.md` | Availability guarantee per CHP unit, penalty per point |
| `contract_chemiepark_leuna.md` | Average availability, heat pump COP guarantee, EIS Flex clause |
| `contract_waermenetz_altona.md` | Supply availability, EIS Flex clause and margin split |
| `om_manual_chp_ecopower_ec400.md` | CHP fault codes incl. **F-217**, cleaning procedure, spare part kit |
| `om_manual_heatpump_thermaflux_hp2000.md` | Heat pump fault codes incl. H-512, start limits |
| `om_manual_thermal_storage.md` | Storage limits and supply security reserve |
| `eis_flex_program_guide.md` | EIS Flex rule, economics, eligibility, roles |

---

## 5. Demo Story (3 moments)

> **Full demo script** with business case intro, talk track, questions (DE/EN), expected results, CIO Q&A and a pre-demo checklist: [`demo_flow_module7.md`](demo_flow_module7.md). Executive one-pager (German): [`eis_onepager_de.html`](eis_onepager_de.html). **Hand-out for colleagues (German)** combining business case, concepts and a modular demo (independent modules of max. 5 minutes, print-friendly): [`eis_handout_de.html`](eis_handout_de.html).

| Moment | Question to the agent | Wow moment |
|-----|-----------------------|-----------|
| **1. Risk & root cause** | *"Which contracts are at risk of missing their guarantee this quarter, and what is our € exposure?"* → follow-up: *"Why is Klinikum Hamburg-Nord CHP-2 below target, and what should the technician do?"* | OT telemetry + contract guarantees + OEM manual in one conversation: € at risk, root cause, concrete fix |
| **2. EIS Flex value** | *"How much did EIS Flex save in the last 30 days, and what are we missing on sites that are not enrolled?"* | Real EPEX prices → realised vs. missed € margin and the next sites to onboard |
| **3. Tomorrow** (short closer) | *"When should the Hamburg-Altona heat pumps run tomorrow?"* | Tomorrow's real market prices turned into an hourly heat pump schedule |

> **Presenter tip:** tomorrow's day-ahead prices are published around 13:00 CET and loaded by the Module 1 task around 17:00 CET. Before that, the schedule is for today and the agent says so. To show a real "tomorrow" plan earlier, run `CALL EPOWER_DEMO.EPOWER_OPS.FETCH_DAY_AHEAD_PRICES(CURRENT_DATE() + 1);` after 13:00 CET.

---

## 6. Setup

1. Run Module 1 (the day-ahead price pipeline must have at least 55 days of prices).
2. Open `07-eis-site-asset-intelligence/eis_setup.ipynb` in the Snowsight Workspace and **Run All** (~5–10 min). The CoWork registration cell needs ACCOUNTADMIN, as in Module 1.
3. Check the expected answers in the notebook's **story check** (section 9).
4. Ask the demo questions above in Snowflake CoWork with the **EIS Operations** agent.

**Cleanup:** [`cleanup-module7.sql`](cleanup-module7.sql) removes the agent from CoWork and runs `DROP SCHEMA EPOWER_DEMO.EIS_GOLD CASCADE`. Module 1 stays untouched.
