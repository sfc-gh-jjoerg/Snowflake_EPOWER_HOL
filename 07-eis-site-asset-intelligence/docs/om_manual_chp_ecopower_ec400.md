# EcoPower EC Series CHP Units (EC400 / EC2000) – Operation & Maintenance Manual (Excerpt)

**Manufacturer:** EcoPower Energietechnik GmbH (fictional)
**Models:** EC400 (400 kW_el / 520 kW_th) and EC2000 (2,000 kW_el / 2,600 kW_th) combined heat and power (CHP / BHKW) modules
**Fuel:** natural gas / biomethane
**Nominal total efficiency:** 88 % (electrical 38 %, thermal 50 %)

---

## 1. Operating Principle
The EC series uses a gas engine driving a synchronous generator. Engine cooling water and exhaust heat are recovered via a plate heat exchanger (cooling circuit) and an **exhaust gas heat exchanger (EGHE)**. Both feed the site heating circuit or the thermal storage tank.

The unit supports two operating modes:
- **Heat-led:** output follows the site heat demand.
- **Power-led / flexible:** output follows an external setpoint (e.g. a price-based dispatch schedule). Surplus heat must be absorbed by thermal storage.

## 2. Key Performance Indicators
| KPI | Nominal | Warning | Critical |
|-----|---------|---------|----------|
| Total efficiency | 88 % | < 85 % | < 82 % |
| Exhaust temperature after EGHE | 120 °C | > 140 °C | > 160 °C |
| Lube oil consumption | 0.2 g/kWh | > 0.4 g/kWh | > 0.6 g/kWh |

A **gradual decline in total efficiency** combined with **rising exhaust temperature after the EGHE** is the typical signature of exhaust heat exchanger fouling.

## 3. Fault Codes
| Code | Description | Typical cause | Action |
|------|-------------|---------------|--------|
| F-101 | Generator overcurrent | Grid disturbance | Auto-restart; check grid protection log |
| F-142 | Low lube oil pressure | Oil level / pump | Stop unit, check oil level and pump |
| **F-217** | **Exhaust heat exchanger fouling – high exhaust temperature** | **Soot / deposit build-up on EGHE tubes** | **See procedure 4.3** |
| F-305 | Cooling water over-temperature | Heat not absorbed (storage full, low demand) | Reduce load; check storage SOC and pumps |
| F-410 | Ignition misfire | Spark plug wear | Replace spark plugs (procedure 4.5) |

## 4. Maintenance Procedures

### 4.3 Procedure for F-217 – Exhaust Heat Exchanger Cleaning
**Trigger:** F-217 recurs more than 2 times in 14 days, **or** total efficiency drops below 85 % for more than 7 consecutive days.

1. Schedule a planned stop of 8–10 hours. On critical-supply sites (e.g. hospitals), make sure backup boilers and thermal storage cover the heat demand first.
2. Isolate the unit, then let it cool down to below 60 °C exhaust temperature.
3. Open the EGHE inspection covers and inspect the tube bundle for soot and deposits.
4. Clean with the approved chemical cleaning agent (spare part kit **EC-KIT-217**, incl. gaskets) and rinse.
5. Replace the inspection cover gaskets (included in EC-KIT-217).
6. Restart, then verify that the exhaust temperature after the EGHE is below 130 °C and that efficiency recovers to ≥ 87 % within 24 h.

**Important:** if the cleaning is postponed, efficiency keeps dropping by roughly 0.05–0.1 percentage points per day, and unplanned trips (F-217 shutdowns) become more frequent. These reduce availability.

**Recommended inspection interval:** every 4,000 operating hours. In flexible (power-led) operation with frequent start/stop cycles, every **3,000 operating hours**.

### 4.5 Spark Plug Replacement
Every 2,000 operating hours or after F-410. Spare part kit EC-KIT-410.

## 5. Spare Parts
| Kit | Content | Lead time |
|-----|---------|-----------|
| EC-KIT-217 | EGHE cleaning agent, inspection cover gaskets | 2 working days |
| EC-KIT-410 | Spark plug set (12) | 1 working day |
