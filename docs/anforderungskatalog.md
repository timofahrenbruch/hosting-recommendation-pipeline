# Anforderungskatalog

Gemeinsame Felddefinitionen für Referenzprofile, Profiler-Schema (3.5), Extraktionsschema (1.4) und Scoring (1.2).

## Profilfelder

| Feld | Typ | Einheit / Werte | Verwendet in |
|---|---|---|---|
| `app_typ` | Enum | siehe App-Typen | Discovery-Query, Evaluator |
| `traffic_normal_min` | Integer | Besucher/Tag | Ableitungsregeln (3.2), Evaluator |
| `traffic_normal_max` | Integer | Besucher/Tag | Ableitungsregeln (3.2), Evaluator |
| `traffic_peak` | Integer / `null` | Besucher/Tag | Ableitungsregeln (3.2), Evaluator |
| `budget_chf_monat_max` | Zahl | CHF/Monat, siehe Preis | K.O. |
| `cpu_vcores_min` | Integer | vCPU | Discovery-Query, Evaluator |
| `ram_gb_min` | Zahl | GB | K.O. |
| `storage_gb_min` | Zahl | GB | K.O. |
| `docker_erforderlich` | Boolean | – | K.O. |
| `ressourcentyp_min` | Enum | `egal`, `vserver`, `dediziert` | K.O. |
| `verwaltung_min` | Enum | `egal`, `managed` | K.O. |
| `skalierung_min` | Stufe | 0–2 | Discovery-Query, Evaluator |
| `backup_min` | Stufe | 0–2 | Discovery-Query, Evaluator |
| `support_min` | Stufe | 0–2 | Discovery-Query, Evaluator |

Pflichtfelder: alle. Einzig `traffic_peak` darf `null` sein.

K.O.-Kriterien sind `budget_chf_monat_max`, `ram_gb_min`, `storage_gb_min`, `docker_erforderlich`, `ressourcentyp_min` und `verwaltung_min`. Die übrigen Mindestwerte dokumentieren die Anforderung, fliessen in die Discovery-Query ein und dienen dem Profiling-Evaluator. Im Scoring zählt der Angebotswert, nicht der Profil-Mindestwert.

In Variante B (direkte Eingabe ohne Profiler) dürfen Felder `null` sein. `null` heisst „keine Anforderung" und löst kein K.O. aus.

## Angebotsfelder

Gegenstück zu den Profilfeldern, gleiche Einheiten und Stufen. Jedes Angebot führt zusätzlich `abgeleitete_felder` und `fehlende_felder` (`scoring-spezifikation.md`, Stufe 0).

| Feld | Typ | Einheit / Werte | Verwendet in |
|---|---|---|---|
| `anbieter`, `produkt`, `url` | String | – | Ausgabe, Nachvollziehbarkeit |
| `kategorie` | Enum | siehe Angebotskategorien | Kategorie-Defaults, Evaluator |
| `preis_chf_monat` | Zahl | CHF/Monat, effektiv | K.O., Scoring (0.30) |
| `cpu_vcores` | Integer | vCPU | Scoring (0.15) |
| `ram_gb` | Zahl | GB | K.O., Scoring (0.15) |
| `storage_gb` | Zahl | GB | K.O. |
| `bandbreite_mbit` | Zahl | Mbit/s | Scoring (0.10) |
| `skalierung` | Stufe | 0–2 | Scoring (0.15) |
| `backup` | Stufe | 0–2 | Scoring (0.10) |
| `support` | Stufe | 0–2 | Scoring (0.05) |
| `docker_support` | Boolean | – | K.O. |
| `ressourcentyp` | Enum | `shared`, `vserver`, `dediziert` | K.O. |
| `verwaltung` | Enum | `managed`, `selbst` | K.O. |

Rohfelder für die Preisberechnung (`monatspreis_regulaer`, `waehrung`, `setup_gebuehr`, `abrechnungsintervall`, `vertragslaufzeit_monate`): Extraktionsschema (1.4), Umrechnung in `scoring-spezifikation.md`.

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

`budget_chf_monat_max` = maximaler Monatspreis in CHF, regulärer Preis (kein Aktionspreis). Preise werden so übernommen, wie der Anbieter sie ausweist. Setup-Gebühr, Fremdwährung und Vertragslaufzeit: `scoring-spezifikation.md`, Stufe 0.

## Vergleichsregeln (Evaluatoren)

**Profiling-Korrektheit**, generiertes Profil gegen Referenzprofil:
- Enums, Stufen, Booleans, Budget, CPU, RAM, Storage: exakt
- Traffic: ±10 %, `null` muss `null` sein

**Kategorie-Korrektheit** ist erfüllt, wenn:
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

Setup-Gebühr und Inklusiv-Traffic sind nicht ausgeschlossen, sondern in den Preisregeln geregelt (`scoring-spezifikation.md`, Stufe 0). Die Vertragslaufzeit wird extrahiert und ausgewiesen, fliesst aber weder in den Preis noch in den Score ein.
