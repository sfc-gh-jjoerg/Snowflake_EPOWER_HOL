# EIS Flex – Program Guide

**EPOWER Infrastructure Solutions · Internal & Customer Information**

---

## 1. What is EIS Flex?
EIS Flex is EPOWER Infrastructure Solutions' program for **running large heat pumps on cheap electricity**. It applies the principle of the EPOWER Virtual Power Plant (residential batteries) to district heating and on-site energy centres.

A site needs the same amount of heat every day. With EIS Flex, the heat pump produces the day's heat **in the cheapest hours of the day** and fills the thermal storage. The storage supplies the heat in the expensive hours.

**Same heat, bought at the cheapest hours.**

## 2. The Rule
Prices: EPEX day-ahead, bidding zone DE-LU, hourly.

Per site and day:
1. Determine how much heat the heat pump has to deliver that day.
2. Rank the day's hours by day-ahead price.
3. Run the heat pump at full load in the cheapest hours until the day's amount is produced.
4. The thermal storage balances the difference: it **charges** when the heat pump produces more than the current demand and **discharges** when it produces less.

The storage size limits how much production can be shifted. CHP units and boilers are **not** part of EIS Flex. They operate heat-led as usual.

**Hard constraint:** heat demand is always met. EIS Flex changes *when* the heat pump runs, never *how much* heat is delivered.

## 3. Economics
- **Heat pump electricity cost** = electricity consumed × day-ahead price of the hour (COP 3.2: 1 MWh of heat needs ~0.31 MWh of electricity).
- **Flex margin** = electricity cost in normal operation − electricity cost with EIS Flex, for the same amount of heat.
- The margin is shared between EIS and the customer as defined in each contract (typically 60/40 or 70/30).

**Example:** 24 MWh of heat per day = 7.5 MWh of electricity. Normal operation at an average of €95/MWh costs €713. EIS Flex, running in the 10 cheapest hours at an average of €55/MWh, costs €413. **Flex margin: €300 per day.**

## 4. Eligibility
A site is a good EIS Flex candidate if it has:
- at least one large heat pump,
- thermal storage of at least 3 hours of average heat demand,
- no critical-supply restriction on storage use, or enough storage to keep the supply-security reserve.

Baseline sites with a heat pump and **idle storage** (state of charge flat, never cycled) are the **top onboarding candidates**.

## 5. Roles
| Layer | Responsibility |
|-------|----------------|
| Plant control / SCADA / EMS | Real-time control of units (seconds to minutes) |
| EIS Flex schedule | Next-day hourly heat pump schedule based on day-ahead prices |
| Analytics & AI layer | Monitoring, margin reporting, onboarding analysis, recommendations |

The schedule is a **recommendation** handed to plant control. Plant control keeps final authority to protect supply security and the equipment.
