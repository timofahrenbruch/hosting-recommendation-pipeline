# Entscheidungen

Kurznotizen pro Arbeitsschritt. Nummern verweisen auf `PLAN.md`.

## 0.1 LLM-Backend

- BFH-Inferenzdienst, Modell `deepseek-v4.1-flash`, Alternative `qwen3.8-27b`.
- Mit und ohne VPN getestet. Einrichtung: `docs/setup-langflow.md`.
- Rate-Limit 2 parallele Requests, 60 RPM, 150k TPM. Discovery und Extraktion laufen deshalb sequenziell, Retry bei 429.

## 0.2 Anbieter-Scope

- Developer-VPS und Cloud zählen dazu, volle 10er-Liste.
- Sonst hätte Szenario 2 kaum Kandidaten. Von den 6 klassischen Hostern deckt nur Infomaniak VPS/Cloud ab.
- Abdeckung und Abgrenzung (Anbieter, Hosting-Typen, App-Typen) im Anforderungskatalog festgehalten. Empfehlung gilt nur innerhalb der 10 Anbieter und der modellierten Kategorien.
- Weitere App-Typen entfallen: andere Kriterien und Prioritäten bräuchten eigene Scoring-Modelle. Ausblick in `docs/diskussionspunkte.md`.

## 1.1 Referenzprofile und Anforderungskatalog

- Katalog in `docs/anforderungskatalog.md`. Referenzprofile aus der Szenarientabelle des Proposals (Kap. 4.4).
- Ranges auf Mindestwerte reduziert, nur die zählen für den K.O.-Filter.
- K.O.-Felder laut Proposal: Budget, RAM, Speicherplatz, Docker, Ressourcentyp. Dazu `verwaltung_min`, sonst gewinnt in S1 ein billiger unverwalteter VPS.
- CPU, Backup und Support nur im Scoring, nicht als K.O. Skalierung seit 1.2 auch K.O.
- Pro Szenario ein simulierter Nutzer mit festen Antworten, sonst ist die Profiling-Evaluation nicht reproduzierbar.
- S2 und S3 haben denselben Erwartungswert, so steht es im Proposal.
- Nicht im Profil: Bandbreite, Standort, Tech-Stack.

## 1.2 Scoring-Spezifikation

- `docs/scoring-spezifikation.md`, folgt Kap. 4.5 des Proposals.
- Vier Ergänzungen zum Proposal, dort begründet: `verwaltung_min` und `skalierung_min` als K.O., Kategorie-Defaults, Preisregeln.
- `skalierung_min` als K.O. nachträglich, als DSR-Iteration. Auslöser: In der Handrechnung mit den Fixtures gewinnt in S2 ein Dedicated-Server ohne Skalierung.
- Begründet ist die Regel mit dem Profil, nicht mit den Testdaten: Wer Auto-Scaling als kritisch nennt, stellt eine harte Anforderung. Gleiche Logik wie `verwaltung_min`. Ob die Regel auch ausserhalb der drei Szenarien trägt, prüfen die Kontrollszenarien (1.7).
- Ausgabe verschlankt: kein `abstand_zum_zweiten`, kein `version`-Block, Tie-Break nur Preis, dann Name.
- Unit-Tests auf Basisfälle beschränkt: Rechenbeispiel, je K.O.-Kriterium, je Kategorie, fehlende Werte, Basisszenarien.
- Keine Wechselkurse und keine MwSt.-Umrechnung. Euro gilt 1:1 als Franken, Preise wie ausgewiesen.
- Keine Sättigung von CPU und RAM, kein eigenes Gewichtsprofil je App-Typ.
- Tests ohne Langflow, LLM und Netz lauffähig.
- Bekannte Ungenauigkeiten: `docs/diskussionspunkte.md`.

## 1.3 Scoring-Engine

- `scoring/engine.py`, eine Funktion je Stufe der Spezifikation. Reines Python, keine Abhängigkeiten.
- Config als JSON statt YAML, damit kein zusätzliches Paket nötig ist.
- Extraktion liefert Werte in Katalog-Einheiten und als Monatspreis. Die Engine verteilt nur die Setup-Gebühr und übernimmt Fremdwährungen 1:1.
- Ausgabe gerundet auf 4 Stellen, Tests vergleichen mit Toleranz 0.001.
- Ausgeschlossene alphabetisch sortiert, damit das Ergebnis nicht von der Reihenfolge der Discovery abhängt.
- Fixtures sind Richtwerte, Abgleich mit echten Seiten in 3.11.
- Kubernetes-Cluster zählen zu `cloud` (Container-Plattform). Ausgeschlossen bleiben PaaS und Serverless.
- Tests: `pytest` in lokaler `.venv`, Befehl im README.

## 1.4 Extraktionsschema

- `scraping/extraction_schema.json`, JSON Schema 2020-12. Abgeleitet aus den Feldern, die die Engine liest.
- Zwei Ebenen: `paket` liefert die Extraktion, `angebot` ist die Eingabe der Engine (Paket plus `anbieter` und `url` aus der Pipeline). Die Extraktion bekommt so keine Felder, die sie nicht von der Seite lesen kann.
- Eine Seite liefert eine Liste von Paketen, weil Produktseiten meist mehrere Pakete zeigen.
- Alle Felder Pflicht, Wert darf `null` sein. Fehlende Werte sind damit explizit leer, wie im Proposal verlangt.
- Die Regeln für das LLM stehen in den `description`-Feldern: Einheiten, Stufen 0–2, Kategorien, `null` statt schätzen, keine Aktionspreise. Das Schema ist damit zugleich Prompt-Grundlage.
- Docker, Ressourcentyp und Verwaltung nur bei ausdrücklicher Angabe, sonst `null`. Dann greifen die Kategorie-Defaults der Engine.
- Das LLM rechnet Einheiten (MB → GB) und reine Jahrespreise (÷ 12) selbst um. Ob das zuverlässig klappt, prüft 3.11.
- Ob SmartScraperGraph das JSON Schema direkt nutzt oder ein Pydantic-Modell braucht, klärt 3.11.
- Tests: Schema gültig, alle Fixtures entsprechen ihm, Engine-Felder sind im Schema enthalten. Validierung mit `jsonschema`.

## Übergreifend

### Profiler

- Nach Proposal Kap. 3: funktionale Rückfragen, technische Werte über feste Regeln in Python abgeleitet.
- Ablauf: Dialog, Funktionsprofil, Ableitungsregeln, technisches Profil, Schema-Validierung mit Nachfrage.
- Evaluation zweistufig, damit klar wird, ob der Dialog oder die Regeln danebenliegen.
- Risiko Overfitting: Regeln nur an drei Referenzprofilen kalibriert.

### Zwei Pipeline-Varianten

- Raúl bezweifelt den Mehrwert des Profilers, daher zwei Varianten.
- A mit Profiler, B ohne. Discovery, Extraktion und Matching sind identisch.
- B läuft zweimal, mit Referenzwerten und mit Laien-Eingaben. Sonst hat B immer die richtigen Werte.
- Daraus entstand Unterfrage 2 im Proposal.

### DSR-Guidelines

- Proposal gegen die 7 Guidelines (Hevner et al. 2004) und die BFH-Struktur geprüft.
- Ergänzt: Beitrag, Teil-Artefakte, Evaluationsmethoden, Guidelines-Tabelle, Methodenkapitel, Management Summary.
- Kontrollszenarien als Gegenprobe zum Overfitting, nicht zur Kalibrierung.
- LangSmith-Tracing ab MVP, nicht erst in Phase 4.
- Literatur: vom Brocke et al. (2020), Triantaphyllou (2000).
