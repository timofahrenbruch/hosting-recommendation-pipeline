# Punkte für die Diskussion

Bekannte Grenzen und bewusste Vereinfachungen, gesammelt während der Konzeption. Grundlage für Schritt 5.1.

| Punkt | Kurz |
|---|---|
| Bandbreite trennt kaum | Shared wirbt mit „unlimitiert", VPS nennen alle 1000 Mbit/s. Das Kriterium hat 0.10 Gewicht, unterscheidet in der Praxis aber selten. Aus dem Proposal übernommen und bewusst beibehalten. |
| Überdimensionierung ungedämpft | CPU und RAM zählen als Nutzen. Ein grosses Angebot im Budget schlägt ein knapp passendes, obwohl die Einleitung Überdimensionierung als Problem nennt. |
| Lückenhafte Angebote im Vorteil | Fehlende Werte werden ausgeklammert und ihr Gewicht umverteilt, meist auf den Preis. Wer nichts publiziert, wird nicht bestraft. `anteil_unvollstaendig` macht es sichtbar. |
| Scores sind relativ | Min-Max normalisiert innerhalb der Kandidatenmenge. Der A/B-Vergleich darf nur Kategorie, Rang und Ausschlussgründe verwenden, keine Score-Zahlen. |
| Ein Gewichtsprofil für alle App-Typen | Das Proposal lässt eigene Profile je App-Typ offen. Verzicht, damit Unterschiede zwischen zwei Empfehlungen eindeutig dem Anforderungsprofil zuzuordnen sind. |
| Preisvergleich ist grob | Euro-Beträge gehen 1:1 als Franken ein, Brutto- und Nettopreise werden nicht vereinheitlicht. Zusammen bis zu einem Fünftel Abweichung, bei 0.30 Gewicht auf dem Preis. Dafür ohne Kursstichtag und Steuersätze, die bei der Abgabe veraltet wären. |
| Vertragslaufzeit ohne Wirkung | Wird extrahiert und ausgewiesen, fliesst aber nicht in Preis oder Score ein. Ein Angebot mit 12 Monaten Bindung steht gleich da wie ein monatlich kündbares. |
| Standort und Datenschutz ausgeschlossen | Alle 10 Anbieter haben CH/EU-Rechenzentren, also kaum Filterwirkung. Für einen erweiterten Anbieter-Scope wäre es ein Kriterium. |
| Overfitting der Ableitungsregeln | An drei Referenzprofilen kalibriert. Gegenprobe über die Kontrollszenarien, die nicht zur Kalibrierung dienen. |
| S2 und S3 mit gleichem Erwartungswert | Die Kategorie-Korrektheit trennt die beiden Szenarien nicht. S3 zeigt den Unterschied nur über das Ranking innerhalb der Kategorie. |
| Selbst erstellte Szenarien | Referenzprofile und Erwartungswerte stammen aus dieser Arbeit, nicht von echten Nutzern. Drei Szenarien plus ein bis zwei Kontrollszenarien. |
