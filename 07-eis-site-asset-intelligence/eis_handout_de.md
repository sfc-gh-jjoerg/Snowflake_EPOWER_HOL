# Energieanlagen intelligent betreiben

*Hand-out für Kollegen · EPOWER Infrastructure Solutions*

**Business Case & Demo-Leitfaden.** Risiken früher erkennen, schneller reparieren, Energiekosten senken. Lesezeit ca. 15 Minuten; danach kannst du den Business Case erklären und die Demo in unabhängigen Modulen von je höchstens 5 Minuten zeigen.

## Inhalt

**Teil A · Verstehen**
1. [Auf einen Blick](#1-auf-einen-blick)
2. [Das Unternehmen und das Problem](#2-das-unternehmen-und-das-problem)
3. [Die Anlagen in einer Energiezentrale](#3-die-anlagen-in-einer-energiezentrale)
4. [Konzept 1: Garantien und Pönalen](#4-konzept-1-garantien-und-pönalen)
5. [Konzept 2: EIS Flex](#5-konzept-2-eis-flex-gleiche-wärme-günstigerer-strom)
6. [Die Rolle von Snowflake](#6-die-rolle-von-snowflake)

**Teil B · Zeigen**
7. [Modulübersicht](#7-modulübersicht)
8. [Vorbereitung](#8-vorbereitung)
   - [M0 Business Case Pitch](#m0--business-case-pitch)
   - [M1 Pönale-Risiko erkennen](#m1--pönale-risiko-erkennen)
   - [M2 Ursache und Reparatur](#m2--ursache-und-reparatur)
   - [M3 EIS Flex: Wert und Rollout](#m3--eis-flex-wert-und-rollout)
   - [M4 Fahrplan für morgen](#m4--fahrplan-für-morgen)
9. [Vorschläge für Kombinationen](#9-vorschläge-für-kombinationen)
10. [Abschluss und nächste Schritte](#10-abschluss-und-nächste-schritte)

**Teil C · Nachschlagen**

11. [Häufige Fragen](#11-häufige-fragen)
12. [Glossar](#12-glossar)

---

# Teil A · Verstehen

## 1. Auf einen Blick

Ein Energiedienstleister betreibt Anlagen bei Kunden und **garantiert**, dass sie laufen. Die Daten dazu liegen verstreut, Probleme fallen spät auf, und günstige Strompreise bleiben ungenutzt. Eine **Daten- und KI-Plattform** bringt Betriebsdaten, Verträge, Handbücher und Strompreise zusammen. Ein Agent beantwortet Fragen in normaler Sprache, mit Euro-Betrag und konkreter Empfehlung.

| Pönalen vermeiden | Schneller reparieren | Energiekosten senken |
|---|---|---|
| Garantierisiken Wochen vor dem Quartalsende erkennen, in Euro beziffert. | Ursache aus den Betriebsdaten und Anleitung aus dem Handbuch, in einer Antwort. | Wärmepumpen in den günstigsten Stunden laufen lassen: gleiche Wärme, weniger Stromkosten. |

> **Kernbotschaft:** Betriebsdaten, Verträge und Handbücher auf einer Plattform. Ein Agent, der in Euro antwortet und konkrete Maßnahmen empfiehlt.

## 2. Das Unternehmen und das Problem

**EPOWER Infrastructure Solutions (EIS)** ist ein fiktiver B2B-Energiedienstleister in Deutschland. EIS plant, finanziert und betreibt Energiezentralen bei Kunden, z. B. in Krankenhäusern, Industrieparks, Wohnquartieren, auf Campus-Geländen und in Fernwärmenetzen. Die Verträge laufen 10–20 Jahre. EIS garantiert darin Verfügbarkeit und Effizienz der Anlagen; wird eine Garantie verfehlt, fällt eine **Vertragsstrafe (Pönale)** an.

| Daten in Silos | Späte Erkennung | Ungenutztes Potenzial |
|---|---|---|
| Betriebsdaten in vielen Leitsystemen, Wartung im ERP, Verträge und Handbücher als PDF, Strompreise an der Börse. | Ob eine Garantie verfehlt wird, zeigt sich oft erst im Quartalsbericht. | Strompreise schwanken stündlich. Viele Wärmepumpen laufen trotzdem unabhängig vom Preis. |

## 3. Die Anlagen in einer Energiezentrale

| Anlage | Funktion | EIS Flex |
|---|---|---|
| **BHKW (Blockheizkraftwerk)** | Erzeugt mit Gas gleichzeitig Strom und Wärme. Läuft nach Wärmebedarf. | nicht Teil von EIS Flex |
| **Großwärmepumpe** | Macht aus 1 Teil Strom (plus Umweltwärme) rund 3 Teile Wärme (COP ≈ 3). | **Hebel von EIS Flex** |
| **Gaskessel** | Nur Wärme, für Spitzenlast und als Reserve. | nicht Teil von EIS Flex |
| **Wärmespeicher** | Großer Heißwassertank: speichert Wärme und gibt sie später ab. | **Voraussetzung für EIS Flex** |

**Normalbetrieb:** Jede Stunde deckt zuerst die Wärmepumpe den Bedarf (Grundlast), dann das BHKW, zuletzt der Kessel.

## 4. Konzept 1: Garantien und Pönalen

Verträge garantieren die **Verfügbarkeit** (Anteil der Zeit ohne Störung) und den **Wirkungsgrad** der Anlagen, gemessen pro Quartal. Jeder verfehlte oder angefangene Prozentpunkt kostet eine im Vertrag festgelegte Pönale.

| Begriff | Bedeutung in der Demo |
|---|---|
| Messfenster | Die **letzten 30 Tage** als Frühindikator: „Wenn es so weitergeht, ist das die Pönale für das Quartal." |
| Status | **AT_RISK** = unter der Garantie · **WATCH** = weniger als 1 Punkt Abstand · **OK** |
| Vertragsbasis | Je Anlage (jede Einheit muss die Garantie erfüllen), im Durchschnitt aller Einheiten oder auf Ebene der Wärmeversorgung |
| Health Score | 0–100 je Anlage aus Verfügbarkeit, anhaltendem Wirkungsgradverlust, Störungen und Warnungen (CRITICAL / WARNING / GOOD) |

### Vorher / Nachher: das BHKW im Klinikum Hamburg-Nord

**Vorher: manuell und reaktiv**
1. Die Anlage meldet einen Fehler, der Techniker quittiert ihn und startet neu.
2. Niemand verbindet die wiederholten Ausfälle mit dem sinkenden Wirkungsgrad.
3. Die Garantie-Klausel steht im Vertrags-PDF, getrennt von den Betriebsdaten.
4. Am Quartalsende zeigt der Bericht: Garantie verfehlt.

*Ergebnis: eine hohe Pönale, erst im Nachhinein erkannt.*

**Nachher: mit dem EIS-Agenten**
1. Frage in normaler Sprache: *„Welche Verträge sind gefährdet?"*
2. Der Agent nennt das Klinikum, beziffert das Risiko in Euro und zeigt die Ursache: verschmutzter Abgaswärmetauscher (Fehler F-217).
3. Er liefert Reinigungsanleitung und Ersatzteil aus dem Herstellerhandbuch.
4. Die Wartung wird geplant, bevor die Garantie verfehlt wird.

*Ergebnis: Risiko Wochen vorher erkannt, Pönale vermeidbar.*

## 5. Konzept 2: EIS Flex, gleiche Wärme, günstigerer Strom

Der Strompreis an der Börse ändert sich jede Stunde. Mit einem Wärmespeicher muss die Wärmepumpe nicht genau dann laufen, wenn Wärme gebraucht wird. **Sie erzeugt die Wärme des Tages in den günstigsten Stunden und speichert sie**, so wie man das Handy nachts lädt.

*Beispielverlauf (illustrativ): Strompreis pro Stunde 0–23 Uhr; ■ = mit EIS Flex läuft die Wärmepumpe*

```
Stunde : 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
Preis  :  ▅  ▅  ▄  ▄  ▄  ▄  ▆  █  ▇  ▆  ▄  ▃  ▃  ▃  ▃  ▄  ▅  █  █  █  ▇  ▆  ▆  ▅
WP an  :        ■  ■  ■  ■              ■  ■  ■  ■  ■  ■
```

- **Die Regel in 4 Schritten:** 1. Wärmemenge des Tages bestimmen · 2. Stunden nach Börsenpreis sortieren · 3. Wärmepumpe in den günstigsten Stunden voll laufen lassen · 4. Der Speicher gleicht aus: laden, wenn mehr erzeugt wird als gebraucht, entladen, wenn weniger.
- **Feste Regel:** Der Wärmebedarf wird **immer** gedeckt. EIS Flex ändert nur, *wann* die Wärmepumpe läuft, nicht *wie viel* Wärme geliefert wird. BHKW und Kessel laufen unverändert.
- **Empfehlung, keine Steuerung:** EIS Flex erstellt einen Fahrplan für den nächsten Tag. Die Anlagensteuerung vor Ort (SCADA/EMS) steuert in Echtzeit und hat das letzte Wort.

### Kennzahlen

| Kennzahl | Bedeutung |
|---|---|
| **Flex-Marge** | Stromkosten der Wärmepumpe im Normalbetrieb minus Stromkosten mit EIS Flex, bei gleicher Wärmemenge |
| **Erzielte Marge** | Flex-Marge an teilnehmenden Standorten: tatsächlich gespart |
| **Entgangene Marge** | Mögliche Flex-Marge an Standorten ohne EIS Flex: der Business Case für den Rollout |
| **EIS- / Kundenanteil** | Aufteilung der Marge laut EIS-Flex-Klausel im Vertrag, typischerweise 60/40 oder 70/30 |

**Wann lohnt sich EIS Flex?**
- Mindestens eine Großwärmepumpe am Standort.
- Speicher für mindestens rund 3 Stunden Wärmebedarf, der heute kaum genutzt wird.
- Keine Versorgungsauflage, die die Speichernutzung einschränkt.

*Sind Wärmepumpe und Speicher vorhanden, ist keine neue Hardware nötig. Nur die Fahrweise ändert sich.*

**Eher nicht geeignet, wenn …**
- keine Wärmepumpe oder nur ein sehr kleiner Speicher vorhanden ist,
- der Strompreis über den Tag kaum schwankt oder der Standort sehr klein ist,
- kritische Versorgung (z. B. Klinik) einen Mindestfüllstand verlangt,
- die Anlagen oft gestört sind (zusätzliche Starts erhöhen den Verschleiß).

*Fehlt die Hardware, wird daraus ein Investitionsprojekt.*

## 6. Die Rolle von Snowflake

1. **Zusammenführen:** Betriebsdaten, Verträge, Handbücher und Strompreise auf einer gesicherten Plattform, mit klaren Zugriffsrechten.
2. **Verstehen:** KI liest Verträge und Handbücher und verknüpft sie mit den Anlagendaten. Fragen auf Deutsch oder Englisch.
3. **Handeln:** Konkrete Empfehlungen: welche Wartung, welches Ersatzteil, wann die Wärmepumpe laufen soll.

> Snowflake ist die **Daten-, Analyse- und Empfehlungsebene**. Die Echtzeit-Steuerung der Anlagen bleibt bei den Leitsystemen vor Ort. Snowflake ersetzt sie nicht.

<details>
<summary>Was die Demo bewusst vereinfacht</summary>

- Standorte, Anlagen, Verträge und Störungen sind **fiktiv** und mit festen Mustern erzeugt, damit die Story bei jedem Lauf stimmt. Die **Strompreise sind echt** (EPEX Day-Ahead, DE-LU, Energy-Charts API / Fraunhofer ISE).
- Der Speicher wird pro Tag mit höchstens 85 % seiner Kapazität genutzt. Weitere Regeln der Betriebsrichtlinie (10–95 % Füllstand, max. 25 % Laden pro Stunde, Mindestfüllstand in Kliniken) werden nicht simuliert.
- Der Fahrplan ist regelbasiert. Er ließe sich zu mathematischer Optimierung oder ML-Prognosen erweitern.

</details>

---

# Teil B · Zeigen

## 7. Modulübersicht

Jedes Modul steht für sich: Es hat einen eigenen Einstiegssatz und dauert höchstens 5 Minuten. Die Module lassen sich frei kombinieren.

| Modul | Dauer | Kernaussage | System nötig? |
|---|---|---|---|
| M0 Business Case Pitch | 3 Min. | Warum das Thema relevant ist | Nein |
| M1 Pönale-Risiko erkennen | 4 Min. | Risiko in Euro, Wochen vor dem Quartalsende | Ja |
| M2 Ursache und Reparatur | 5 Min. | Daten + Handbuch in einer Antwort | Ja |
| M3 EIS Flex: Wert und Rollout | 5 Min. | Gleiche Wärme, günstigerer Strom, nächste Standorte | Ja |
| M4 Fahrplan für morgen | 3 Min. | Von echten Börsenpreisen zum Stundenplan | Ja |

## 8. Vorbereitung

**Erledigt der Demo-Owner (am Demo-Tag)**
1. Die Demo-Umgebung ist aufgesetzt und läuft fehlerfrei.
2. Die aktuellen **Erwartungswerte** (Story Check) werden dem Presenter mitgegeben, z. B. Euro-Risiko je Vertrag, erzielte und entgangene Ersparnis, Top-Kandidaten. Die Zahlen ändern sich mit den echten Strompreisen.
3. Für Modul M4: Die Strompreise für morgen sind geladen. Das passiert automatisch gegen 17:00 MEZ; nach 13:00 MEZ kann der Demo-Owner sie auch früher laden.

**Vor dem Termin (Presenter, ca. 5 Min.)**
1. Snowflake CoWork öffnen und den Agenten **EIS Operations** auswählen.
2. Eine Testfrage stellen, damit der Agent „warm" ist, z. B. *„Wie viele Standorte nehmen an EIS Flex teil?"*
3. Die Erwartungswerte vom Demo-Owner bereitlegen und die Fragen der geplanten Module griffbereit haben.

---

### M0 · Business Case Pitch
*3 Min. · ohne System*

**Ziel:** in drei Minuten klarmachen, wo Geld verloren geht und was möglich ist. Eignet sich als Einstieg vor jedem anderen Modul.

> **Talk Track:** „Stellen Sie sich ein Unternehmen vor, das Energieanlagen bei seinen Kunden baut und betreibt: Blockheizkraftwerke im Krankenhaus, Wärmepumpen im Fernwärmenetz, Speicher im Industriepark. Die Verträge laufen 15, 20 Jahre, und das Unternehmen **garantiert**, dass die Anlagen laufen. Wird die Garantie verfehlt, zahlt es eine Vertragsstrafe. Die nötigen Informationen liegen verstreut: Betriebsdaten in den Leitsystemen, Wartung im ERP, Garantien im Vertrags-PDF, Anleitungen im Herstellerhandbuch, Strompreise an der Börse. Probleme fallen oft erst im Quartalsbericht auf, und Wärmepumpen laufen unabhängig davon, ob Strom gerade teuer oder billig ist. Heute zeige ich, wie eine Daten- und KI-Plattform drei Fragen beantwortet: **Wo verlieren wir Geld? Warum? Und wo können wir sofort sparen?**"

- **Hilfsmittel:** Abschnitte 1–3 dieses Hand-outs oder der One-Pager

---

### M1 · Pönale-Risiko erkennen
*4 Min.*

**Ziel:** zeigen, dass Garantierisiken in Euro sichtbar werden, bevor das Quartal vorbei ist.

**Einstieg:** „EIS garantiert seinen Kunden Verfügbarkeit, und jeder verfehlte Prozentpunkt kostet Geld. Fragen wir, wo wir gerade gefährdet sind."

> **DE:** Welche Verträge laufen Gefahr, in diesem Quartal ihre Garantie zu verfehlen, und wie hoch ist unser Pönale-Risiko?
>
> **EN:** Which contracts are at risk of missing their guarantee this quarter, and what is our € exposure?

- **Im Hintergrund:** Der Agent nutzt die semantische Sicht (Text-zu-SQL) und verbindet Betriebsdaten mit den Garantien aus den Verträgen.
- **Erwartetes Ergebnis:** Klinikum Hamburg-Nord mit dem größten Risiko (BHKW-2 unter der garantierten Verfügbarkeit), ein kleinerer Fall am Campus Kiel, Chemiepark Leuna unter Beobachtung. Jeweils mit Euro-Betrag.
- **Wow-Satz:** **„Eine Frage in normaler Sprache, die Antwort in Euro, und zwar jetzt, nicht am Quartalsende."**
- **Optionale Nachfrage:** *„Zeige das Risiko je Vertrag als Balkendiagramm."*
- **Fallback:** Kommt keine Euro-Zahl: nachfragen *„Wie hoch ist die Pönale je Vertrag in Euro?"*

---

### M2 · Ursache und Reparatur
*5 Min.*

**Ziel:** der stärkste Moment. Messdaten, Arbeitsauftrag und Herstellerhandbuch fließen in eine Antwort.

**Einstieg** (wenn ohne M1 gezeigt): „Im Klinikum Hamburg-Nord ist ein Blockheizkraftwerk mehrfach ausgefallen, und die Garantie ist gefährdet. Fragen wir nach der Ursache."

> **DE:** Warum liegt das BHKW-2 im Klinikum Hamburg-Nord unter Plan, und was soll der Techniker tun?
>
> **EN:** Why is Klinikum Hamburg-Nord CHP-2 below target, and what should the technician do?

- **Im Hintergrund:** Zwei Werkzeuge nacheinander: die Datenanalyse findet sinkenden Wirkungsgrad, wiederholte Störungen F-217 und einen offenen Arbeitsauftrag. Die Dokumentensuche holt Reinigungsanleitung und Ersatzteil aus dem Herstellerhandbuch.
- **Erwartetes Ergebnis:** Ursache: verschmutzter Abgaswärmetauscher. Maßnahme: Reinigung nach Handbuch, Ersatzteil-Kit bestellen. Bisher wurde nur neu gestartet, ein Ersatzteil wurde nicht bestellt.
- **Wow-Satz:** **„Daten aus der Anlage, Klausel aus dem Vertrag, Anleitung aus dem Handbuch, in einer Antwort. Der Techniker weiß, was zu tun ist, bevor die Pönale fällig wird."**
- **Optionale Nachfrage:** *„Zeige den Wirkungsgrad-Verlauf von BHKW-2 als Chart."* Der Verlauf fällt deutlich ab.
- **Fallback:** Fehlt die Anleitung: nachfragen *„Was sagt das Herstellerhandbuch zu Fehler F-217?"*

---

### M3 · EIS Flex: Wert und Rollout
*5 Min.*

**Ziel:** zeigen, dass dieselbe Wärme günstiger erzeugt werden kann, und welche Standorte als Nächstes dran sind.

**Einstieg:** „Strom kostet an der Börse jede Stunde etwas anderes. Mit einem Wärmespeicher kann die Wärmepumpe die Wärme des Tages in den günstigsten Stunden erzeugen, wie beim Handy, das man nachts lädt. Gleiche Wärme, niedrigere Stromkosten, ohne neue Anlagen."

> **DE:** Wie viel hat EIS Flex in den letzten 30 Tagen eingespart, und was entgeht uns bei den Standorten, die noch nicht teilnehmen?
>
> **EN:** How much did EIS Flex save in the last 30 days, and what are we missing on sites that are not enrolled?

> **DE:** Welche fünf Standorte sollten wir als Nächstes in EIS Flex aufnehmen?
>
> **EN:** Which five sites should we onboard to EIS Flex next?

- **Im Hintergrund:** Die Datenanalyse vergleicht die Stromkosten der Wärmepumpen im Normalbetrieb und mit EIS Flex, auf Basis echter Börsenpreise.
- **Erwartetes Ergebnis:** Eine erzielte Ersparnis an den Flex-Standorten (Spitzenreiter: Wärmenetz Hamburg-Altona), eine entgangene Ersparnis an den übrigen Standorten und eine Liste der besten Kandidaten, darunter das Wohnquartier München-Riem.
- **Wow-Satz:** **„Aus einer Analyse wird eine Entscheidungsliste: der Business Case für den Rollout, Standort für Standort."**
- **Talking Point:** „Das sind echte Börsenpreise, täglich automatisch geladen. Dieselbe Datenquelle nutzt bereits ein anderer Geschäftsbereich."
- **Fallback:** Wird nur ein Teil beantwortet: die zweite Frage separat stellen.

---

### M4 · Fahrplan für morgen
*3 Min.*

**Ziel:** von der Analyse zur konkreten Handlung für den nächsten Tag.

**Einstieg** (wenn ohne M3 gezeigt): „Die Wärmepumpen im Fernwärmenetz Hamburg-Altona sollen in den günstigsten Stunden laufen. Lassen wir uns den Plan für morgen erstellen."

> **DE:** Wann sollen die Wärmepumpen im Wärmenetz Hamburg-Altona morgen laufen? Zeige es als Chart zusammen mit dem Strompreis.
>
> **EN:** When should the Hamburg-Altona heat pumps run tomorrow? Show it as a chart with the power price.

- **Im Hintergrund:** Eine Sicht verbindet die neuesten Börsenpreise mit dem erwarteten Wärmebedarf und erstellt daraus einen Stundenplan.
- **Erwartetes Ergebnis:** Die Wärmepumpen laufen in den günstigsten Stunden (typisch nachts und mittags), der Speicher überbrückt die teuren Abendstunden. Dazu die erwartete Ersparnis des Tages.
- **Wow-Satz:** **„Snowflake steuert die Anlage nicht, das bleibt beim Leitsystem. Aber es liefert die Empfehlung für morgen, auf Basis echter Marktpreise."**
- **Hinweis:** Sind die Preise für morgen noch nicht geladen, sagt der Agent korrekt „Plan für heute". Siehe Vorbereitung (Demo-Owner, Punkt 3).

---

## 9. Vorschläge für Kombinationen

| Verfügbare Zeit | Module | Geeignet für |
|---|---|---|
| 5 Min. | M0 + M1 · oder nur M3 | Elevator Pitch, Messestand |
| 10 Min. | M1 + M2 | Betrieb und Service, „Daten + Dokumente" |
| 15 Min. | M0 + M1 + M2 + M3 | Management-Termin |
| 20 Min. | M0 – M4 + Abschluss | Vollständige Story |

## 10. Abschluss und nächste Schritte

> **Talk Track:** „Wir haben gesehen: Risiken früh erkennen, in Euro. Schneller reparieren, mit Ursache und Anleitung in einer Antwort. Kosten senken, mit gleicher Wärme und günstigerem Strom. Alles auf einer gesicherten Plattform mit klaren Zugriffsrechten, Fragen auf Deutsch oder Englisch."

1. 1–2 Prioritäten wählen: Garantierisiko, Anlagenzustand oder Flexibilität.
2. Echte Datenquellen benennen: Leitsysteme, ERP/Wartung, Vertragsablage, Marktdaten.
3. Proof of Value auf einer Auswahl echter Standorte.

---

# Teil C · Nachschlagen

## 11. Häufige Fragen

| Frage | Antwort |
|---|---|
| Ersetzt das unsere Leitsysteme / unser EMS? | Nein. Snowflake ist die Daten-, Analyse- und Empfehlungsebene. Die Echtzeit-Steuerung bleibt vor Ort. |
| Wie kommen die Betriebsdaten hinein? | Über Standard-Anbindungen (z. B. Streaming, Konnektoren, Dateien aus dem Historian). In der Demo sind sie simuliert. |
| Sind die Zahlen echt? | Standorte, Anlagen und Verträge sind fiktiv. Die Strompreise sind echte EPEX-Day-Ahead-Preise. |
| Wer darf was sehen? | Zugriffsrechte über Rollen; jeder Geschäftsbereich hat sein eigenes Schema. Der Agent sieht nur, was die Rolle des Nutzers sehen darf. |
| Wie verlässlich sind die KI-Antworten? | Der Agent arbeitet auf definierten Kennzahlen (semantische Sicht) und zitiert Dokumente. Er rechnet über nachvollziehbares SQL, das sich anzeigen lässt. |
| Geht das auch mit Optimierung statt Regeln? | Ja. Die regelbasierte Planung lässt sich zu mathematischer Optimierung (z. B. in Snowpark Python) oder ML-Prognosen erweitern. |
| Warum nur die Wärmepumpe? | Sie ist der einfachste und wirkungsvollste Hebel: Ihr Strombedarf lässt sich mit einem Speicher zeitlich verschieben, ohne dass sich die gelieferte Wärme ändert. |

## 12. Glossar

| Begriff | Erklärung |
|---|---|
| **BHKW** | Blockheizkraftwerk; erzeugt mit Gas gleichzeitig Strom und Wärme (engl. CHP) |
| **COP** | Leistungszahl der Wärmepumpe: Wärme geteilt durch Strom (≈ 3). In den Daten als COP × 100 (320 = 3,2) |
| **Day-Ahead / EPEX** | Börsenhandel für Strom des Folgetags; Preise je Stunde für die Zone DE-LU, veröffentlicht gegen 13:00 MEZ |
| **Pönale** | Vertragsstrafe bei verfehlter Garantie |
| **SOC** | Ladestand (State of Charge) des Wärmespeichers in % |
| **SCADA / EMS** | Leit- und Energiemanagementsysteme, die die Anlagen in Echtzeit steuern |
| **Semantische Sicht** | Geschäftsvokabular in Snowflake, mit dem der Agent Fragen in korrektes SQL übersetzt |
| **Cortex Search** | Suche über Dokumente (Verträge, Handbücher), damit der Agent Inhalte zitieren kann |
| **Cortex Agent / CoWork** | Der KI-Agent „EIS Operations" und die Chat-Oberfläche, in der er genutzt wird |

---

*Fiktive Daten („EPOWER Infrastructure Solutions": Standorte, Anlagen und Verträge sind erfunden) mit echten EPEX-Day-Ahead-Strompreisen (Energy-Charts API, Fraunhofer ISE). Konkrete Euro-Beträge berechnet die Demo live; dieses Hand-out enthält deshalb bewusst keine festen Zahlen.*
