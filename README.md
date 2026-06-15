# Trade-Republic-Dashboard

Ein lokales Finanz-Dashboard, das Trade-Republic-Daten importiert, analysiert und uebersichtlich visualisiert.

## Ziel und Scope

Ziel des Projekts ist ein lokal laufendes Dashboard zur Auswertung eigener Finanzdaten aus Trade Republic. Der Fokus liegt auf einem sicheren, nachvollziehbaren Import von Export-Dateien und einer klaren Darstellung von Portfolio, Transaktionen und Auswertungen.

Zu Beginn wird bewusst keine echte Trade-Republic-Login-Automatisierung umgesetzt. Es werden keine Passwoerter, API-Keys oder Zugangsdaten gespeichert.

## Datenquelle

Als Datenquelle sollen zunaechst lokale Export-Dateien verwendet werden:

- CSV-Export von Trade Republic
- Excel-Export von Trade Republic, falls verfuegbar

Nicht Teil des ersten Scopes sind:

- Login-Scraping
- inoffizielle APIs
- Speicherung von Zugangsdaten
- automatischer Zugriff auf das Depot

Dieser Ansatz reduziert Security-Risiken und vermeidet den Umgang mit sensiblen Login-Daten.

## Bedrohungsmodell

| Frage                        | Antwort                                                                    |
| ---------------------------- | -------------------------------------------------------------------------- |
| Welche Daten sind sensibel?  | Depotwerte, Transaktionen, IBAN, Name und weitere persoenliche Finanzdaten |
| Wer koennte angreifen?       | Malware, fremde Nutzer am Laptop oder versehentliche GitHub-Leaks          |
| Was darf nie passieren?      | Finanzdaten oder Zugangsdaten landen auf GitHub                            |
| Wo werden Daten gespeichert? | Lokal auf dem eigenen Rechner                                              |
| Wer hat Zugriff?             | Nur der lokale Nutzer                                                      |

## Funktionale Anforderungen

- CSV-Import von Transaktionen
- Anzeige des Gesamtportfolios
- Gewinn/Verlust pro Aktie oder ETF
- Dividendenuebersicht
- Monatsauswertung
- Diagramme in Streamlit

## Sicherheitsanforderungen

- Keine Zugangsdaten im Code speichern
- `.env` fuer lokale Konfiguration verwenden
- `.gitignore` fuer CSV-Dateien, `.env`, lokale Datenbanken und andere sensible Dateien pflegen
- Finanzdaten lokal speichern, idealerweise verschluesselt oder zumindest ausserhalb des Repositories
- Eingabedaten beim Import validieren
- Fehlerausgaben ohne sensible Daten anzeigen
- Keine Finanzdaten in Logs schreiben

## Architektur

```text
Trade Republic CSV
        |
        v
CSV Import Modul
        |
        v
Datenvalidierung
        |
        v
Lokale Datenbank / Pandas DataFrame
        |
        v
Analyse-Modul
        |
        v
Streamlit Dashboard
```

## Geplanter Tech-Stack

- Python
- Pandas fuer Datenaufbereitung und Analyse
- Streamlit fuer das lokale Dashboard
- Lokale CSV-/Excel-Dateien als Importquelle
- Optional: SQLite fuer lokale Zwischenspeicherung

## CI/CD

Das Repository ist fuer GitHub Actions vorbereitet. Die CI-Pipeline laeuft bei Pushes und Pull Requests gegen `main` oder `master` und prueft:

- Installation der Python-Abhaengigkeiten
- Code-Formatierung mit Ruff
- Linting mit Ruff
- Tests mit Pytest
- Security-Scan des `app`-Ordners mit Bandit

Die Pipeline liegt unter `.github/workflows/ci.yml`.

Ein echtes Deployment ist noch nicht aktiviert, weil das Projekt aktuell als lokales Dashboard geplant ist. Sobald ein Ziel feststeht, kann eine CD-Stufe ergaenzt werden, zum Beispiel fuer Streamlit Cloud, einen eigenen Server oder ein Docker-basiertes Deployment.

## Lokale Entwicklung

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
ruff check .
ruff format .
bandit -r app
```

## Projektstatus

Das Projekt befindet sich in der fruehen Planungs- und Aufbauphase. Der erste sichere Meilenstein ist ein lokaler CSV-Import mit validierten Beispieldaten und einer einfachen Streamlit-Ansicht.
