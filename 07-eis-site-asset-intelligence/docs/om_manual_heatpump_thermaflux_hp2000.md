# ThermaFlux HP2000 Large Heat Pump – Operation & Maintenance Manual (Excerpt)

**Manufacturer:** ThermaFlux Industrial Heat AG (fictional)
**Model:** HP2000 industrial / district heating heat pump
**Thermal output:** 2.0 MW_th · **Refrigerant:** R1234ze · **Nominal COP:** 3.2 (at 10 °C source / 70 °C supply)

---

## 1. Operating Principle
The HP2000 lifts low-temperature heat (from waste water, river water or industrial waste heat) to district heating supply temperature. It **consumes electricity**, which makes it ideal for **low and negative electricity price hours**. Heat produced in cheap hours can be stored in thermal storage for later use.

## 2. Key Performance Indicators
| KPI | Nominal | Warning | Critical |
|-----|---------|---------|----------|
| COP (seasonal) | 3.2 | < 2.8 | < 2.5 |
| Compressor starts per hour | ≤ 3 | > 4 | > 6 |

**Flexible operation note:** the HP2000 can ramp from 30 % to 100 % load in 5 minutes. To protect the compressor, keep it to **6 starts per hour or fewer**. Price-based schedules should use minimum run blocks of 1 hour.

## 3. Fault Codes
| Code | Description | Action |
|------|-------------|--------|
| H-110 | High pressure trip | Check condenser flow / supply temperature |
| H-220 | Compressor motor overload | Inspect motor, check supply voltage |
| H-305 | Low source temperature | Reduce load, check source pump |
| H-512 | Frequency converter fault | Reset; if repeated, replace converter module (kit TF-KIT-512, lead time 10 days) |

## 4. Maintenance
- Quarterly: filter cleaning on the source side and a refrigerant leak check.
- Annually: compressor oil analysis and frequency converter inspection.
- Long outages (> 3 days) are mostly caused by frequency converter failures (H-512). Keeping a spare converter module on site is recommended for sites with efficiency guarantees.
