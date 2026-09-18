# Langflow Setup — BFH-Inferenzdienst

Getestet mit Langflow Desktop v1.12.2.

## Voraussetzungen

- Login auf `inference.mlmp.ti.bfh.ch` nur via VPN (SwitchEduID)
- API-Key: Settings → Account → API keys

## Provider-Konfiguration (Langflow)

Settings → Model Providers → **OpenAI Compatible**:

| Variante | Base URL |
|---|---|
| mit VPN | `https://inference.mlmp.ti.bfh.ch/api/v1` |
| ohne VPN | `https://inference.proxy.ti.bfh.ch/api/v1` |

API Key: BFH-Key einfügen. Beide Varianten getestet (Modell-Liste + Chat-Completion im Playground) — funktionieren.

## Nötige Env-Variable

Langflows SSRF-Schutz blockt den BFH-Hostnamen (löst zu privater IP auf). Fix in `~/.langflow/data/.env`:

```
LANGFLOW_SSRF_ALLOWED_HOSTS=inference.mlmp.ti.bfh.ch,inference.proxy.ti.bfh.ch
```

Danach Langflow neu starten.

## Bekanntes Problem: Startup-Crash

Symptom: `sqlalchemy.exc.OperationalError: no such table: main.sso_config` beim Start, App bricht ab.
Ursache: kaputte Alembic-Migration in `~/.langflow/data/database.db` (nach App-Update).
Fix: Langflow-Prozesse beenden, `database.db` (+ `-wal`/`-shm`) umbenennen statt löschen, Langflow neu starten → frische DB.

## Modellwahl

Siehe `docs/entscheidungen.md` (`deepseek-v4.1-flash`, Alternative `qwen3.8-27b`).