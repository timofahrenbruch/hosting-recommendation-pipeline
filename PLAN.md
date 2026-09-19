# Vorgehensplan

## Phase 0 — Vorfragen

- [x] LLM-Backend (BFH vs. Claude) mit Raúl klären → BFH, siehe `docs/entscheidungen.md`
- [x] Scope Developer-VPS/Cloud (Hetzner, netcup, Contabo, DigitalOcean) klären → eingeschlossen, siehe `docs/entscheidungen.md`

## Phase 1 — Konzeption

Reihenfolge wichtig: Scoring bestimmt Schema, nicht umgekehrt.

- [x] Referenzprofile + Erwartungswerte, alle 3 Szenarien → `docs/anforderungskatalog.md`, `docs/szenarien/szenario-{1,2,3}.md`
- [ ] Scoring-Spezifikation (K.O., Gewichte, Normalisierung, fehlende Werte) → `docs/scoring-spezifikation.md`
- [ ] Scoring-Engine als Python-Modul, unit-getestet → `scoring/engine.py`, `tests/test_scoring.py`
- [ ] Extraktionsschema ableiten → `scraping/extraction_schema.json`
- [ ] Anbieterliste (10 Anbieter) → `scraping/provider_list.yaml`
- [ ] Evaluator-Logik Kategorie-Vergleich → `evaluation/evaluators/`

Doku: Kapitel Anforderungsanalyse + Grundlagen können jetzt entstehen.

## Phase 2 — MVP (End-zu-Ende, gemockt)

- [ ] Langflow Desktop, Version pinnen, `lfx`-Sync einrichten → `flows/`, `docs/entscheidungen.md`
- [ ] Szenario 1 wählen
- [ ] 4 Knoten verdrahten — Profiler: Referenzprofil direkt eingespeist. Discovery: statische URL-Liste. Extraktion: Fixture-JSON mit bewusster Lücke. Matching: echt (Engine aus Phase 1) → `flows/mvp_szenario1.json`, `fixtures/`, `components/matching_node.py`

Doku: Grundgerüst Kapitel Umsetzung.

## Phase 3 — Komponenten real

Pro Szenario komplett durchziehen, dann nächstes.

Vorbereitung Profiler (fachliche Fragen, technische Ableitung per Regeln):

- [ ] Funktionsprofil definieren (fachliche Felder) → `docs/anforderungskatalog.md`
- [ ] Ableitungsregeln + Sizing-Tabelle (alle App-Typen × Lastklassen, mit Begründung) → `docs/ableitungsregeln.md`
- [ ] Ableitungsregeln als Python-Modul, unit-getestet (3 Funktionsprofile → 3 Referenzprofile) → `profiler/ableitung.py`, `tests/test_ableitung.py`
- [ ] Szenarien: simulierter Nutzer nur fachlich, Referenz-Funktionsprofil ergänzen → `docs/szenarien/`
- [ ] Funktionsprofil-Schema → `schemas/funktionsprofil_schema.json`
- [ ] Profiling-Evaluator zweistufig (Funktionsprofil, abgeleitetes technisches Profil) → `evaluation/evaluators/`

- [ ] Profiler real, Szenario 1 — Ziel: Funktionsprofil = Referenz, abgeleitetes Profil = Referenzprofil
- [ ] Discovery real, Szenario 1 — Ziel: richtige Anbieterseiten
- [ ] Extraktion real, Szenario 1 — Ziel: fehlende Felder = `null`, nie geschätzt
- [ ] Matching-Check mit echten Daten, Szenario 1 — Ziel: Szenario 1 komplett real
- [ ] Szenario 2 (Scope-Entscheid muss stehen) — Ziel: K.O. schliesst Shared aus, Empfehlung = VPS/Cloud
- [ ] Szenario 3 — Ziel: Empfehlung zwischen Extremen aus 1/2

Doku: Kapitel Umsetzung wächst pro Schritt mit.

## Phase 4 — LangSmith

- [ ] LangSmith-Projekt + Price-Map-Eintrag
- [ ] Dataset aus Phase 1
- [ ] Evaluatoren andocken
- [ ] Kosten-Richtwert (≤ CHF 0.20/Durchlauf) kalibrieren
- [ ] Runs auswerten: Profiling-/Kategorie-Korrektheit, Kosten, Latenz, Datenvollständigkeit
- [ ] 5 Erfolgskriterien gegenprüfen → `evaluation/results.md`

Doku: Kapitel Test & Auswertung.

## Phase 5 — Abschluss

- [ ] Diskussion (Risiken: Websuche, Scoring-Aufwand, Langflow-Version, Profiler-Mehrdeutigkeit, Overfitting Ableitungsregeln)
- [ ] Fazit
- [ ] Repo-Doku finalisieren
- [ ] Demo vorbereiten
- [ ] Review gegen Outline + Erfolgskriterien
- [ ] Abgabe
