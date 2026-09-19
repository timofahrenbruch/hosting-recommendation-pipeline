# Szenario 2 — Vergleichsplattform für Reservierungen

## Freitext-Input

> Wir bauen ein Vergleichsportal für Ferienunterkünfte, ähnlich wie booking.com, mit ziemlich viel Traffic vor allem in den Ferien.

## Simulierter Nutzer

Antwortet nur auf das Gefragte, nennt Werte wie unten.

| Frage nach | Antwort |
|---|---|
| Traffic | 20'000–200'000 Besucher pro Tag, Spitzen in Ferien und Feiertagen, genaue Spitze unbekannt |
| Budget | maximal 600 Franken im Monat |
| CPU / RAM | mindestens 8 vCPUs, horizontal skalierbar, mindestens 16 GB RAM |
| Speicher | mindestens 100 GB |
| Docker | zwingend, wir haben Microservices |
| Ressourcentyp | egal, solange es skaliert |
| Verwaltung | egal, unser DevOps-Team kann Server selbst betreiben |
| Skalierung | kritisch, Auto-Scaling gewünscht |
| Backup | täglich, idealerweise redundant |
| Support | SLA mit garantierter Reaktionszeit |

## Referenzprofil

```json
{
  "app_typ": "portal_plattform",
  "traffic_normal_min": 20000,
  "traffic_normal_max": 200000,
  "traffic_peak": null,
  "budget_chf_monat_max": 600,
  "cpu_vcores_min": 8,
  "ram_gb_min": 16,
  "storage_gb_min": 100,
  "docker_erforderlich": true,
  "ressourcentyp_min": "egal",
  "verwaltung_min": "egal",
  "skalierung_min": 2,
  "backup_min": 2,
  "support_min": 2
}
```

## Erwartungswert

```json
{
  "kategorie_erwartet": ["cloud", "vps"],
  "kategorien_ausgeschlossen": ["shared", "managed"]
}
```

Beispiel-Anbieter (informativ): Hetzner, Infomaniak, DigitalOcean
