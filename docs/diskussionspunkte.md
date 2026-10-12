# Punkte für die Diskussion

Bekannte Grenzen und bewusste Vereinfachungen, gesammelt während der Konzeption. Grundlage für Schritt 5.1.

| Punkt | Kurz |
|---|---|
| Bandbreite trennt kaum | Shared wirbt mit „unlimitiert", VPS nennen alle 1000 Mbit/s. Das Kriterium hat 0.10 Gewicht, unterscheidet in der Praxis aber selten. Aus dem Proposal übernommen und bewusst beibehalten. |
| Überdimensionierung ungedämpft | CPU und RAM zählen als Nutzen. Ein grosses Angebot im Budget schlägt ein knapp passendes, obwohl die Einleitung Überdimensionierung als Problem nennt. |
| Lückenhafte Angebote im Vorteil | Fehlende Bewertungswerte werden ausgeklammert und ihr Gewicht umverteilt, meist auf den Preis. Bei K.O.-Werten mildert die Rangfolge belegt vor unbelegt das ab, eingeführt nach der Erhebung echter Daten. |
| Datenvollständigkeit unterscheidet kaum | Mit echten Daten fehlt fast jedem Angebot ein Wert, `anteil_unvollstaendig` liegt dann bei rund 1.0. Aussagekräftiger wäre der Anteil fehlender Felder. |
| Strenge Profile, wenige Kandidaten | Mit `skalierung_min` 2 bleiben in S2 nur Angebote mit Auto-Scaling. Im Fixture-Set ist das ein einziges, sein Score 1.0 sagt dann nichts aus. Mit echten Daten prüfen. |
| Lesbarkeit der Anbieterseiten | Bot-Schutz (cyon), nachgeladene Preise (Hetzner, DigitalOcean), Konfiguratoren und Stundenpreise (Infomaniak). Ein Teil des Markts ist für automatische Abfragen schwer erreichbar, unabhängig von der Qualität des LLM. |
| Preise je Standort des Abrufs | Contabo und netcup zeigen je nach Standort andere Preise bzw. MwSt.-Sätze, Hetzner unterscheidet je Rechenzentrum. Reproduzierbar nur mit festem Abrufstandort (de-CH). |
| Kubernetes ohne Leistungsangaben | DigitalOcean nennt für Kubernetes nur ab-Preise je Knoten ohne CPU und RAM. In S2 bleiben zwei Kandidaten mit Flag `ko_wert_unbelegt`, die Empfehlung ist entsprechend unsicher. |
| Kubernetes je Knoten | Kubernetes wird mit Preis und Ressourcen eines Knotens erfasst. Ein skalierender Cluster braucht mehrere Knoten und kostet entsprechend mehr. Der Vergleich mit Einzelservern unterschätzt deshalb die Kosten. |
| Scores sind relativ | Min-Max normalisiert innerhalb der Kandidatenmenge. Der A/B-Vergleich darf nur Kategorie, Rang und Ausschlussgründe verwenden, keine Score-Zahlen. |
| Ein Gewichtsprofil für alle App-Typen | Das Proposal lässt eigene Profile je App-Typ offen. Verzicht, damit Unterschiede zwischen zwei Empfehlungen eindeutig dem Anforderungsprofil zuzuordnen sind. |
| Nur vier App-Typen | Reine Backends/APIs, ML, Games oder Streaming haben andere Kriterien und Prioritäten (z. B. Netzwerk, GPU, Egress). Ein Gewichtsprofil passt nicht für alle. Ausblick: eigenes Scoring-Modell je Typ, dazu Ableitungsregeln und Referenzprofil. |
| Preisvergleich ist grob | Euro- und Dollar-Beträge gehen 1:1 als Franken ein, Brutto- und Nettopreise werden nicht vereinheitlicht. Selbst ein Anbieter mischt beides (Hostpoint Webhosting inkl., Managed Flex Server exkl. MwSt.). Zusammen eine Abweichung im zweistelligen Prozentbereich, bei 0.30 Gewicht auf dem Preis. Dafür ohne Kursstichtag und Steuersätze, die bei der Abgabe veraltet wären. |
| Vertragslaufzeit ohne Wirkung | Wird extrahiert und ausgewiesen, fliesst aber nicht in Preis oder Score ein. Ein Angebot mit 12 Monaten Bindung steht gleich da wie ein monatlich kündbares. |
| Standort und Datenschutz ausgeschlossen | Alle 10 Anbieter haben CH/EU-Rechenzentren, also kaum Filterwirkung. Für einen erweiterten Anbieter-Scope wäre es ein Kriterium. |
| Overfitting der Ableitungsregeln | An drei Referenzprofilen kalibriert. Gegenprobe über die Kontrollszenarien, die nicht zur Kalibrierung dienen. |
| S2 und S3 mit gleichem Erwartungswert | Die Kategorie-Korrektheit trennt die beiden Szenarien nicht. S3 zeigt den Unterschied nur über das Ranking innerhalb der Kategorie. |
| Selbst erstellte Szenarien | Referenzprofile und Erwartungswerte stammen aus dieser Arbeit, nicht von echten Nutzern. Drei Szenarien plus ein bis zwei Kontrollszenarien. |
