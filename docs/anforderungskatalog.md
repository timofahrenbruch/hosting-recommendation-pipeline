# Anforderungskatalog

Gemeinsame Felddefinitionen für Referenzprofile, Profiler-Schema (1.5), Extraktionsschema (1.4) und Scoring (1.2).

## Profilfelder

| Feld | Typ | Einheit / Werte | Verwendet in |
|---|---|---|---|
| `app_typ` | Enum | siehe App-Typen | Discovery-Query, Evaluator |
| `traffic_normal_min` | Integer | Besucher/Tag | Evaluator (Kontext) |
| `traffic_normal_max` | Integer | Besucher/Tag | Evaluator (Kontext) |
| `traffic_peak` | Integer / `null` | Besucher/Tag | Evaluator (Kontext) |
| `budget_chf_monat_max` | Zahl | CHF/Monat, siehe Preis | K.O. |
| `cpu_vcores_min` | Integer | vCPU | K.O.? (1.2) |
| `ram_gb_min` | Zahl | GB | K.O. |
| `storage_gb_min` | Zahl | GB | K.O. |
| `docker_erforderlich` | Boolean | – | K.O. |
| `ressourcentyp_min` | Enum | `egal`, `vserver`, `dediziert` | K.O. |
| `verwaltung_min` | Enum | `egal`, `managed` | K.O. |
| `skalierung_min` | Stufe | 0–2 | Scoring, K.O.? (1.2) |
| `backup_min` | Stufe | 0–2 | Scoring, K.O.? (1.2) |
| `support_min` | Stufe | 0–2 | Scoring, K.O.? (1.2) |

Pflichtfelder: alle. Einzig `traffic_peak` darf `null` sein.

## App-Typen

| Wert | Bedeutung |
|---|---|
| `website_cms` | Website/Blog auf CMS (z. B. WordPress) |
| `webshop` | E-Commerce |
| `portal_plattform` | Portal mit vielen anonymen Nutzern (z. B. Such-/Vergleichsportal) |
| `saas_webapp` | Webanwendung mit Login und Geschäftslogik |

## Stufen

**Skalierung**

| Stufe | Bedeutung |
|---|---|
| 0 | keine Skalierung nötig / möglich |
| 1 | vertikal upgradebar (Paketwechsel ohne Migration) |
| 2 | horizontal / Auto-Scaling |

**Backup**

| Stufe | Bedeutung |
|---|---|
| 0 | kein oder nur manuelles Backup |
| 1 | automatisch, mind. wöchentlich |
| 2 | automatisch, täglich |

**Support**

| Stufe | Bedeutung |
|---|---|
| 0 | Basic: Ticket/E-Mail ohne Reaktionszusage |
| 1 | Erweitert: priorisiert oder Telefon zu Geschäftszeiten |
| 2 | SLA: garantierte Reaktionszeit oder Verfügbarkeit (z. B. 99,9 %), oder 24/7 |

**Ressourcentyp**

Reihenfolge `shared` < `vserver` < `dediziert`. Profil `egal` akzeptiert alles.

| Wert | Bedeutung |
|---|---|
| `shared` | geteilte Ressourcen (nur Angebotsseite) |
| `vserver` | virtuelle Maschine mit zugesicherten Ressourcen |
| `dediziert` | physischer Server exklusiv |

**Verwaltung**

Profil `managed` schliesst Angebote mit `selbst` aus. Profil `egal` akzeptiert alles.

| Wert | Bedeutung |
|---|---|
| `managed` | Anbieter betreibt Betriebssystem, Updates, Sicherheit |
| `selbst` | Nutzer administriert den Server selbst (nur Angebotsseite) |

## Angebotskategorien

| Wert | Bedeutung |
|---|---|
| `shared` | Shared Hosting / Webhosting-Pakete |
| `managed` | verwaltetes Hosting, inkl. Managed WordPress |
| `vps` | virtueller Server, selbst administriert |
| `cloud` | skalierbare Instanzen / Container-Plattform |
| `dedicated` | dedizierter physischer Server |

## Preis

`budget_chf_monat_max` = maximaler Monatspreis in CHF inkl. MwSt., regulärer Preis (kein Aktionspreis). Umrechnung Fremdwährung und Vertragslaufzeit: Scoring-Spezifikation (1.2).

## Vergleichsregeln (Evaluatoren)

**Profiling-Korrektheit** — generiertes Profil vs. Referenzprofil:
- Enums, Stufen, Booleans, Budget, CPU, RAM, Storage: exakt
- Traffic: ±10 %, `null` muss `null` sein

**Kategorie-Korrektheit** — erfüllt, wenn:
- Top-1-Empfehlung in `kategorie_erwartet`
- kein Angebot aus `kategorien_ausgeschlossen` im Ranking

## Bewusst ausgeschlossen

| Faktor | Grund |
|---|---|
| Bandbreite (Profilseite) | kein sinnvoll erhebbarer Profilwert, nur auf Angebotsseite bewertet |
| Standort / Datenschutz (CH/EU) | nicht im Proposal; alle 10 Anbieter haben CH/EU-Rechenzentren → kaum Filterwirkung. Erwähnung in Diskussion/Ausblick |
| Domain, E-Mail, SSL inklusive | bei Shared/Managed Standard |
| PHP-/DB-Versionen, Tech-Stack | bei allen Kandidaten gegeben |
| DDoS-Schutz, Firewall, Monitoring | schwer vergleichbar |
| Support-Sprache, Nachhaltigkeit | nicht entscheidungsrelevant für die Szenarien |

Inkl. Traffic-Volumen, Setup-Gebühr, Kündigungsfrist: nicht ausgeschlossen, sondern Teil der Preisregeln (1.2).

## Offen für 1.2

- `cpu_vcores_min`, `skalierung_min`, `backup_min`, `support_min` zusätzlich als K.O. oder nur gewichtet?
- `null` in K.O.-Feldern (Shared-Hoster nennen RAM/vCPU/Docker oft nicht) — ausschliessen oder durchlassen?
- Preisregeln: Fremdwährung, MwSt., Aktionspreis, Vertragslaufzeit
