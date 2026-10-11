# Scoring-Spezifikation

Grundlage für die Matching-Komponente. Folgt dem Proposal, Kap. 4.5 (Scoring-Algorithmus). Feldnamen, Einheiten und Stufen: `anforderungskatalog.md`.

## Eigenschaften

- Weighted Sum Model, zweistufig: harter Ausschlussfilter, danach gewichtete Punktbewertung.
- Reine Funktion: kein I/O, kein LLM, keine Zufälligkeit.
- Gewichte und Kategorie-Defaults liegen in der Konfiguration, nicht in der Logik.
- Die Ausgabe enthält die Einzelbeiträge je Kriterium. Sie ist damit der Nachweis für die Nachvollziehbarkeit.
- Keine szenariospezifischen Regeln, damit die Kontrollszenarien ohne Anpassung laufen.

## Abweichungen vom Proposal

| Ergänzung | Grund |
|---|---|
| K.O.-Kriterium `verwaltung_min` | Ohne dieses Kriterium gewinnt in Szenario 1 ein günstiger unverwalteter VPS. Der Erwartungswert des Proposals (Shared-Hosting für einen Nutzer ohne Admin-Know-how) wäre nicht erreichbar. |
| K.O.-Kriterium `skalierung_min` | Ohne dieses Kriterium gewinnt in Szenario 2 ein günstiger Dedicated-Server mit viel RAM, obwohl das Profil Auto-Scaling verlangt. Der Erwartungswert des Proposals (skalierbares VPS/Cloud-Angebot) wäre nicht erreichbar. |
| Kategorie-Defaults in Stufe 0 | Shared-Pakete nennen Docker fast nie. Ohne Default greift der Docker-K.O. nicht und die Szenarien 2 und 3 schliessen Shared nicht aus, wie das Proposal es erwartet. |
| Preisregeln (Setup-Gebühr, Vergleichsbasis) | Das Proposal vergleicht „Preis CHF/Monat", definiert die Aufbereitung aber nicht. Ohne feste Regel sind die Angebote nicht vergleichbar. |

Alles Übrige entspricht dem Proposal.

## Eingabe

| Teil | Inhalt |
|---|---|
| `profil` | technisches Profil gemäss Katalog. Felder dürfen `null` sein (Variante B) |
| `angebote[]` | Angebotsfelder gemäss Katalog |
| `config` | `gewichte`, `kategorie_defaults` (`scoring/config.json`) |

## Stufe 0 — Aufbereitung

**Einheiten:** GB dezimal (1 GB = 1000 MB), Bandbreite in Mbit/s, Preis in CHF mit 2 Nachkommastellen. Die Extraktion liefert die Werte bereits in diesen Einheiten, die Engine rechnet sie nicht um.

**Preis** → effektiver Monatspreis:

```
preis_chf_monat = (setup_gebuehr + 12 × monatspreis_regulaer) / 12   [in CHF]
```

- Grundlage ist der veröffentlichte reguläre Monatspreis, keine Aktionspreise.
- Der Preis wird so übernommen, wie der Anbieter ihn ausweist. Es findet keine Umrechnung zwischen brutto und netto statt.
- Fremdwährungen werden 1:1 übernommen, ein Preis von 10 EUR gilt als 10 CHF. Es gibt keine Wechselkurse und keinen Kursstichtag.
- Ein fehlender Preis führt immer zum Ausschluss (Grund `preis_fehlt`), auch ohne Budget im Profil.
- Die Extraktion liefert den Monatspreis. Jahrespreise rechnet sie vorher um (`abrechnungsintervall`), die Engine kennt nur Monatspreise.
- „Unlimitiert" (Speicher, Bandbreite) liefert die Extraktion als `null`. Die Engine behandelt es als fehlenden Wert.
- Die Vertragslaufzeit wird extrahiert und in der Ausgabe mitgeführt, beeinflusst den Preis aber nicht. Gerechnet wird immer mit dem regulären Monatspreis, unabhängig von der Mindestlaufzeit.

**Kategorie-Defaults** gelten nur für Felder, die nach der Extraktion `null` sind:

| Kategorie | `docker_support` | `verwaltung` | `ressourcentyp` |
|---|---|---|---|
| `shared`, `managed` | `false` | `managed` | `shared` |
| `vps`, `cloud` | `true` | `selbst` | `vserver` |
| `dedicated` | `true` | `selbst` | `dediziert` |

Fehlt die Kategorie oder ist sie kein gültiger Wert, wird das Angebot ausgeschlossen (Grund `kategorie_fehlend`). Ohne Kategorie greifen weder die Defaults noch der Kategorie-Evaluator, und das Angebot käme an K.O.-Kriterien vorbei, die für seine Kategorie gelten.

**Nachvollziehbarkeit:** Jedes Angebot führt zwei Listen. `abgeleitete_felder` enthält die per Default gesetzten Felder. `fehlende_felder` enthält die Felder aus K.O.-Filter und Bewertung, die auch nach den Defaults `null` sind. So ist sichtbar, welche Werte nicht aus der Extraktion stammen.

## Stufe 1 — K.O.-Filter

Ein Angebot wird ausgeschlossen, wenn es eine Mindestanforderung verletzt.

| Kriterium | Ausschluss, wenn | Angebotswert `null` |
|---|---|---|
| Preis | `preis > budget_chf_monat_max` | Ausschluss |
| RAM | `ram_gb < ram_gb_min` | durchlassen |
| Speicherplatz | `storage_gb < storage_gb_min` | durchlassen |
| Docker | `docker_erforderlich` und nicht `docker_support` | durchlassen |
| Ressourcentyp | Rang Angebot < Rang Profil (`egal` = kein Rang) | durchlassen |
| Verwaltung | Profil `managed` und Angebot `selbst` | durchlassen |
| Skalierung | `skalierung < skalierung_min` | durchlassen |

Ein fehlender Angebotswert führt nur beim Preis zum Ausschluss. Sonst bleibt das Angebot im Rennen und das Feld steht in `fehlende_felder`. Docker, Ressourcentyp und Verwaltung sind nach Stufe 0 nie `null`, weil jede gültige Kategorie einen Default liefert. Fehlen kann der Wert deshalb nur bei RAM, Speicherplatz und Skalierung. Ein `null` im Profil heisst „keine Anforderung" (Variante B) und wird nicht geprüft.

Ausschlüsse werden protokolliert:

```json
{ "anbieter": "…", "produkt": "…", "gruende": [ { "kriterium": "ram_gb", "profil": 16, "angebot": 8 } ] }
```

## Stufe 2 — Bewertung

**Gewichte** (`config.gewichte`, Summe 1.0, identisch mit dem Proposal):

| Kriterium | Typ | Gewicht | Richtung |
|---|---|---|---|
| `preis_chf_monat` | Kosten | 0.30 | tiefer = besser |
| `cpu_vcores` | Nutzen | 0.15 | höher = besser |
| `ram_gb` | Nutzen | 0.15 | höher = besser |
| `bandbreite_mbit` | Nutzen | 0.10 | höher = besser |
| `skalierung` | Nutzen | 0.15 | höher = besser |
| `backup` | Nutzen | 0.10 | höher = besser |
| `support` | Nutzen | 0.05 | höher = besser |

Speicherplatz, Docker, Verwaltung und Ressourcentyp wirken nur als K.O. und gehen nicht ins Scoring ein. Preis, RAM und Skalierung wirken in beiden Stufen.

Das Proposal stellt eigene Gewichtsprofile je App-Typ als Möglichkeit in Aussicht. Darauf wird bewusst verzichtet: Die Gewichte sind konfigurierbar, alle Szenarien laufen aber mit demselben Default-Profil. Sonst wäre bei einem Unterschied zwischen zwei Empfehlungen nicht mehr trennbar, ob das Profil oder die Gewichtung ihn verursacht hat.

**Normalisierung** je Kriterium innerhalb der verbliebenen Kandidaten:

```
Nutzen:  norm = (x - min) / (max - min)
Kosten:  norm = (max - x) / (max - min)
max = min → norm = 1 für alle
```

`null`-Werte nehmen an der Berechnung von `min` und `max` nicht teil.

**Fehlende Werte** werden nicht als 0 gewertet, weil das ein Angebot unfair abwerten würde. Das Kriterium entfällt für dieses Angebot und sein Gewicht wird proportional auf die vorhandenen Kriterien desselben Angebots verteilt:

```
gewicht_i' = gewicht_i / Σ(Gewichte der vorhandenen Kriterien)
```

Das Angebot erhält das Flag `unvollstaendige_datenbasis`.

**Gesamtformel:**

```
Score = Σ (gewicht_i' × norm_i)        über alle Kriterien mit Wert, gerundet auf 4 Stellen
```

Intern wird ungerundet gerechnet, gerundet wird nur für die Ausgabe. Die Summe der ausgegebenen Beiträge entspricht dem Score bis auf Rundungsdifferenzen (< 0.001).

## Stufe 3 — Ranking & Ausgabe

Sortierung absteigend nach Score. Tie-Break: tieferer Preis, dann Anbieter und Produkt alphabetisch. Ausgeschlossene stehen alphabetisch nach Anbieter und Produkt. Das Ergebnis hängt damit nicht von der Reihenfolge ab, in der Discovery die Angebote liefert.

**Flags**

| Flag | Bedeutung |
|---|---|
| `unvollstaendige_datenbasis` | Angebot hat fehlende Werte (Erfolgskriterium Robustheit) |
| `anforderung_unspezifiziert` | Profil hat Lücken (nur Variante B) |

**Ausgabe**

```json
{
  "empfehlung": { "anbieter": "…", "produkt": "…", "kategorie": "vps", "score": 0.8400 },
  "ranking": [
    {
      "anbieter": "…", "produkt": "…", "url": "…", "kategorie": "vps", "score": 0.8400,
      "beitraege": {
        "preis_chf_monat": { "wert": 25.00, "norm": 0.6000, "gewicht": 0.30, "beitrag": 0.1800 }
      },
      "vertragslaufzeit_monate": 12,
      "abgeleitete_felder": [], "fehlende_felder": [], "flags": []
    }
  ],
  "ausgeschlossen": [ { "anbieter": "…", "produkt": "…", "gruende": [] } ],
  "metriken": { "kandidaten": 7, "ausgeschlossen": 12, "anteil_unvollstaendig": 0.29 }
}
```

Bleibt kein Kandidat übrig: `empfehlung: null`, `ranking: []`, alle Angebote stehen mit ihren Gründen unter `ausgeschlossen`.

## Grenzen des Verfahrens

- **Scores sind relativ.** Min-Max normalisiert innerhalb der Kandidatenmenge. Der Variantenvergleich (Unterfrage 2) darf deshalb nur Kategorie, Rang und Ausschlussgründe vergleichen, keine Score-Zahlen.
- **Ein einzelner Kandidat** erhält immer Score 1.0 (`max = min`). Der Wert ist dann nicht aussagekräftig.
- **WSM ist kompensatorisch.** Eine Schwäche lässt sich durch Stärken ausgleichen. Harte Anforderungen fängt deshalb der K.O.-Filter ab.
- **Überdimensionierung wird nicht gedämpft.** Ein grosses Angebot innerhalb des Budgets schlägt ein knapp passendes, weil CPU und RAM als Nutzen-Kriterien zählen. Das Proposal nennt Überdimensionierung als Problem, sieht im Scoring aber keine Gegenmassnahme vor. Punkt für die Diskussion.
- **Unvollständig dokumentierte Angebote sind im Vorteil.** Sie kommen durch den K.O.-Filter und ihr Gewicht wird auf die vorhandenen Kriterien verteilt, meist auf den Preis. `anteil_unvollstaendig` macht den Anteil sichtbar.
- **Der Preisvergleich ist bewusst grob.** Euro- und Dollar-Beträge gehen 1:1 als Franken ein, und Brutto- wie Nettopreise werden so übernommen, wie der Anbieter sie ausweist. Beides zusammen kann einen Preis um einen zweistelligen Prozentsatz verschieben. Der Preis hat mit 0.30 das höchste Gewicht, Rangfolgen innerhalb einer Kategorie sind deshalb mit Vorsicht zu lesen. Dafür braucht die Berechnung weder Kursstichtag noch Steuersätze, die bei der Abgabe veraltet wären.
- **Traffic-Inklusivvolumen** bleibt unberücksichtigt, Überschreitungskosten fliessen nicht in den Preis ein.
- **Die Vertragslaufzeit fliesst nicht in den Score ein.** Ein Angebot mit 12 Monaten Mindestlaufzeit wird gleich bewertet wie ein monatlich kündbares. Die Laufzeit steht in der Ausgabe und bleibt damit für den Nutzer sichtbar.

## Umsetzung

`scoring/engine.py`, eine Funktion je Stufe:

| Funktion | Stufe | Aufgabe |
|---|---|---|
| `lade_config` | – | liest `scoring/config.json`, prüft Gewichtssumme 1.0 |
| `aufbereiten` | 0 | effektiver Monatspreis, Kategorie-Defaults, `abgeleitete_felder`, `fehlende_felder` |
| `ausschlussgruende` | 1 | alle K.O.-Verstösse eines Angebots, leer = Kandidat |
| `bewerten` | 2 | Normalisierung, Umverteilung, Beitrag je Kriterium, Score |
| `bewerte` | 0–3 | Gesamtablauf mit Ranking, Flags und Metriken, Einstiegspunkt der Matching-Komponente |

Eingabe und Ausgabe sind JSON-kompatible Dicts. Die Eingabe wird nicht verändert.

## Tests

Unit-Tests der Engine, Umsetzung in 1.3 (`tests/test_scoring.py`, Ausführung: `README.md`). Sie stellen sicher, dass ein falsches Ergebnis in den Szenarien nicht aus der Rechenlogik kommt. Die Szenarien selbst werden in LangSmith evaluiert.

| Test | Prüft |
|---|---|
| Rechenbeispiel | Beispiel aus dem Proposal ergibt A 0.40, B 0.84, C 0.60. Die Beiträge je Kriterium summieren sich zum Score |
| Preisregel (Stufe 0) | Setup-Gebühr wird auf 12 Monate verteilt |
| Kategorie-Defaults (Stufe 0) | `shared`, `managed`, `vps`, `cloud`, `dedicated` erhalten die Werte gemäss Tabelle |
| K.O. je Kriterium (Stufe 1) | Preis, RAM, Speicher, Docker, Ressourcentyp, Verwaltung, Skalierung: ein Verstoss schliesst aus, Grund wird protokolliert |
| Profilwert `null` (Stufe 1) | keine Prüfung, Flag `anforderung_unspezifiziert` (Variante B). Vollständiges Profil: kein Flag |
| Fehlende Werte (Stufe 0–2) | ohne Preis oder Kategorie: Ausschluss. Sonst kein Ausschluss, Gewicht umverteilt, Flag `unvollstaendige_datenbasis` |
| Gleiche Werte (Stufe 2) | alle Kandidaten mit gleichem Wert erhalten `norm` 1 |
| Ranking (Stufe 3) | Tie-Break: tieferer Preis, dann Anbieter. Kein Kandidat: `empfehlung` ist `null`, alle Angebote ausgeschlossen |
| Metrik (Stufe 3) | `anteil_unvollstaendig` = Anteil der Kandidaten mit Flag `unvollstaendige_datenbasis` |
| Basisszenarien | Referenzprofile S1–S3 gegen 11 Fixture-Angebote über alle Kategorien: Top-1 in `kategorie_erwartet`, keine Kategorie aus `kategorien_ausgeschlossen` im Ranking |

**Auswahl der Tests.** Jede Regel dieser Spezifikation wird genau einmal geprüft, Stufe für Stufe: Preisregel, jede Kategorie, jedes K.O.-Kriterium, Profil- und Angebotswerte `null`, gleiche Werte, Tie-Break, leeres Ergebnis, Metrik. Dazu kommen die beiden Referenzen, die das Proposal selbst liefert: das Rechenbeispiel und die Erwartungswerte der drei Szenarien. Nicht geprüft werden Rundung (reine Ausgabeformatierung) und ungültige Eingaben, die die Schema-Validierung abfängt (1.4).

**Auswahl der Fixtures.** Das Set ist so zusammengestellt, dass die Szenario-Tests die Regeln mit realistischen Angeboten durchlaufen:

| Kriterium | Umsetzung im Set |
|---|---|
| alle Kategorien | 2 `shared`, 1 `managed`, 4 `vps`, 2 `cloud`, 2 `dedicated` |
| Anbieter-Scope | 8 der 10 Anbieter (ohne STRATO, All-Inkl) |
| Preisspanne | 4.59 bis 144 pro Monat. Das Budget schliesst in S1 Angebote aus, in S2 und S3 liegen alle darunter |
| Preisregeln | CHF, EUR und USD, ein Angebot mit Setup-Gebühr |
| fehlende Werte | Shared/Managed ohne CPU, RAM, Bandbreite (wie auf echten Seiten), ein VPS ohne Backup und Support |
| Kategorie-Defaults | Docker, Verwaltung, Ressourcentyp überall `null`, damit die Defaults greifen |
| Skalierung | Stufen 0, 1 und 2 vertreten |

In den Szenarien greifen damit alle K.O.-Kriterien ausser Ressourcentyp, den kein Referenzprofil verlangt. Dieser ist nur im Unit-Test abgedeckt.

Die Fixtures (`tests/fixtures/angebote.json`) sind Richtwerte, angelehnt an typische Pakete der 10 Anbieter. Sie wurden fertiggestellt, bevor das Ergebnis geprüft wurde, sonst bestätigt der Test nur die eigene Erwartung. Der Abgleich mit echten Seiten folgt in 3.11.

Aus der ersten Prüfung entstand `skalierung_min` als K.O. (siehe Abweichungen vom Proposal): Ohne diese Regel gewann in S2 ein Dedicated-Server.
