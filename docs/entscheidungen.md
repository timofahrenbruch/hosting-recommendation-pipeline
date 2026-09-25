# Entscheidungen

## 2026-09-18 — LLM-Backend: BFH-Zugang

- Login (`inference.mlmp.ti.bfh.ch`) nur via VPN möglich, Auth über SwitchEduID
- API-Key erstellt (Settings → Account → API keys)
- Langflow SSRF-Schutz blockte BFH-Hostname (private IP) → `LANGFLOW_SSRF_ALLOWED_HOSTS` in `~/.langflow/data/.env` gesetzt
- Test mit VPN + Base URL `https://inference.mlmp.ti.bfh.ch/api/v1`: Modell-Liste + Chat-Completion im Playground funktionieren ✓
- Test ohne VPN + Proxy-URL `https://inference.proxy.ti.bfh.ch/api/v1`: funktioniert ebenfalls ✓
- Technisch bestätigt: BFH-Inferenzdienst lässt sich in Langflow einbinden, mit und ohne VPN
- **Entscheid:** LLM-Backend = BFH-Inferenzdienst
- Modell: `deepseek-v4.1-flash` (Speed 4/5, Intelligenz 4/5, 1M Kontext, MIT-Lizenz). Alternative zum Vergleich: `qwen3.8-27b`
- Rate-Limit BFH (fix, nicht wählbar): 2 gleichzeitige Requests, 60 RPM, 150k TPM pro User → Discovery/Extraktion über die 10 Anbieter sequenziell verarbeiten, Retry/Backoff für 429 einplanen (Phase 3)

## 2026-09-18 — Scope: Developer-VPS/Cloud-Anbieter

- Frage: zählen Hetzner, netcup, Contabo, DigitalOcean (Developer-VPS/Cloud) zum Untersuchungsrahmen, oder nur die 6 klassischen Hoster (Hostpoint, Infomaniak, cyon, IONOS, STRATO, All-Inkl)?
- **Entscheid:** einschliessen — volle 10er-Anbieterliste
- Begründung: ohne sie hätte Szenario 2 (Docker zwingend, Auto-Scaling, hohe Last) kaum Kandidaten — von den 6 klassischen deckt nur Infomaniak Cloud/VPS ab. K.O.-Filter + Ranking liessen sich damit kaum sinnvoll demonstrieren.

## 2026-09-19 — Szenarien maschinenlesbar gemacht

- Felder, Stufen (0–2), App-Typen und Angebotskategorien zentral in `docs/anforderungskatalog.md`
- Regel: jedes Profilfeld hat einen Verwender (K.O., Scoring, Discovery, Evaluator), alle Werte typisiert statt Prosa
- Ranges aus dem Proposal auf Mindestwerte reduziert (z. B. RAM 16–32 GB → `ram_gb_min: 16`), da nur der Mindestwert für den K.O.-Filter zählt
- Nicht im Profil: Bandbreite (nur Angebotsseite bewertet), Standort, Tech-Stack (kein Verwender)
- Ressourcentyp im Proposal nicht spezifiziert → `egal` für alle 3 Szenarien
- Pro Szenario neu: simulierter Nutzer (feste Antworten, nötig für reproduzierbare Profiling-Evaluation) und maschinenprüfbarer Erwartungswert (`kategorie_erwartet`, `kategorien_ausgeschlossen`)
- Stufen-Zuordnung eigene Einschätzung aus Proposal-Freitext, z. B. S3 Support "Business während Geschäftszeiten" → 1, S2 "Business/SLA" → 2
- Neues K.O.-Feld `verwaltung_min` (`egal`/`managed`), nicht im Proposal. Grund: ohne dieses Feld gewinnt in S1 ein günstiger unverwalteter VPS (besteht alle K.O., schlägt Shared-Hosting bei Preis/CPU/RAM) → falsche Empfehlung für Nutzer ohne Admin-Know-how. S1 = `managed`, S2/S3 = `egal`
- Support-Stufe 2 umfasst auch garantierte Verfügbarkeit (Uptime-SLA)
- Standort/Datenschutz bewusst ausgeschlossen: nicht im Proposal, alle 10 Anbieter mit CH/EU-Rechenzentren → kaum Filterwirkung. Wird in Diskussion/Ausblick erwähnt
- Weitere bewusst ausgeschlossene Faktoren: siehe `docs/anforderungskatalog.md`

## 2026-09-19 — Profiler: fachliche Fragen statt technischer

- Abweichung vom Proposal: Profiler fragt nicht direkt nach CPU/RAM usw., sondern nach Funktion der Anwendung (Inhalte, Besucher, Ausfallfolgen, Team-Know-how …)
- Aufbau: LLM-Dialog → Funktionsprofil → deterministische Ableitungsregeln (Python, unit-getestet) → technisches Profil gemäss `docs/anforderungskatalog.md`
- Begründung: realistischer für Nutzer ohne Technikwissen; Ableitung bleibt nachvollziehbar und reproduzierbar statt LLM-Blackbox
- Evaluation zweistufig: (a) Funktionsprofil korrekt erhoben, (b) Regeln liefern Referenzprofil → Fehlerquelle lokalisierbar
- Technisches Referenzprofil bleibt Ground Truth und Schnittstelle für Scoring/Extraktion — Schritte 1.2–1.4 nicht betroffen
- Umsetzung erst vor Profiler real (Phase 3), siehe `PLAN.md`
- Risiko: Regeln an 3 Referenzprofilen kalibriert → Overfitting. Gegenmassnahme: vollständige Sizing-Tabelle mit Begründung pro Zelle; Thema in Diskussion

## 2026-09-25 — Zwei Pipeline-Varianten (mit/ohne Profiler)

- Anlass: Raúl bezweifelt, dass der Profiler einen Mehrwert bietet
- **Entscheid:** Pipeline in zwei Varianten. A: Profiler vorgelagert, fachliche Fragen → technische Ableitung. B: ohne Profiler, Nutzer gibt technische Spezifikationen direkt ein (schema-validiert)
- Discovery, Extraktion, Matching in beiden Varianten identisch → Unterschiede eindeutig dem Profiler zuordenbar
- Neue Unterfrage 2 im Proposal: Mehrwert des Profilers (Empfehlungsqualität, Kosten, Latenz)
- Variante B zweimal laufen lassen: mit Referenz-Spezifikationen (versierter Nutzer) und mit Laien-Eingaben. Sonst bekommt B immer die korrekten Werte und der Vergleich ist unfair
- MVP aus Phase 2 (Referenzprofil direkt eingespeist) = Grundlage für Variante B

## 2026-09-25 — Abgleich mit DSR-Guidelines

- Proposal gegen die 7 Guidelines (Hevner et al. 2004) und die BFH-Struktur für DSR-Arbeiten geprüft, bewusst praxisnah gehalten
- Neu im Proposal: Beitrag der Arbeit benannt, Teil-Artefakte (Construct/Model/Method), Evaluationsmethoden (descriptive, testing, experimental), Guidelines-Tabelle, Methodenkapitel in Outline, Management Summary
- Kontrollszenarien (1–2) gegen Overfitting: werden nicht zur Kalibrierung verwendet, erst in der Evaluation durchgespielt
- LangSmith-Tracing ab MVP statt erst in Phase 4, damit Iterationen messbar sind
- Literatur minimal ergänzt: vom Brocke et al. (2020), Triantaphyllou (2000) für WSM

