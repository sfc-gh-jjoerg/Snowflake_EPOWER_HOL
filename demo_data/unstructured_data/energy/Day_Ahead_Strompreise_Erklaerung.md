# Day-Ahead Strompreise: So funktioniert der Strommarkt

## Der Strompreis wird taeglich neu bestimmt

### Was sind Day-Ahead Preise?

Day-Ahead Preise sind die Grosshandelspreise fuer Strom, die **einen Tag im Voraus** an der Stromboerse festgelegt werden. Jeden Tag um 12:00 Uhr werden die Preise fuer die 24 Stunden des Folgetages veroeffentlicht.

### Warum schwanken die Preise?

```
Typischer Tagesverlauf der Strompreise (Beispiel)

Preis
EUR/MWh
   │
120│                              ▲
   │                             ╱ ╲
100│                            ╱   ╲
   │        ▲                  ╱     ╲
 80│       ╱ ╲                ╱       ╲
   │      ╱   ╲              ╱         ╲
 60│     ╱     ╲────────────╱           ╲
   │    ╱                                ╲
 40│───╱                                  ╲───
   │  Nacht    Morgen   Mittag   Abend   Nacht
   └──────────────────────────────────────────►
                     Uhrzeit
```

**Preistreiber**:
| Faktor | Wirkung auf Preis |
|--------|-------------------|
| Hohe Nachfrage (morgens, abends) | ▲ Preis steigt |
| Viel Wind/Sonne | ▼ Preis sinkt |
| Kraftwerksausfaelle | ▲ Preis steigt |
| Feiertage/Wochenende | ▼ Preis sinkt |

### Was bedeutet das fuer Sie?

Mit einem **dynamischen Stromtarif** von EPOWER zahlen Sie den tatsaechlichen Boersenpreis (plus Netzentgelte und Abgaben). Das bedeutet:

- **Guenstige Stunden nutzen**: Waschmaschine mittags laufen lassen
- **Teure Stunden meiden**: Elektroauto nachts laden
- **Mit EPOWER profitieren**: Ihr Speicher optimiert automatisch

---

## Die Stromboerse EPEX SPOT

### Wo werden die Preise gemacht?

Die **EPEX SPOT** in Paris ist die fuehrende Stromboerse fuer Mitteleuropa. Hier treffen sich:
- **Verkaeufer**: Kraftwerksbetreiber, Windparks, Solaranlagen
- **Kaeufer**: Energieversorger wie EPOWER, Industrieunternehmen

### Die Marktzone DE-LU

Deutschland und Luxemburg bilden eine gemeinsame Preiszone. Der Preis gilt fuer das gesamte Gebiet - ob Sie in Hamburg oder Muenchen wohnen, der Grosshandelspreis ist identisch.

### Ablauf der Preisbildung

| Zeit | Ereignis |
|------|----------|
| Bis 12:00 | Alle Gebote fuer morgen eingereicht |
| 12:00 | Auktion startet |
| 12:42 | Ergebnisse veroeffentlicht |
| Ab 12:42 | Preise fuer 24 Stunden des Folgetages bekannt |

---

## Negative Strompreise

### Ja, manchmal ist Strom "kostenlos"

Bei sehr viel Wind und Sonne und wenig Nachfrage kann der Boersenpreis **negativ** werden. Das bedeutet: Erzeuger zahlen dafuer, dass jemand ihren Strom abnimmt.

**Wann passiert das?**
- Sonnige Fruehlingstage mit viel Wind
- Feiertage (Industrie steht still)
- Nachts bei starkem Wind

**Was bedeutet das fuer EPOWER?**
Ihr Speicher laed automatisch bei negativen Preisen:
- Sie bekommen guenstigen Strom
- EPOWER teilt 50% der Ersparnis mit Ihnen
- Sie helfen, ueberschuessigen Oekostrom zu nutzen

### Statistik 2023

| Monat | Stunden mit negativem Preis | Niedrigster Preis |
|-------|----------------------------|-------------------|
| Januar | 12 | -85 EUR/MWh |
| April | 48 | -130 EUR/MWh |
| Juli | 28 | -92 EUR/MWh |
| Oktober | 8 | -45 EUR/MWh |

---

## So sehen Sie die aktuellen Preise

### In der EPOWER App

1. EPOWER App oeffnen
2. "Energie" → "Strompreise"
3. Tages- oder Wochenansicht waehlen

### Online Quellen

| Quelle | Link | Aktualisierung |
|--------|------|----------------|
| EPEX SPOT | epexspot.com | 12:42 Uhr |
| Energy-Charts | energy-charts.info | 13:00 Uhr |
| Smard | smard.de | 13:00 Uhr |

### API-Zugang fuer Entwickler

EPOWER stellt eine API bereit:
```
GET https://api.eon.de/energy/prices/day-ahead
Authorization: Bearer {api_key}
```

Antwort:
```json
{
  "date": "2024-03-16",
  "market_zone": "DE-LU",
  "prices": [
    {"hour": 0, "price_eur_mwh": 42.15},
    {"hour": 1, "price_eur_mwh": 38.90},
    ...
  ]
}
```

---

## Dynamische Tarife bei EPOWER

### EPOWER Flex

Unser dynamischer Tarif basiert auf Day-Ahead Preisen:

**Zusammensetzung Ihres Strompreises**:
| Komponente | ca. Anteil |
|------------|------------|
| Boersenpreis (variabel) | 35% |
| Netzentgelte | 25% |
| Steuern & Abgaben | 30% |
| EPOWER Marge | 10% |

### Preisberechnung Beispiel

Boersenpreis: 80 EUR/MWh = 8 ct/kWh

| Position | Betrag |
|----------|--------|
| Boersenpreis | 8,00 ct/kWh |
| Netzentgelt | 8,50 ct/kWh |
| Stromsteuer | 2,05 ct/kWh |
| EEG-Umlage | 0,00 ct/kWh |
| EPOWER Aufschlag | 2,50 ct/kWh |
| **Endpreis** | **21,05 ct/kWh** |

### Sparpotenzial mit EPOWER

Mit EPOWER optimiert Ihr Speicher automatisch:
- Laden bei niedrigen Preisen
- Eigenverbrauch bei hohen Preisen
- Durchschnittliche Ersparnis: **15-25%** gegenueber Festpreistarif

---

## Glossar

| Begriff | Erklaerung |
|---------|------------|
| **MWh** | Megawattstunde = 1.000 kWh |
| **Day-Ahead** | Handel fuer den Folgetag |
| **Intraday** | Kurzfristiger Handel am selben Tag |
| **Merit Order** | Reihenfolge der Kraftwerke nach Kosten |
| **Spot-Markt** | Kurzfristiger Stromhandel |
| **Baseload** | Durchschnittspreis aller 24 Stunden |
| **Peakload** | Durchschnittspreis 8-20 Uhr |

---

## Weiterführende Informationen

- **Bundesnetzagentur**: www.bundesnetzagentur.de
- **Energy-Charts (Fraunhofer ISE)**: energy-charts.info
- **EPEX SPOT**: www.epexspot.com

---

*Stand: Maerz 2024*
