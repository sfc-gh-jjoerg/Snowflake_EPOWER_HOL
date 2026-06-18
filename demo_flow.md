# EPOWER Energy Intelligence Demo — Demoskript

**EPOWER Energie Deutschland** — 20.000 Kunden, 360°-Energiestrategie. Im Zentrum: das **ePulse Virtual Power Plant (VPP)** mit ~4.050 Heim-Batterien, die bei günstigen Strompreisen laden und bei teuren entladen. Erlöse: 70% Kunde / 30% EPOWER.

---

## Die 6 Kernfragen

**1 — Geschäft & Segmente** *(Sales + Kunden)*

> *„Überblick über unser Geschäft: Umsatz nach Produktkategorie und Region, Vertragswerte nach Kundensegment."*

| Tools | `energy_sales_analyst` |
|-------|------------------------|
| Aha-Effekt | Gewerbekunden: nur 7%, aber 6x Vertragswert. South dominiert Solar-Umsatz. East wächst am schnellsten. |

---

**2 — Kundenanalyse + Dokumentation** *(cross-domain, RAG + SQL)*

> *„Welche Kunden mit hohem Verbrauch haben noch keine Solaranlage? Was empfiehlt unsere Produktdokumentation?"*

| Tools | `customer_energy_analyst` + `product_docs_search` |
|-------|---------------------------------------------------|
| Aha-Effekt | North-Kunden erscheinen überproportional (niedrigste Solar-Quote) — regionale Vertriebschance. Agent kombiniert Datenbank + Dokumente. |

---

**3 — Service + Handlungsempfehlung** *(handlungsorientiert)*

> *„Welche Regionen haben die meisten negativen Service-Tickets? Leite konkrete Maßnahmen ab."*

| Tools | `service_analyst` |
|-------|-------------------|
| Aha-Effekt | East sticht hervor (Wachstumsschmerzen bei Installation). Winter-Peak bei HP-Beschwerden sichtbar. Agent empfiehlt Maßnahmen — nicht nur Zahlen. |

---

**4 — VPP: Preis-Batterie-Korrelation** *(cross-domain, Chart)*

> *„Zeige Strompreis vs. Batterie-Ladezustand der letzten 7 Tage. Reagiert das VPP auf den Markt?"*

| Tools | `vpp_telemetry_analyst` + `market_prices_analyst` + `data_to_chart` |
|-------|----------------------------------------------------------------------|
| Aha-Effekt | Inverse Korrelation als Chart — der Beweis, dass 4.050 Batterien autonom auf echte EPEX-Preise reagieren. |

---

**5 — Upsell-Strategie** *(cross-domain, handlungsorientiert)*

> *„Analysiere VPP-Effizienz und Umsatztrend. Welche Kunden ohne Batterie haben das größte Potenzial? Erstelle eine Strategie."*

| Tools | `vpp_telemetry_analyst` + `energy_sales_analyst` + `customer_energy_analyst` |
|-------|-----------------------------------------------------------------------------|
| Aha-Effekt | Agent verknüpft 3 Domains zu einer Vertriebsstrategie. Gewerbekunden in North/East = Top-Potenzial. |

---

**6 — Executive Summary** *(alle Domains, handlungsorientiert)*

> *„Executive Summary: Umsatz, VPP-Performance, Kundenzufriedenheit, Personal — und drei Maßnahmen fürs nächste Quartal."*

| Tools | `energy_sales_analyst` + `vpp_telemetry_analyst` + `service_analyst` + `hr_analyst` + `energy_docs_search` |
|-------|-------------------------------------------------------------------------------------------------------------|
| Aha-Effekt | Agent aggregiert 5 Tools in einer strategischen Antwort — demonstriert Orchestrierung über alle Domains. |

---

## Übersicht

| # | Domänen | Cross-Domain | RAG | Handlung |
|---|---------|:---:|:---:|:---:|
| 1 | Sales, Kunden | | | |
| 2 | Kunden, Produkt-Docs | x | x | |
| 3 | Service | | | x |
| 4 | VPP, Marktpreise | x | | |
| 5 | VPP, Sales, Kunden | x | | x |
| 6 | Sales, VPP, Service, HR, Docs | x | x | x |

---

## Tipps

- **Frage 1** zeigt sofort regionale und segment-bezogene Unterschiede — kein Flat-Chart
- **Frage 4** ist der zentrale Aha-Moment — hier beweist sich das VPP mit echten Marktdaten
- **Fragen 3, 5, 6** sind handlungsorientiert — Agent liefert Strategien, nicht nur Daten
- **Follow-ups** nach jeder Frage: „Aufschlüsselung nach Region", „Zeige als Chart", „Erkläre das VPP-Programm" (triggert RAG)
- **Natürliche Sprache**: Kurze, direkte Fragen — zeigt, dass keine perfekte Formulierung nötig ist

---

## Datencharakteristik

| Dimension | Erwartetes Muster |
|-----------|-------------------|
| **Regionen** | South = Solar-Champion (85%), North = HP-stark (80%), West = E-Mobility/Gewerbe, East = Wachstum + Installationsprobleme |
| **Segmente** | Gewerbe: 6x Vertragswert, 3-6 Verträge. Privat: 1-3 Verträge |
| **Zeittrends** | YoY-Wachstum, Solar-Peak Frühjahr, HP-Peak Herbst |
| **Service** | East: negatives Sentiment-Cluster. Winter: HP-Beschwerden +80% |

---

## Technische Komponenten

| Komponente | Details |
|-----------|---------|
| **Agent** | `EPOWER_AGENT` (12 Tools: 7 Analyst + 4 Search + 1 Chart) |
| **Semantic Views** | 7 (Sales, Billing, Service, Customer Energy, HR, VPP, Market Prices) |
| **Cortex Search** | 9 Services (4 Dokument-RAG + 5 Column Lookup) |
| **Datenbank** | `EPOWER_DEMO` (Medallion: Bronze → Silver → Gold) |
| **MCP Server** | `EPOWER_MCP_SERVER` |

---

*EPOWER Energy Intelligence Demo — Powered by Snowflake Cortex*
