# Anforderungen für Trade-Republic-Dashboard

## Projektzweck

Dieses Projekt bietet ein lokales Dashboard zur Analyse von Trade Republic Export-Dateien. Es soll Nutzern helfen, ihre Finanztransaktionen, Portfolioentwicklung, Dividenden und Gebühren schnell und sicher zu uebersichtlichen.

## Funktionale Anforderungen

- Benutzer koennen eine lokale Exportdatei hochladen (CSV oder Excel).
- Die App validiert die Datei und gibt klares Feedback bei Problemen.
- Die App stellt die importierten Transaktionen in einer Tabelle dar.
- Die App zeigt Portfolio-Kennzahlen wie Gesamtkosten, Gebühren, Datumsspanne und Waehrung an.
- Die App bietet Uebersichten fuer Portfolio, Dividenden, Allokation und Transaktionen.
- Die App zeigt einfache Visualisierungen und Berichte im Streamlit-Interface.
- Erweiterungen an Importformaten oder Auswertungen sollen einfach hinzufuegbar sein.

## Nicht-funktionale Anforderungen

- Die App laeuft lokal ohne externe Authentifizierung oder Remote-APIs.
- Anwendungen sollen sicher sein, indem keine Zugangsdaten gespeichert oder auf GitHub hochgeladen werden.
- Fehlermeldungen enthalten keine sensiblen Daten.
- Die Architektur soll modular sein, damit neue Analyse-Module leicht hinzugefuegt werden koennen.

## Ausgeschlossener Scope

- Keine Login-Automatisierung fuer Trade Republic.
- Kein Zugriff auf inoffizielle Trade Republic APIs.
- Keine Nutzung von externen Wechselkursdaten fuer Waehrungsumrechnung.
- Kein Tracking oder Monitoring ausserhalb der Kernfunktionalitaet.
- Keine fancy Visualisierungen, die nicht direkt mit der Datenanalyse zusammenhaengen.

## Wartbarkeit

- Das Hinzufuegen neuer Einheiten (z. B. neue Importformate oder neue Auswertungen) soll ohne groesseren Umbau moeglich sein.
- Die Datenverarbeitung soll klar getrennt von der Darstellung sein.
- Code soll mit `pytest` testbar und mit `ruff` lintbar sein.
