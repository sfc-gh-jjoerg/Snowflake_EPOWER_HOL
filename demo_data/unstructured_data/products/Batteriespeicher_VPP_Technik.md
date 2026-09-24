# Batteriespeicher im Virtuellen Kraftwerk: Technischer Leitfaden

## Technische Anforderungen fuer EPOWER VPP

### Kompatible Batteriespeicher

| Hersteller | Modellreihe | Min. Kapazitaet | VPP-Ready |
|------------|-------------|-----------------|-----------|
| EPOWER | SolarBattery 5/10/15 | 5 kWh | Ja |
| BYD | HVS/HVM | 5.1 kWh | Ja |
| LG Energy | RESU Prime | 6.5 kWh | Ja |
| Sonnen | sonnenBatterie 10 | 5.5 kWh | Ja |
| VARTA | pulse neo | 6.5 kWh | Ja |
| Huawei | LUNA2000 | 5 kWh | Ja |

### Systemvoraussetzungen

```
┌─────────────────────────────────────────────────────────────────┐
│                   TECHNISCHE ARCHITEKTUR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    │
│   │   Batterie  │◄──►│   Gateway   │◄──►│  EPOWER Cloud   │    │
│   │   System    │    │   EPOWER    │    │   VPP Backend   │    │
│   └─────────────┘    └─────────────┘    └─────────────────┘    │
│         │                  │                    │               │
│         ▼                  ▼                    ▼               │
│   Modbus TCP/IP      MQTT over TLS        REST API             │
│   oder Sunspec       Port 8883            Aggregator           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Batterie-Anforderungen
- Mindestkapazitaet: **5 kWh**
- Maximale Entladeleistung: mindestens **2,5 kW**
- Rundtrip-Effizienz: mindestens **90%**
- Kommunikation: Modbus TCP/IP oder Sunspec

#### Netzwerk-Anforderungen
- Stabiles WLAN (min. 2 Mbit/s) oder LAN
- Ausgehende Ports: 8883 (MQTT), 443 (HTTPS)
- Latenz zum Gateway: < 100ms

#### Gateway-Spezifikationen
| Eigenschaft | Wert |
|-------------|------|
| Abmessungen | 120 x 80 x 30 mm |
| Stromversorgung | 5V USB (Netzteil inkl.) |
| WLAN | 802.11 b/g/n (2.4 GHz) |
| LAN | RJ45 10/100 Mbit |
| Protokoll | MQTT over TLS 1.3 |
| Polling-Intervall | 1 Sekunde |
| Steuerlatenz | < 500ms |

---

## Kommunikationsprotokoll

### Telemetrie-Daten (Gateway → Cloud)

Das Gateway sendet alle **5 Sekunden** folgende Daten:

```json
{
  "gateway_id": "GW-2024-001234",
  "timestamp": "2024-03-15T14:30:05.123Z",
  "telemetry": {
    "battery_soc_pct": 72.5,
    "battery_power_kw": 2.3,
    "solar_yield_kw": 4.8,
    "grid_import_kw": 0.0,
    "grid_export_kw": 1.2,
    "heatpump_consumption_kw": 0.8
  },
  "status": {
    "online": true,
    "vpp_enabled": true,
    "error_code": null
  }
}
```

### Steuerbefehle (Cloud → Gateway)

| Befehl | Parameter | Beschreibung |
|--------|-----------|--------------|
| `SET_MODE` | IDLE, CHARGE, DISCHARGE | Betriebsmodus setzen |
| `SET_POWER` | -10.0 ... +10.0 kW | Lade-/Entladeleistung |
| `SET_SOC_LIMIT` | 10 ... 90 % | SOC-Grenzen setzen |
| `PAUSE_VPP` | Dauer in Minuten | VPP temporaer deaktivieren |

Beispiel Steuerbefehl:
```json
{
  "command": "SET_POWER",
  "value": -3.5,
  "duration_seconds": 900,
  "priority": "GRID_STABILIZATION",
  "timestamp": "2024-03-15T14:30:00Z"
}
```

---

## Batteriemanagement im VPP

### SOC-Strategie (State of Charge)

```
SOC %
100 ┤████████████████████████████████████████
    │████████ NICHT VERFUEGBAR (Puffer) ████
 90 ┤────────────────────────────────────────
    │
    │        VPP VERFUEGBAR (60%)
    │        Positive + Negative Regelung
    │
 30 ┤────────────────────────────────────────
    │████████████████████████████████████████
 20 ┤███ EIGENVERBRAUCH RESERVE (20%) ██████
    │████████████████████████████████████████
 10 ┤────────────────────────────────────────
    │████████ TIEFENTLADESCHUTZ █████████████
  0 ┴────────────────────────────────────────
```

| Zone | SOC-Bereich | Verwendung |
|------|-------------|------------|
| Tiefentladeschutz | 0-10% | Niemals unterschritten |
| Eigenverbrauch | 10-30% | Reserve fuer Haushalt |
| VPP verfuegbar | 30-90% | Fuer Netzregelung nutzbar |
| Puffer oben | 90-100% | Fuer Solarueberschuss |

### Zyklenmanagement

Um die Batterielebensdauer zu maximieren:

1. **Tiefentladung vermeiden**: SOC nie unter 10%
2. **Vollladung begrenzen**: Selten ueber 95%
3. **Teilzyklen bevorzugen**: 30-80% optimal
4. **Temperaturueberwachung**: 15-25°C ideal

**Jaehrliche Zyklen durch EPOWER**:
- Garantiert: max. 250 Zyklen/Jahr
- Typisch: 150-200 Zyklen/Jahr
- Aequivalent: ca. 0,5 Zyklen/Tag

---

## Regelleistungsarten

### Primaerregelung (FCR)

| Eigenschaft | Wert |
|-------------|------|
| Reaktionszeit | < 30 Sekunden |
| Haltedauer | 15 Minuten |
| Typische Leistung | 0,5 - 2 kW |
| Haeufigkeit | 10-20x pro Woche |

**Einsatz**: Sofortige Frequenzstabilisierung bei Netzschwankungen

### Sekundaerregelung (aFRR)

| Eigenschaft | Wert |
|-------------|------|
| Reaktionszeit | < 5 Minuten |
| Haltedauer | 15-60 Minuten |
| Typische Leistung | 1 - 5 kW |
| Haeufigkeit | 5-10x pro Woche |

**Einsatz**: Ausgleich von Prognoseabweichungen

### Minutenreserve (mFRR)

| Eigenschaft | Wert |
|-------------|------|
| Reaktionszeit | < 15 Minuten |
| Haltedauer | 15 Min - 4 Stunden |
| Typische Leistung | 2 - 5 kW |
| Haeufigkeit | 2-5x pro Woche |

**Einsatz**: Laengerfristiger Ausgleich, Kraftwerksausfaelle

---

## Installation des EPOWER Gateways

### Schritt 1: Standortwahl

- Max. 5m vom Wechselrichter/BMS entfernt
- Gute WLAN-Abdeckung (mind. -70 dBm)
- Trocken, staubgeschuetzt
- Temperaturbereich: 5-40°C

### Schritt 2: Verbindung zum Batteriesystem

**Option A: LAN (empfohlen)**
```
Wechselrichter [LAN] ───► [LAN] Gateway [WLAN] ───► Router
```

**Option B: WLAN**
```
Wechselrichter [LAN] ───► [WLAN] Gateway [WLAN] ───► Router
```

### Schritt 3: Konfiguration

1. Gateway mit Strom versorgen (USB)
2. EPOWER App oeffnen → EPOWER → Gateway hinzufuegen
3. QR-Code auf Gateway scannen
4. WLAN-Zugangsdaten eingeben
5. Batteriesystem auswaehlen
6. Modbus-Adresse eingeben (Standard: 1)

### Schritt 4: Verifizierung

Nach erfolgreicher Einrichtung:
- LED am Gateway: Gruen (verbunden)
- App zeigt: "Gateway online"
- Telemetrie: Werte werden angezeigt

---

## Fehlerdiagnose

### Haeufige Probleme

| Symptom | Ursache | Loesung |
|---------|---------|---------|
| Gateway offline | WLAN-Verbindung unterbrochen | Router neu starten, Gateway neu verbinden |
| Keine Telemetrie | Modbus-Fehler | Modbus-Adresse pruefen, Kabel checken |
| VPP pausiert | SOC zu niedrig | Batterie laden lassen |
| Steuerung reagiert nicht | Wechselrichter im Fehlermodus | Wechselrichter-Status pruefen |

### LED-Statuscodes

| LED-Muster | Bedeutung |
|------------|-----------|
| Gruen konstant | Verbunden, bereit |
| Gruen blinkend | Daten werden gesendet |
| Gelb konstant | Verbunden, VPP pausiert |
| Rot blinkend | Verbindungsfehler |
| Rot konstant | Hardware-Fehler |

### Log-Dateien

Gateway-Logs koennen ueber die App eingesehen werden:
1. App → EPOWER → Gateway → Diagnose
2. "Logs exportieren" waehlen
3. Per E-Mail an Support senden

---

## Sicherheit

### Verschluesselung

- **Transport**: TLS 1.3 (MQTT und HTTPS)
- **Authentifizierung**: X.509 Zertifikate
- **Daten**: AES-256 verschluesselt

### Zugriffskontrolle

- Gateway akzeptiert nur signierte Befehle von EPOWER
- Jedes Gateway hat eindeutiges Zertifikat
- Zertifikatsrotation alle 90 Tage automatisch

### Notfall-Abschaltung

Bei Kommunikationsverlust > 5 Minuten:
1. Gateway wechselt in sicheren Modus
2. Batterie arbeitet im normalen Eigenbetrieb
3. Keine externen Steuerbefehle werden ausgefuehrt

---

## Technischer Support

**Technische Hotline**:
- Telefon: 0800 - 22 33 560
- E-Mail: epower-technik@eon.de
- Servicezeiten: Mo-Fr 7-22 Uhr, Sa 8-18 Uhr

**Installateur-Support**:
- Partner-Portal: partner.eon.de/epower
- Schulungen: Online-Webinare (monatlich)

---

*Stand: Maerz 2024 | Technische Dokumentation v3.2*
