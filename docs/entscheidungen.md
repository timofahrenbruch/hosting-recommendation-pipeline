# Entscheidungen

Kurznotizen pro Arbeitsschritt. Nummern verweisen auf `PLAN.md`.

## 0.1 LLM-Backend

- BFH-Inferenzdienst, Modell `deepseek-v4.1-flash`, Alternative `qwen3.8-27b`.
- Mit und ohne VPN getestet. Einrichtung: `docs/setup-langflow.md`.
- Rate-Limit 2 parallele Requests, 60 RPM, 150k TPM. Discovery und Extraktion laufen deshalb sequenziell, Retry bei 429.

## 0.2 Anbieter-Scope

- Developer-VPS und Cloud zählen dazu, volle 10er-Liste.
- Sonst hätte Szenario 2 kaum Kandidaten. Von den 6 klassischen Hostern deckt nur Infomaniak VPS/Cloud ab.

## 1.1 Referenzprofile und Anforderungskatalog

- Katalog in `docs/anforderungskatalog.md`. Referenzprofile aus der Szenarientabelle des Proposals (Kap. 4.4).
- Ranges auf Mindestwerte reduziert, nur die zählen für den K.O.-Filter.
- K.O.-Felder laut Proposal: Budget, RAM, Speicherplatz, Docker, Ressourcentyp. Dazu `verwaltung_min`, sonst gewinnt in S1 ein billiger unverwalteter VPS.
- CPU, Skalierung, Backup und Support nur im Scoring, nicht als K.O.
- Pro Szenario ein simulierter Nutzer mit festen Antworten, sonst ist die Profiling-Evaluation nicht reproduzierbar.
- S2 und S3 haben denselben Erwartungswert, so steht es im Proposal.
- Nicht im Profil: Bandbreite, Standort, Tech-Stack.

## 1.2 Scoring-Spezifikation

- `docs/scoring-spezifikation.md`, folgt Kap. 4.5 des Proposals.
- Drei Ergänzungen zum Proposal, dort begründet: `verwaltung_min` als K.O., Kategorie-Defaults, Preisregeln.
- Keine Wechselkurse und keine MwSt.-Umrechnung. Euro gilt 1:1 als Franken, Preise wie ausgewiesen.
- Keine Sättigung von CPU und RAM, kein eigenes Gewichtsprofil je App-Typ.
- Tests auf drei Ebenen, alle ohne Langflow, LLM und Netz lauffähig.
- Bekannte Ungenauigkeiten: `docs/diskussionspunkte.md`.

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
