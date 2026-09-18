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