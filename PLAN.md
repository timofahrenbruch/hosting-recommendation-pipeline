# Vorgehensplan

## Phase 0 — Vorfragen

- [x] 0.1 LLM-Backend (BFH vs. Claude) mit Raúl klären → BFH, siehe `docs/entscheidungen.md`
- [x] 0.2 Scope Developer-VPS/Cloud (Hetzner, netcup, Contabo, DigitalOcean) klären → eingeschlossen, siehe `docs/entscheidungen.md`

## Phase 1 — Konzeption

Reihenfolge wichtig: Scoring bestimmt Schema, nicht umgekehrt.

- [x] 1.1 Referenzprofile + Erwartungswerte, alle 3 Szenarien → `docs/anforderungskatalog.md`, `docs/szenarien/szenario-{1,2,3}.md`
- [x] 1.2 Scoring-Spezifikation (K.O., Gewichte, Normalisierung, fehlende Werte) → `docs/scoring-spezifikation.md`
- [x] 1.3 Scoring-Engine als Python-Modul, unit-getestet → `scoring/engine.py`, `scoring/config.json`, `tests/test_scoring.py`, `tests/fixtures/angebote.json`. Fixtures seit 1.5 echte Pakete
- [x] 1.4 Extraktionsschema ableiten, Fixtures per Test gegen das Schema validieren → `scraping/extraction_schema.json`, `tests/test_extraktionsschema.py`
- [x] 1.5 Anbieterliste (10 Anbieter) → `scraping/provider_list.json`, `tests/test_anbieterliste.py`. Fixtures durch 48 echte Pakete ersetzt
- [ ] 1.5b Machbarkeitstest ScrapeGraphAI. Variante A: Open-Source-Bibliothek mit BFH-LLM (Cloud-API nur als Vergleich). SearchGraph und SmartScraperGraph auf 2–3 Seiten der Anbieterliste, Ergebnis mit den Fixtures vergleichen (Bot-Schutz, JavaScript-Seiten, JSON nach Schema) → `docs/entscheidungen.md`
- [ ] 1.6 Evaluator-Logik Kategorie-Vergleich, Discovery-Messung (Pflicht-Treffer aus der Anbieterliste, Zusatzfunde, Fehlgriffe) → `evaluation/evaluators/`
- [ ] 1.7 1–2 Kontrollszenarien definieren, nicht für Kalibrierung verwenden (erst in Phase 4 laufen lassen) → `docs/szenarien/kontrollszenario-{1,2}.md`
- [ ] 1.8 Referenzprofile + Erwartungswerte mit Raúl plausibilisieren

Doku: Kapitel Anforderungsanalyse + Grundlagen können jetzt entstehen.

## Phase 2 — MVP (End-zu-Ende, gemockt)

- [ ] 2.1 Langflow Desktop, Version pinnen, `lfx`-Sync einrichten → `flows/`, `docs/entscheidungen.md`
- [ ] 2.2 LangSmith-Projekt + Price-Map-Eintrag, Tracing ab erstem Durchlauf (Iterationen messbar)
- [ ] 2.3 Dataset aus Phase 1 anlegen
- [ ] 2.4 Szenario 1 wählen
- [ ] 2.5 4 Knoten verdrahten — Profiler: Referenzprofil direkt eingespeist. Discovery: statische URL-Liste. Extraktion: Fixture-JSON aus 1.3 (`tests/fixtures/angebote.json`, enthält bewusste Lücken). Matching: echt (Engine aus 1.3) → `flows/mvp_szenario1.json`, `components/matching_node.py`
- [ ] 2.6 MVP als Variante B (ohne Profiler) weiterführen, nicht ersetzen → `flows/variante_b.json`

Doku: Grundgerüst Kapitel Umsetzung.

## Phase 3 — Komponenten real

Pro Szenario komplett durchziehen, dann nächstes.

Vorbereitung Profiler (fachliche Fragen, technische Ableitung per Regeln):

- [ ] 3.1 Funktionsprofil definieren (fachliche Felder) → `docs/anforderungskatalog.md`
- [ ] 3.2 Ableitungsregeln + Sizing-Tabelle (4 App-Typen × 3 Lastklassen, je ein Satz Begründung) → `docs/ableitungsregeln.md`
- [ ] 3.3 Ableitungsregeln als Python-Modul, unit-getestet (3 Funktionsprofile → 3 Referenzprofile) → `profiler/ableitung.py`, `tests/test_ableitung.py`
- [ ] 3.4 Szenarien: simulierter Nutzer nur fachlich, Referenz-Funktionsprofil ergänzen → `docs/szenarien/`
- [ ] 3.5 Funktionsprofil-Schema → `schemas/funktionsprofil_schema.json`
- [ ] 3.6 Schema-Validierung im Profiler: Pflichtfelder prüfen, gezielt nachfragen, erst dann an Discovery übergeben → `profiler/validierung.py`, `tests/test_validierung.py`
- [ ] 3.7 Profiling-Evaluator zweistufig (Funktionsprofil, abgeleitetes technisches Profil) → `evaluation/evaluators/`
- [ ] 3.8 Variante B: Laien-Eingaben pro Szenario definieren (typische Fehleinschätzungen, z. B. RAM zu knapp, Docker vergessen) → `docs/szenarien/`

- [ ] 3.9 Profiler real, Szenario 1 — Ziel: Funktionsprofil = Referenz, abgeleitetes Profil = Referenzprofil
- [ ] 3.10 Discovery real, Szenario 1 — Ziel: richtige Anbieterseiten
- [ ] 3.11 Extraktion real, Szenario 1 — Ziel: fehlende Felder = `null`, nie geschätzt. Ausgabe gegen das Extraktionsschema validieren. Achtung: Bei Hetzner und netcup zeigt ein automatischer Abruf andere MwSt. als die Fixtures (Schweizer Browser), Abweichungen dort sind kein Lesefehler. Echte Ausgabe mit den Fixtures abgleichen (Felder, Einheiten, Werte), Abweichungen in Schema, Stufe 0 oder Fixtures nachziehen
- [ ] 3.12 Matching-Check mit echten Daten, Szenario 1 — Ziel: Szenario 1 komplett real
- [ ] 3.13 Szenario 2 (Scope-Entscheid muss stehen) — Ziel: K.O. schliesst Shared aus, Empfehlung = VPS/Cloud
- [ ] 3.14 Szenario 3 — Ziel: Empfehlung zwischen Extremen aus 1/2

Doku: Kapitel Umsetzung wächst pro Schritt mit.

## Phase 4 — LangSmith

- [ ] 4.1 Evaluatoren andocken
- [ ] 4.2 Kosten-Richtwert (≤ CHF 0.20/Durchlauf) kalibrieren
- [ ] 4.3 Runs auswerten: Profiling-/Kategorie-Korrektheit, Kosten, Latenz, Datenvollständigkeit
- [ ] 4.4 Variantenvergleich: A vs. B (Referenz-Eingabe) vs. B (Laien-Eingabe) als separate Experimente, gleiches Dataset
- [ ] 4.5 Kontrollszenarien durchspielen (nicht Teil der Erfolgskriterien)
- [ ] 4.6 6 Erfolgskriterien gegenprüfen → `evaluation/results.md`

Doku: Kapitel Evaluation (nur Ergebnisse, Vorgehen steht im Methodenkapitel).

## Phase 5 — Abschluss

- [ ] 5.1 Diskussion (Sammlung: `docs/diskussionspunkte.md`): Forschungsfragen beantworten (inkl. Mehrwert Profiler), Beitrag (Artefakt, Profiler-Erkenntnis, Vorgehen Langflow), Grenzen der Evaluation (selbst erstellte Szenarien, nur 3 + Kontrollszenarien), Risiken (Websuche, Scoring-Aufwand, Langflow-Version, Profiler-Mehrdeutigkeit, Overfitting Ableitungsregeln)
- [ ] 5.2 Fazit
- [ ] 5.3 Management Summary
- [ ] 5.4 Repo-Doku finalisieren
- [ ] 5.5 Demo vorbereiten
- [ ] 5.6 Review gegen Outline, Erfolgskriterien und DSR-Guidelines (Tabelle im Proposal, Kap. 4.1)
- [ ] 5.7 Abgabe
