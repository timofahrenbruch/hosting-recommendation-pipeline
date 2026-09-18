# Vorgehensplan

Abgeleitet aus dem Proposal (Kapitel 6 "Project planning" und 7 "Outline"). Vier Arbeitspakete (AP), die aufeinander aufbauen. AP1 ist unabhängig vom LLM-Backend-Entscheid und kann sofort starten.

## Offene Vorfragen (parallel zu AP1 klären)

- [ ] **LLM-Backend:** BFH-Inferenzdienst vs. kommerzielles Modell (z. B. Claude) — mit Betreuer abstimmen
- [ ] **Scope Developer-VPS/Cloud:** Zählen Hetzner, netcup, Contabo, DigitalOcean zum Untersuchungsrahmen? — mit Betreuer abstimmen
- [ ] Falls BFH-Endpoint: Zugang unter `https://infra.pages.ti.bfh.ch/mlmp/src/llm/` beantragen

## AP1 — Anforderungsmatrix & Konzeption

Kein Code, keine Infrastruktur nötig — kann sofort starten.

- [ ] App-Typen festlegen (die 3 Testszenarien aus Kapitel 4, ggf. verfeinern)
- [ ] Mindestanforderungen pro App-Typ ausformulieren (Traffic, Budget, CPU/RAM, Docker, Skalierbarkeit, Backup, Support)
- [ ] Anbieterliste finalisieren (10 Anbieter, abhängig vom Scope-Entscheid oben)
- [ ] Extraktionsschema definieren (Preis, CPU, RAM, Storage, Bandbreite, Backup, Docker-Support, Vertragslaufzeit)
- [ ] Scoring-Algorithmus verfeinern: K.O.-Kriterien, Gewichte, Min-Max-Normalisierung, Umgang mit fehlenden Werten (Proposal Kapitel 4 als Ausgangsbasis)

**Output:** `scraping/provider_list.yaml`, `scraping/extraction_schema.json`, kurze Doku der Scoring-Logik

## AP2 — Umsetzung in Langflow

Startet, sobald das LLM-Backend feststeht.

- [ ] Langflow Desktop installieren, verwendete Version dokumentieren/fixieren
- [ ] LLM-Backend anbinden
- [ ] Grobe End-zu-End-Pipeline zuerst (Profiler → Discovery → Extraktion → Matching), einfache Logik, damit eine Anfrage einmal komplett durchläuft
- [ ] Komponenten einzeln verfeinern, in der Reihenfolge Profiler → Discovery → Extraktion → Matching
- [ ] Scoring-Algorithmus als Custom-Code-Komponente implementieren, mit Unit-Tests abgesichert
- [ ] `lfx` einrichten (Flow-Sync Desktop ↔ Git, siehe Repo-Setup)

**Output:** `flows/*.json`, `components/`, `tests/`

## AP3 — Test und Auswertung mit LangSmith

- [ ] LangSmith-Projekt einrichten; bei BFH-Modell eigenen Model-Price-Map-Eintrag anlegen
- [ ] Die 3 Testszenarien als LangSmith-Dataset hinterlegen
- [ ] Custom Evaluators bauen (Profiling-Korrektheit, Kategorie-Korrektheit)
- [ ] Pipeline pro Szenario laufen lassen, Traces auswerten (Kosten, Latenz, Datenvollständigkeit)
- [ ] Die 5 Erfolgskriterien aus Kapitel 4 gegenprüfen

**Output:** `evaluation/`, LangSmith-Dataset + Traces

## AP4 — Dokumentation

- [ ] Bericht schreiben, Kapitelstruktur gemäss Proposal-Outline (Einleitung, Grundlagen, Anforderungsanalyse, Umsetzung, Test & Auswertung, Diskussion, Fazit)
- [ ] Code/Repo-Doku vervollständigen
- [ ] Demo anhand der 3 Testszenarien vorbereiten

## Reihenfolge auf einen Blick

```
Vorfragen (Betreuer)  ─┐
                       ├─→ AP2 → AP3 → AP4
AP1 (sofort startbar) ─┘
```
