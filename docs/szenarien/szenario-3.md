# Szenario 3 — B2B-SaaS-Kundenportal

## Freitext-Input

> Kundenportal für unsere B2B-SaaS-Lösung, brauchen Docker für die Microservices, mittelgrosse Firma.

## Simulierter Nutzer

Antwortet nur auf das Gefragte, nennt Werte wie unten.

| Frage nach | Antwort |
|---|---|
| Traffic | normal 500–3000 Besucher pro Tag, bei Releases oder Kampagnen bis 10'000 |
| Budget | maximal 150 Franken im Monat |
| CPU / RAM | 2–4 vCPUs, mindestens 8 GB RAM |
| Speicher | 50 GB |
| Docker | ja, zwingend |
| Ressourcentyp | egal |
| Verwaltung | egal, wir können Server selbst administrieren |
| Skalierung | später hochrüsten können reicht, kein Auto-Scaling |
| Backup | täglich |
| Support | während Geschäftszeiten erreichbar, priorisiert |

## Referenzprofil

```json
{
  "app_typ": "saas_webapp",
  "traffic_normal_min": 500,
  "traffic_normal_max": 3000,
  "traffic_peak": 10000,
  "budget_chf_monat_max": 150,
  "cpu_vcores_min": 2,
  "ram_gb_min": 8,
  "storage_gb_min": 50,
  "docker_erforderlich": true,
  "ressourcentyp_min": "egal",
  "verwaltung_min": "egal",
  "skalierung_min": 1,
  "backup_min": 2,
  "support_min": 1
}
```

## Erwartungswert

```json
{
  "kategorie_erwartet": ["vps", "cloud"],
  "kategorien_ausgeschlossen": ["shared", "managed"]
}
```

Mittleres Profil zwischen Szenario 1 und 2.
