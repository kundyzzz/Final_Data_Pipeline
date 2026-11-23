
# Team — Final Data Pipeline

## Team Members and Responsibilities

| Team Member | Topic | Responsible Files |
|-------------|-------|-------------------|
| Qian | Data Extraction — Web Scraping with Playwright | `src/scraper.py`, `tests/test_scraper_parser.py` |
| Balnur | Data Cleaning and Preprocessing with Pandas | `src/cleaner.py`, `tests/test_cleaner.py` |
| Nurdaulet | Data Storage and Database Management with SQLite | `src/loader.py`, `sql/create_tables.sql`, `tests/test_loader.py` |
| Kundyz | Workflow Automation, Docker, Integration and Data Analysis | `dags/airflow_dag.py`, `Dockerfile`, `docker-compose.yaml`, `src/analysis.py`|

## GitHub Workflow

The project uses Git and GitHub for version control and collaboration.

| Branch | Responsible Member |
|--------|--------------------|
| `feature/scraper` | Qian |
| `feature/cleaning` | Balnur |
| `feature/database` | Nurdaulet |
| `feature/airflow` | Kundyz |

Each member is expected to contribute through their assigned branch and submit changes through Pull Requests.

Each member is responsible for understanding their implementation and how it connects to the complete ETL workflow.

