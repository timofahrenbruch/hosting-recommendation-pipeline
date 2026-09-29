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
| Kategorie-Defaults in Stufe 0 | Shared-Pakete nennen Docker fast nie. Ohne Default greift der Docker-K.O. nicht und die Szenarien 2 und 3 schliessen Shared nicht aus, wie das Proposal es erwartet. |
| Preisregeln (Setup-Gebühr, Vergleichsbasis) | Das Proposal vergleicht „Preis CHF/Monat", definiert die Aufbereitung aber nicht. Ohne feste Regel sind die Angebote nicht vergleichbar. |

Alles Übrige entspricht dem Proposal.

## Eingabe

| Teil | Inhalt |
|---|---|
| `profil` | technisches Profil gemäss Katalog. Felder dürfen `null` sein (Variante B) |
| `angebote[]` | Angebotsfelder gemäss Katalog |
| `config` | `version`, `gewichte`, `kategorie_defaults` |

## Stufe 0 — Aufbereitung

**Einheiten:** GB dezimal (1 GB = 1000 MB), Bandbreite in Mbit/s, Preis in CHF mit 2 Nachkommastellen.

**Preis** → effektiver Monatspreis:

```
preis_chf_monat = (setup_gebuehr + 12 × monatspreis_regulaer) / 12   [in CHF]
```

- Grundlage ist der veröffentlichte reguläre Monatspreis, keine Aktionspreise.
- Der Preis wird so übernommen, wie der Anbieter ihn ausweist. Es findet keine Umrechnung zwischen brutto und netto statt.
- Fremdwährungen werden 1:1 übernommen, ein Preis von 10 EUR gilt als 10 CHF. Es gibt keine Wechselkurse und keinen Kursstichtag.
- Die Vertragslaufzeit wird extrahiert und in der Ausgabe mitgeführt, beeinflusst den Preis aber nicht. Gerechnet wird immer mit dem regulären Monatspreis, unabhängig von der Mindestlaufzeit.

**Kategorie-Defaults** gelten nur für Felder, die nach der Extraktion `null` sind:

| Kategorie | `docker_support` | `verwaltung` | `ressourcentyp` |
|---|---|---|---|
| `shared`, `managed` | `false` | `managed` | `shared` |
| `vps`, `cloud` | `true` | `selbst` | `vserver` |
| `dedicated` | `true` | `selbst` | `dediziert` |

Fehlt die Kategorie, wird das Angebot ausgeschlossen (Grund `kategorie_fehlend`). Ohne Kategorie greifen weder die Defaults noch der Kategorie-Evaluator, und das Angebot käme an K.O.-Kriterien vorbei, die für seine Kategorie gelten.

**Nachvollziehbarkeit:** Jedes Angebot führt zwei Listen, `abgeleitete_felder` und `fehlende_felder`. So ist sichtbar, welche Werte nicht aus der Extraktion stammen.

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

Ein fehlender Angebotswert führt nur beim Preis zum Ausschluss. Sonst bleibt das Angebot im Rennen und das Feld steht in `fehlende_felder`. Ein `null` im Profil heisst „keine Anforderung" (Variante B) und wird nicht geprüft.

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

Speicherplatz, Docker, Verwaltung und Ressourcentyp wirken nur als K.O. und gehen nicht ins Scoring ein.

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

Intern wird ungerundet gerechnet, gerundet wird nur für die Ausgabe. Die Invariante „Summe der Beiträge = Score" wird auf den ungerundeten Werten mit Toleranz 1e-9 geprüft.

## Stufe 3 — Ranking & Ausgabe

Sortierung absteigend nach Score. Tie-Break: tieferer Preis, dann mehr RAM, dann Anbietername alphabetisch.

**Flags**

| Flag | Bedeutung |
|---|---|
| `unvollstaendige_datenbasis` | Angebot hat fehlende Werte (Erfolgskriterium Robustheit) |
| `anforderung_unspezifiziert` | Profil hat Lücken (nur Variante B) |

**Ausgabe**

```json
{
  "version": { "spezifikation": "1.2", "config": "…" },
  "empfehlung": { "anbieter": "…", "produkt": "…", "kategorie": "vps", "score": 0.8400 },
  "abstand_zum_zweiten": 0.0412,
  "ranking": [
    {
      "anbieter": "…", "produkt": "…", "kategorie": "vps", "score": 0.8400,
      "beitraege": {
        "preis_chf_monat": { "wert": 25.00, "norm": 0.6000, "gewicht": 0.30, "beitrag": 0.1800 }
      },
      "abgeleitete_felder": [], "fehlende_felder": [], "flags": []
    }
  ],
  "ausgeschlossen": [ { "anbieter": "…", "produkt": "…", "gruende": [] } ],
  "metriken": { "kandidaten": 7, "ausgeschlossen": 12, "anteil_unvollstaendig": 0.29 }
}
```

Bleibt kein Kandidat übrig: `empfehlung: null`, `ranking: []`, und unter `ausgeschlossen` stehen die Angebote mit den wenigsten Verstössen zuerst.

## Grenzen des Verfahrens

- **Scores sind relativ.** Min-Max normalisiert innerhalb der Kandidatenmenge. Der Variantenvergleich (Unterfrage 2) darf deshalb nur Kategorie, Rang und Ausschlussgründe vergleichen, keine Score-Zahlen.
- **Ein einzelner Kandidat** erhält immer Score 1.0 (`max = min`). Der Wert ist dann nicht aussagekräftig.
- **WSM ist kompensatorisch.** Eine Schwäche lässt sich durch Stärken ausgleichen. Harte Anforderungen fängt deshalb der K.O.-Filter ab.
- **Überdimensionierung wird nicht gedämpft.** Ein grosses Angebot innerhalb des Budgets schlägt ein knapp passendes, weil CPU und RAM als Nutzen-Kriterien zählen. Das Proposal nennt Überdimensionierung als Problem, sieht im Scoring aber keine Gegenmassnahme vor. Punkt für die Diskussion.
- **Unvollständig dokumentierte Angebote sind im Vorteil.** Sie kommen durch den K.O.-Filter und ihr Gewicht wird auf die vorhandenen Kriterien verteilt, meist auf den Preis. `anteil_unvollstaendig` macht den Anteil sichtbar.
- **Der Preisvergleich ist bewusst grob.** Euro-Beträge gehen 1:1 als Franken ein, und Brutto- wie Nettopreise werden so übernommen, wie der Anbieter sie ausweist. Beides zusammen kann einen Preis um bis zu einem Fünftel verschieben. Der Preis hat mit 0.30 das höchste Gewicht, Rangfolgen innerhalb einer Kategorie sind deshalb mit Vorsicht zu lesen. Dafür braucht die Berechnung weder Kursstichtag noch Steuersätze, die bei der Abgabe veraltet wären.
- **Traffic-Inklusivvolumen** bleibt unberücksichtigt, Überschreitungskosten fliessen nicht in den Preis ein.
- **Die Vertragslaufzeit fliesst nicht in den Score ein.** Ein Angebot mit 12 Monaten Mindestlaufzeit wird gleich bewertet wie ein monatlich kündbares. Die Laufzeit steht in der Ausgabe und bleibt damit für den Nutzer sichtbar.

## Tests (Umsetzung in 1.3)

### Ebene 1 — Regeltests

| # | Stufe | Fall | Erwartung |
|---|---|---|---|
| 1 | 0 | Preis in EUR, mit Setup-Gebühr und 12 Monaten Mindestlaufzeit | Betrag 1:1 als CHF, Setup amortisiert, Laufzeit ohne Einfluss |
| 2 | 0 | Einheiten 512 MB, 1 TB, 1 GiB | in GB dezimal umgerechnet |
| 3 | 0 | Preis fehlt | Ausschluss |
| 4 | 0 | Kategorie-Defaults je Kategorie (3 Fälle, parametrisiert) | Werte gemäss Tabelle, Felder in `abgeleitete_felder` |
| 5 | 0 | Feld wurde extrahiert | Default überschreibt den Wert nicht |
| 6 | 0 | Angebot ohne Kategorie | Ausschluss, Grund `kategorie_fehlend` |
| 7 | 1 | Je ein K.O. pro Kriterium (6 Fälle, parametrisiert) | Ausschluss, Grund protokolliert |
| 8 | 1 | Gleichheit: `ram == min`, `preis == budget` | kein Ausschluss |
| 9 | 1 | Ressourcentyp in beide Richtungen und `egal` | Profil `dediziert` schliesst `vserver` aus, umgekehrt nicht, `egal` prüft nicht |
| 10 | 1 | Angebotswert `null` in einem K.O.-Feld | durchlassen, Feld in `fehlende_felder` |
| 11 | 1 | Profilwert `null` (Variante B) | keine Prüfung, Flag `anforderung_unspezifiziert` |
| 12 | 2 | Beispielrechnung aus dem Proposal: A (15/4/2/0), B (25/8/4/1), C (40/8/4/1), Gewichte 0.4/0.3/0.2/0.1 | A 0.40, B 0.84, C 0.60 |
| 13 | 2 | `null` bei einem von drei Angeboten | nimmt an `min` und `max` nicht teil |
| 14 | 2 | Ein fehlender Wert | Gewicht umverteilt, Flag `unvollstaendige_datenbasis` |
| 15 | 2 | Mehrere fehlende Werte | Summe der effektiven Gewichte bleibt 1.0 |
| 16 | 2 | Alle Kriterien eines Angebots fehlen | Score 0, kein Absturz |
| 17 | 2 | Mehrere Kandidaten, identischer Wert (`max = min`) | `norm = 1` für alle |
| 18 | 3 | Zwei identische Scores, danach gleicher Preis | Tie-Break deterministisch |
| 19 | 3 | Nur ein Kandidat | `abstand_zum_zweiten: null` |
| 20 | 3 | Leere Angebotsliste | `empfehlung: null`, kein Absturz |
| 21 | 3 | Alle Angebote ausgeschlossen | `empfehlung: null`, alle Gründe protokolliert, wenigste Verstösse zuerst |

### Ebene 2 — Invarianten

Gelten für jede Eingabe. Geprüft werden sie auf allen Fixtures aus Ebene 1 und Ebene 3, nicht auf generierten Eingaben.

| # | Invariante | Deckt auf |
|---|---|---|
| 22 | Summe der Beiträge = Score | Aufschlüsselung ist der Nachweis für Nachvollziehbarkeit |
| 23 | Reihenfolge der Eingabeangebote ändert das Ergebnis nicht | versteckte Sortierabhängigkeit |
| 24 | Zweiter Aufruf liefert identisches Ergebnis | Reinheit, Voraussetzung reproduzierbarer Evaluation |
| 25 | Score liegt zwischen 0 und 1 | |

### Ebene 3 — Szenario-Tests

Fixture-Set von rund 15 Angeboten über alle 5 Kategorien, Werte an real publizierten Paketen der 10 Anbieter orientiert. Die drei Szenarien werden dagegen gerechnet und gegen `kategorie_erwartet` und `kategorien_ausgeschlossen` geprüft.

Die Fixtures werden fertiggestellt, bevor das erwartete Ergebnis geprüft wird. Sonst bestätigt der Test nur die eigene Erwartung.

Nicht abgedeckt und damit Sache von Phase 3: ob Discovery die richtige Produktseite findet, ob die Extraktion korrekte Werte liefert, ob die Kategorie einer echten Seite richtig erkannt wird.
