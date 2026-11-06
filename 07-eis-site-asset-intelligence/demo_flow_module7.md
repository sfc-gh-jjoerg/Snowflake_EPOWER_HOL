# EIS Site & Asset Intelligence – Demo-Skript (Modul 7)

**Zielgruppe:** CIO / Management, keine Domänen-Experten
**Dauer:** 20–25 Minuten (5 Min. Einstieg, 15 Min. Demo, 5 Min. Abschluss)
**Agent:** **EIS Operations** (`EPOWER_DEMO.EIS_GOLD.EIS_OPERATIONS_AGENT`) in Snowflake CoWork
**Begleitmaterial:** [One-Pager (DE)](eis_onepager_de.html), [Hand-out für Kollegen mit modularer Demo (DE)](eis_handout_de.html), [README-module7.md](README-module7.md)

> Die Fragen sind jeweils auf Deutsch und Englisch angegeben. Der Agent antwortet in der Sprache der Frage. Ein Sprachwechsel mitten in der Demo ist ein kleiner Wow-Moment.

---

## Checkliste vor der Demo

| # | Prüfpunkt | Wie |
|---|---|---|
| 1 | Modul 1 und Modul 7 sind aufgesetzt | `eis_setup.ipynb` lief ohne Fehler |
| 2 | Erwartete Antworten kennen | Notebook-Zelle **Story Check** (Abschnitt 9) ausführen und die Zahlen notieren |
| 3 | Strompreise für morgen sind geladen | Ab ca. 17:00 MEZ automatisch. Früher (nach 13:00 MEZ): `CALL EPOWER_DEMO.EPOWER_OPS.FETCH_DAY_AHEAD_PRICES(CURRENT_DATE() + 1);` |
| 4 | Agent ist in CoWork sichtbar | CoWork öffnen → Agent **EIS Operations** auswählen |
| 5 | Eine Testfrage stellen | Damit Warehouse und Agent „warm" sind |

---

## 1. Einstieg: der Business Case (ca. 5 Min., ohne Demo)

*Optional den One-Pager zeigen.*

**Talk Track (DE):**

> „Stellen Sie sich ein Unternehmen vor, das Energieanlagen bei seinen Kunden baut und betreibt: Blockheizkraftwerke im Krankenhaus, Wärmepumpen im Fernwärmenetz, Speicher im Industriepark. Die Verträge laufen 15, 20 Jahre, und das Unternehmen **garantiert**, dass die Anlagen laufen. Wird die Garantie verfehlt, zahlt es eine Vertragsstrafe.
>
> Die Herausforderung: Die nötigen Informationen liegen verstreut. Betriebsdaten in den Leitsystemen, Wartungsaufträge im ERP, Garantien im Vertrags-PDF, Reparaturanleitungen im Herstellerhandbuch, Strompreise an der Börse. Niemand hat das Gesamtbild. Probleme fallen oft erst im Quartalsbericht auf, und Wärmepumpen laufen unabhängig davon, ob Strom gerade teuer oder billig ist.
>
> Heute zeige ich Ihnen am Beispiel unseres fiktiven Unternehmens **EPOWER Infrastructure Solutions**, wie eine Daten- und KI-Plattform drei Fragen beantwortet: **Wo verlieren wir gerade Geld? Warum? Und wo können wir sofort sparen?**"

**Kernbotschaft in einem Satz:** *Betriebsdaten, Verträge und Handbücher auf einer Plattform – ein Agent, der in Euro antwortet und konkrete Maßnahmen empfiehlt.*

---

## 2. Moment 1: Risiko & Ursache (ca. 6 Min.)

### Frage 1a: Welche Verträge sind gefährdet?

> DE: *„Welche Verträge laufen Gefahr, in diesem Quartal ihre Garantie zu verfehlen, und wie hoch ist unser Pönale-Risiko?"*
>
> EN: *"Which contracts are at risk of missing their guarantee this quarter, and what is our € exposure?"*

| | |
|---|---|
| **Was passiert** | Der Agent nutzt `eis_analyst` (semantische Sicht) und kombiniert Betriebsdaten der Anlagen mit den Garantien aus den Verträgen. |
| **Erwartetes Ergebnis** | Klinikum Hamburg-Nord mit dem höchsten Risiko (BHKW-2 unter der garantierten Verfügbarkeit), dazu ein kleinerer Fall am Campus Kiel und Chemiepark Leuna „unter Beobachtung". Jeweils mit Euro-Betrag. |
| **Talking Point** | „Das ist keine vorgefertigte Auswertung. Die Frage wurde in normaler Sprache gestellt, die Antwort kommt in Euro. Und zwar jetzt, nicht am Quartalsende." |

### Frage 1b: Warum, und was ist zu tun?

> DE: *„Warum liegt das BHKW-2 im Klinikum Hamburg-Nord unter Plan, und was soll der Techniker tun?"*
>
> EN: *"Why is Klinikum Hamburg-Nord CHP-2 below target, and what should the technician do?"*

| | |
|---|---|
| **Was passiert** | Der Agent verkettet zwei Werkzeuge: `eis_analyst` findet den sinkenden Wirkungsgrad, die wiederholten Störungen F-217 und den offenen Arbeitsauftrag. `eis_docs_search` holt die passende Reparaturanleitung und das Ersatzteil aus dem Herstellerhandbuch. |
| **Erwartetes Ergebnis** | Ursache: verschmutzter Abgaswärmetauscher. Maßnahme: Reinigung nach Handbuch-Prozedur, Ersatzteil-Kit bestellen. Der Arbeitsauftrag zeigt: Bisher wurde nur neu gestartet, kein Ersatzteil bestellt. |
| **Talking Point (Wow)** | „Das ist der Moment, den es so bisher nicht gibt: Messdaten aus der Anlage, die Klausel aus dem Vertrag und die Anleitung aus dem Handbuch in **einer** Antwort. Der Techniker weiß, was zu tun ist, bevor die Pönale fällig wird." |

**Optionale Nachfrage:** *„Zeige den Wirkungsgrad-Verlauf von BHKW-2 als Chart."* Der Chart zeigt einen klar fallenden Trend.

---

## 3. Moment 2: EIS Flex, gleiche Wärme, günstigerer Strom (ca. 6 Min.)

**Kurz erklären (ohne Fachbegriffe):**

> „Der Strompreis an der Börse ändert sich jede Stunde. Eine Wärmepumpe braucht Strom, um Wärme zu erzeugen. Mit einem Wärmespeicher muss sie nicht genau dann laufen, wenn Wärme gebraucht wird. Sie kann die Wärme des Tages in den günstigsten Stunden erzeugen und speichern. Das ist wie beim Handy, das man nachts lädt. Gleiche Wärme, niedrigere Stromkosten, ohne neue Anlagen."

### Frage 2a: Was bringt EIS Flex?

> DE: *„Wie viel hat EIS Flex in den letzten 30 Tagen eingespart, und was entgeht uns bei den Standorten, die noch nicht teilnehmen?"*
>
> EN: *"How much did EIS Flex save in the last 30 days, and what are we missing on sites that are not enrolled?"*

| | |
|---|---|
| **Erwartetes Ergebnis** | Eine realisierte Ersparnis bei den Flex-Standorten und eine entgangene Ersparnis bei den übrigen Standorten (beides in Euro, auf Basis echter Börsenpreise). Das Fernwärmenetz Hamburg-Altona ist der Spitzenreiter. |
| **Talking Point** | „Das sind echte Strompreise der Börse EPEX, täglich automatisch geladen. Dieselben Daten nutzt übrigens schon unser virtuelles Kraftwerk aus Modul 1. Eine Datenquelle, zwei Geschäftsbereiche." |

### Frage 2b: Wen nehmen wir als Nächstes auf?

> DE: *„Welche fünf Standorte sollten wir als Nächstes in EIS Flex aufnehmen?"*
>
> EN: *"Which five sites should we onboard to EIS Flex next?"*

| | |
|---|---|
| **Erwartetes Ergebnis** | Eine Liste nicht teilnehmender Standorte mit der größten entgangenen Ersparnis, darunter das Wohnquartier München-Riem. |
| **Talking Point (Wow)** | „Aus einer Analyse wird eine Entscheidungsliste: Hier ist der Business Case für den Rollout, Standort für Standort." |

---

## 4. Moment 3: der Plan für morgen (ca. 3 Min., kurzer Abschluss)

> DE: *„Wann sollen die Wärmepumpen im Wärmenetz Hamburg-Altona morgen laufen? Zeige es als Chart zusammen mit dem Strompreis."*
>
> EN: *"When should the Hamburg-Altona heat pumps run tomorrow? Show it as a chart with the power price."*

| | |
|---|---|
| **Erwartetes Ergebnis** | Ein Stundenplan: Die Wärmepumpen laufen in den günstigsten Stunden (typisch nachts und mittags), der Speicher überbrückt die teuren Abendstunden. Dazu die erwartete Ersparnis für den Tag. |
| **Hinweis** | Sind die Preise für morgen noch nicht geladen, sagt der Agent korrekt „Plan für heute". Siehe Checkliste Punkt 3. |
| **Talking Point** | „Snowflake steuert die Anlage nicht. Das bleibt beim Leitsystem vor Ort. Snowflake liefert die Empfehlung: von der Analyse zur konkreten Handlung für morgen." |

---

## 5. Abschluss (ca. 5 Min.)

**Zusammenfassung (DE):**

> „In 15 Minuten haben wir gesehen:
> 1. **Risiken früh erkennen:** Pönale-Risiko in Euro, Wochen vor dem Quartalsende.
> 2. **Schneller reparieren:** Ursache und Anleitung in einer Antwort, aus Daten *und* Dokumenten.
> 3. **Kosten senken:** gleiche Wärme, günstigerer Strom, mit einer klaren Liste der nächsten Standorte.
>
> Alles auf einer Plattform: gesichert und mit klaren Zugriffsrechten. Fragen in Deutsch oder Englisch."

**Vorschlag für die nächsten Schritte:**
1. 1–2 Prioritäten wählen (Garantierisiko, Anlagenzustand oder Flexibilität).
2. Echte Datenquellen benennen (Leitsysteme, ERP/Wartung, Vertragsablage, Marktdaten).
3. Proof of Value auf einer Auswahl echter Standorte.

---

## Mögliche Fragen des CIO, und Antworten

| Frage | Antwort |
|---|---|
| *„Ersetzt das unsere Leitsysteme / unser EMS?"* | Nein. Snowflake ist die Daten-, Analyse- und Empfehlungsebene. Die Echtzeit-Steuerung bleibt vor Ort. |
| *„Wie kommen die Betriebsdaten hinein?"* | Über Standard-Anbindungen (z. B. Streaming, Konnektoren, Dateien aus dem Historian). In der Demo sind sie simuliert. |
| *„Sind die Zahlen echt?"* | Standorte, Anlagen und Verträge sind fiktiv. Die Strompreise sind echte EPEX-Day-Ahead-Preise (Energy-Charts API, Fraunhofer ISE). |
| *„Wer darf was sehen?"* | Zugriffsrechte über Rollen; jeder Geschäftsbereich hat sein eigenes Schema. Der Agent sieht nur, was die Rolle des Nutzers sehen darf. |
| *„Wie sicher sind die KI-Antworten?"* | Der Agent arbeitet auf definierten Kennzahlen (semantische Sicht) und zitiert Dokumente. Er rechnet nicht frei, sondern über nachvollziehbares SQL, das sich anzeigen lässt. |
| *„Kann man statt Regeln auch optimieren?"* | Ja. Die regelbasierte Planung lässt sich zu mathematischer Optimierung (z. B. in Snowpark Python) oder ML-Prognosen erweitern. |
| *„Wie lange dauert so ein Aufbau?"* | Der Demo-Aufbau läuft in ca. 10 Minuten aus einem Notebook. Ein Proof of Value mit echten Daten ist typischerweise eine Frage von Wochen, nicht Monaten. |

---

## Presenter-Tipps

- **Zahlen nicht auswendig lernen:** Sie hängen von den echten Strompreisen ab. Vor der Demo den Story Check im Notebook ansehen.
- **Bei Moment 1 Zeit lassen:** Die Kombination aus Daten und Handbuch in einer Antwort ist der stärkste Moment.
- **EIS Flex ohne Technik erklären:** „gleiche Wärme, günstigerer Strom" und „wie das Handy nachts laden" reichen.
- **Wenn der Agent länger braucht:** erklären, was im Hintergrund passiert (Werkzeugauswahl, SQL, Dokumentensuche).

---

## Anhang A: Hintergrund für Presenter

### A.1 Die Anlagen in einer Energiezentrale

| Anlage | Erzeugt | Energiequelle | Teil von EIS Flex? |
|---|---|---|---|
| **BHKW** (Blockheizkraftwerk) | Strom und Wärme gleichzeitig | Gas | Nein, läuft nach Wärmebedarf |
| **Großwärmepumpe** | Wärme; aus 1 Teil Strom ≈ 3 Teile Wärme (COP ≈ 3) | Strom und Umweltwärme | **Ja** |
| **Gaskessel** | nur Wärme, für Spitzenlast und Reserve | Gas | Nein, läuft nach Wärmebedarf |
| **Wärmespeicher** | speichert Heißwasser, liefert die Wärme später | – | **Ja**, Voraussetzung |

### A.2 Die Regeln von EIS Flex

- **Prinzip:** Die Wärmepumpe erzeugt die Wärme des Tages in den **günstigsten Strompreisstunden** und lädt damit den Speicher. Der Speicher liefert die Wärme in den teuren Stunden. Es ist dieselbe Wärme, nur günstiger erzeugt.
- **Preisbasis:** EPEX Day-Ahead, Gebotszone DE-LU, stündlich. Die Preise für morgen werden gegen 13:00 MEZ veröffentlicht.
- **Feste Regel:** Der Wärmebedarf wird **immer** gedeckt. EIS Flex ändert nur, **wann** die Wärmepumpe läuft, nicht **wie viel** Wärme sie liefert. BHKW und Kessel laufen unverändert.
- **Rollen:** EIS Flex erstellt einen **Fahrplan als Empfehlung** für den nächsten Tag. Die Anlagensteuerung vor Ort (SCADA/EMS) steuert in Echtzeit und hat das letzte Wort.

### A.3 Kennzahlen

| Kennzahl | Definition |
|---|---|
| **Flex-Marge** | Stromkosten der Wärmepumpe im Normalbetrieb minus Stromkosten mit EIS Flex, bei gleicher Wärmemenge |
| **Erzielte Marge** | Flex-Marge an teilnehmenden Standorten, also tatsächlich gespart |
| **Entgangene Marge** | Mögliche Flex-Marge an Standorten ohne EIS Flex, also ungenutztes Potenzial |
| **EIS-Anteil / Kundenanteil** | Aufteilung der Marge laut § 4 „EIS Flex" im Kundenvertrag, typischerweise 60/40 oder 70/30 |
| **COP** | Wärme-zu-Strom-Verhältnis der Wärmepumpe. In den Daten steht COP × 100, z. B. 320 = COP 3,2 |
| **Ladestand (SOC)** | Füllstand des Speichers in % |

**Vereinfachtes Beispiel (fiktive Zahlen):** Eine Wärmepumpe braucht für die Wärme eines Tages eine feste Strommenge. Läuft sie verteilt über den Tag, zahlt sie den Durchschnittspreis aller Stunden. Mit EIS Flex zahlt sie nur den Preis der günstigsten Stunden. Die Differenz ist die Flex-Marge, die laut Vertrag zwischen EIS und Kunde aufgeteilt wird.

> **Was die Demo bewusst vereinfacht:** Der Speicher wird pro Tag mit höchstens 85 % seiner Kapazität genutzt. Weitere Regeln aus der Betriebsrichtlinie (`docs/om_manual_thermal_storage.md`) werden **nicht** simuliert: Nutzbarkeit nur zwischen 10 und 95 % Füllstand, höchstens 25 % Laden pro Stunde, und an Kliniken ein Mindestfüllstand von 25 % zwischen 06:00 und 22:00 Uhr. Darauf hinweisen, falls nachgefragt wird.

### A.4 Wann ist ein Standort geeignet?

**Ja, wenn**
- mindestens eine Großwärmepumpe vorhanden ist,
- der Speicher **mindestens 3 Stunden** des durchschnittlichen Wärmebedarfs abdeckt,
- keine Versorgungsauflage die Speichernutzung einschränkt,
- idealerweise der Speicher heute **kaum genutzt** wird.

**Eher nein, wenn**
- keine Wärmepumpe vorhanden ist (in den Demodaten haben einige nicht teilnehmende Standorte keine Wärmepumpe und damit kein Potenzial) oder der Speicher zu klein ist,
- **kritische Versorgung** besteht (Kliniken, Pflegeheime) und der Speicher deshalb einen Mindestfüllstand halten muss,
- die Ersparnis klein ist, weil der Standort klein ist oder der Strompreis über den Tag kaum schwankt,
- die Anlagen oft gestört sind. Mehr Starts bedeuten mehr Verschleiß und damit ein Risiko für die garantierte Verfügbarkeit. Das Herstellerhandbuch der Wärmepumpe begrenzt die Starts auf höchstens 6 pro Stunde und empfiehlt Laufblöcke von mindestens 1 Stunde (`docs/om_manual_heatpump_thermaflux_hp2000.md`).

### A.5 Kosten

- **Wärmepumpe und Speicher vorhanden:** keine Anschaffung, nur Einführung, Vertragsanpassung und Überwachung.
- **Hardware fehlt:** Dann ist es ein Investitionsprojekt, und die Flex-Marge ist nur ein Teil des Nutzens.

### A.6 Offene Punkte für die nächsten Kandidaten (Folgeschritt nach der Demo)

Bevor ein Kandidat aufgenommen wird, sind zu klären:
- tatsächliche Speichergröße und heutige Speichernutzung,
- Zustand und Störhistorie der Anlagen,
- Margenaufteilung und Flex-Klausel im Vertrag,
- Versorgungsauflagen am Standort.

---

## Anhang B: Beispiel-Ergebnisse eines Laufs (Momentaufnahme)

> **Nur als Orientierung.** Die Zahlen stammen aus dem Notebook-Lauf vom **06.11.2026** (Zeitraum 07.10.–05.11.2026) und ändern sich mit jedem Lauf, weil sie auf echten Börsenstrompreisen beruhen. Für die Demo immer den aktuellen **Story Check** (Notebook, Abschnitt 9) verwenden.

| | Standorte | Marge (30 Tage) | EIS-Anteil |
|---|---|---|---|
| **Erzielt** (EIS Flex) | 72 | ≈ 527.000 EUR | ≈ 338.000 EUR |
| **Entgangen** (ohne EIS Flex) | 48, davon 13 ohne Wärmepumpe | ≈ 127.000 EUR | ≈ 89.000 EUR |

- **Spitzenreiter:** Wärmenetz Hamburg-Altona mit ≈ 38.600 EUR in 30 Tagen. Die Wärmepumpen zahlten im Schnitt ≈ 141 statt ≈ 181 EUR/MWh.
- **Nächste 5 Kandidaten:** Bremen S059, München S042, Bremen S021, München-Riem, Mannheim S063. Zusammen ≈ 44.000 EUR in 30 Tagen (≈ 31.000 EUR EIS-Anteil). Alle haben 2 Wärmepumpen und einen Speicher, es ist keine neue Hardware nötig.
- **Pönale-Risiko:** Klinikum Hamburg-Nord ≈ 135.000 EUR (Verfügbarkeit ≈ 94 % statt 97 %), Campus Kiel ≈ 20.000 EUR, Chemiepark Leuna unter Beobachtung.
