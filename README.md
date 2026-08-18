# Trade-Republic-Dashboard

A local finance dashboard that imports, analyzes, and clearly visualizes Trade Republic data.

## Goal and Requirements

The goal of the project is a locally running dashboard for evaluating personal financial data from Trade Republic. The focus is on secure, traceable importing of export files and clear presentation of portfolio, transactions, and analyses.

### Functional Requirements

- Users can upload local Trade Republic export files (CSV and Excel).
- The app validates imported data and displays clear error messages.
- The app displays portfolio overviews, transaction lists, dividends, allocation, and metrics.
- The app calculates and displays total costs, fees, date range, and currencies of the data.
- Visualization occurs locally in Streamlit without external services.
- Extensions such as new import formats or additional analyses should be easy to add.

### Out of Scope

- No Trade Republic login automation or storage of access credentials.
- No access to unofficial APIs or automatic portfolio queries.
- No currency conversion with external exchange rates or exchange rate-based third-party data.
- No usage tracking or telemetry features outside of direct dashboard functionality.

## Data Source

Local export files should initially be used as the data source:

- CSV export from Trade Republic
- Excel export from Trade Republic, if available

Not part of the initial scope are:

- Login scraping
- Unofficial APIs
- Storage of access credentials
- Automatic access to the portfolio

This approach reduces security risks and avoids handling sensitive login data.

## Threat Model

| Question                | Answer                                                                 |
| ----------------------- | ---------------------------------------------------------------------- |
| What data is sensitive? | Securities, transactions, IBAN, name and other personal financial data |
| Who could attack?       | Malware, other users on the laptop, or accidental GitHub leaks         |
| What must never happen? | Financial data or access credentials end up on GitHub                  |
| Where are data stored?  | Locally on your own computer                                           |
| Who has access?         | Only the local user                                                    |

## Architecture

```text
Trade Republic CSV/Excel
        |
        v
Import Module
        |
        v
Data Validation
        |
        v
Pandas DataFrame / local storage
        |
        v
Analysis Module
        |
        v
Streamlit Dashboard
```

## Planned Tech Stack

- Python
- Pandas for data processing and analysis
- Streamlit for the local dashboard
- Yfinance for financial data
- Local CSV/Excel files as import source
- Optional: SQLite for local caching

## CI/CD

The repository is prepared for GitHub Actions. The CI pipeline runs on pushes and pull requests against `main` or `master` and checks:

- Installation of Python dependencies
- Code formatting with Ruff
- Linting with Ruff
- Tests with Pytest
- Security scan of the `app` folder with Bandit

The pipeline is located at `.github/workflows/ci.yml`.

A real deployment is not yet activated because the project is currently planned as a local dashboard. Once a goal is set, a CD stage can be added, for example for Streamlit Cloud, your own server, or Docker-based deployment.

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
ruff check .
ruff format .
bandit -r app
```

## Project Status

The project is in the early planning and development phase. The first secure milestone is a local CSV/Excel import with validated sample data and a simple Streamlit view.
