# Szenario 1 — Gymivorbereitungskurse ZH

## Freitext-Input

> Anmeldeseite für Gymivorbereitungskurse in Zürich, einfache WordPress-Seite, eher wenig Traffic ausser kurz vor Anmeldeschluss.

## Simulierter Nutzer

Antwortet nur auf das Gefragte, nennt Werte wie unten.

| Frage nach | Antwort |
|---|---|
| Traffic | normal 50–300 Besucher pro Tag, kurz vor Anmeldeschluss bis 2000 |
| Budget | höchstens 25 Franken im Monat |
| CPU / RAM | laut unserem Webentwickler reichen 1 vCPU und 2 GB RAM |
| Speicher | etwa 10 GB, eher mehr Luft wäre gut |
| Docker | brauchen wir nicht |
| Ressourcentyp | ist uns egal, geteiltes Hosting ist ok |
| Verwaltung | wir haben kein Know-how, um einen Server selbst zu betreuen |
| Skalierung | nicht wichtig |
| Backup | wöchentlich reicht |
| Support | E-Mail-Support reicht, keine Reaktionszeit nötig |

## Referenzprofil

```json
{
  "app_typ": "website_cms",
  "traffic_normal_min": 50,
  "traffic_normal_max": 300,
  "traffic_peak": 2000,
  "budget_chf_monat_max": 25,
  "cpu_vcores_min": 1,
  "ram_gb_min": 2,
  "storage_gb_min": 10,
  "docker_erforderlich": false,
  "ressourcentyp_min": "egal",
  "verwaltung_min": "managed",
  "skalierung_min": 0,
  "backup_min": 1,
  "support_min": 0
}
```

## Erwartungswert

```json
{
  "kategorie_erwartet": ["shared", "managed"],
  "kategorien_ausgeschlossen": []
}
```

Beispiel-Anbieter (informativ): Hostpoint, cyon
