
# Scraping Sandbox — Automated Product Data Pipeline

An automated ETL (Extract, Transform, Load) pipeline that collects product data from a JavaScript-rendered website, cleans and processes the dataset, stores the results in SQLite, and automates the complete workflow using Apache Airflow and Docker.

**Source Website:** https://scrapingsandbox.com/infinite-scroll

**GitHub Repository:** https://github.com/kundyzzz/Final_Data_Pipeline

## 1. Project Overview

The goal of this project is to develop an automated data pipeline that extracts structured product information from a dynamic website and stores the cleaned data in a relational database.

The project demonstrates:

- Dynamic web scraping using Playwright.
- Data cleaning and preprocessing with Pandas.
- Structured data storage using SQLite.
- Workflow automation with Apache Airflow.
- Containerized execution using Docker.
- Automated testing with pytest.
- Exploratory Data Analysis (EDA) using Pandas, NumPy, and Matplotlib.

The pipeline processes product data from the Scraping Sandbox website, which uses JavaScript and infinite scrolling to display product information.

## 2. Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Main programming language |
| Playwright | Dynamic web scraping |
| Pandas | Data cleaning and preprocessing |
| SQLite3 | Database storage |
| Apache Airflow | Workflow scheduling and orchestration |
| Docker | Containerization |
| Docker Compose | Container configuration |
| pytest | Automated testing |
| NumPy | Numerical analysis |
| Matplotlib | Data visualization |
| Git & GitHub | Version control |

## 3. Pipeline Architecture

The ETL pipeline consists of three main stages.

```text
Dynamic Website
      |
      v
+-----------------------+
| 1. DATA EXTRACTION    |
| Playwright Scraper    |
| src/scraper.py        |
+-----------------------+
      |
      v
   data/raw.csv
      |
      v
+-----------------------+
| 2. DATA CLEANING      |
| Pandas Cleaner        |
| src/cleaner.py        |
+-----------------------+
      |
      v
 data/cleaned.csv
      |
      v
+-----------------------+
| 3. DATA LOADING       |
| SQLite Loader         |
| src/loader.py         |
+-----------------------+
      |
      v
  data/output.db
      |
      v
   products table
```

Apache Airflow orchestrates the complete process:

```text
scrape >> clean >> load
```

The workflow runs in the following order:

1. Scrape product information from the website.
2. Clean and validate the collected records.
3. Load the cleaned dataset into SQLite.

The DAG is scheduled to run daily.

## 4. Data Source

**Website:** Scraping Sandbox

**URL:** https://scrapingsandbox.com/infinite-scroll

The website contains dynamically rendered product cards and uses infinite scrolling.

Traditional HTTP requests may not retrieve all products because additional content is loaded through JavaScript.

Playwright is used to:

- Open the website in a browser.
- Wait for dynamic content.
- Scroll through the product listing.
- Extract product information.
- Save structured records into CSV.

### Extracted Fields

| Field | Description |
|-------|-------------|
| sku | Unique product identifier |
| name | Product name |
| brand | Product brand |
| category | Product category |
| price | Current product price |
| original_price | Original product price |
| rating | Product rating |
| availability | Product availability |
| source_url | Source page URL |
| scraped_at | Data extraction timestamp |

## 5. Data Extraction

The scraper is implemented in:

`src/scraper.py`

It uses Playwright to interact with the dynamic website.

### Main Operations

1. Launch the Chromium browser.
2. Navigate to the source website.
3. Wait for product elements to load.
4. Scroll to load additional products.
5. Extract structured product information.
6. Save the collected data to `data/raw.csv`.

### Run the Scraper

```powershell
python -m src.scraper --output data/raw.csv
```

Expected output:

`data/raw.csv`

The corrected scraper successfully extracted 500 distinct product records during local testing.

## 6. Data Cleaning and Preprocessing

The cleaning module is implemented in:

`src/cleaner.py`

It uses Pandas to transform raw data into a consistent dataset.

### Cleaning Operations

- Remove duplicate records.
- Handle missing values.
- Normalize text fields.
- Convert numeric columns to appropriate types.
- Validate product identifiers.
- Check data consistency.
- Prepare records for SQLite.

### Run the Cleaner

```powershell
python -m src.cleaner --input data/raw.csv --output data/cleaned.csv
```

Expected output:

`data/cleaned.csv`

The corrected local test produced 500 cleaned product records.

## 7. SQLite Database

The cleaned dataset is stored in a SQLite database.

**Database:** `data/output.db`

**Table:** `products`

The table creation script is located at:

`sql/create_tables.sql`

The database stores the cleaned product information and loading timestamps.

### Database Loading

The loader is implemented in:

`src/loader.py`

Run:

```powershell
python -m src.loader --input data/cleaned.csv --db data/output.db
```

### Duplicate Prevention

The loader uses an UPSERT operation:

```sql
ON CONFLICT(sku) DO UPDATE
```

This allows the pipeline to update existing product records instead of inserting duplicate SKUs.

### Database Verification

Example SQL query:

```sql
SELECT COUNT(*) FROM products;
```

Verified local result:

```text
500
```

Additional data quality checks:

```sql
SELECT COUNT(*)
FROM products
WHERE brand = 'Unknown';
```

Result:

```text
0
```

```sql
SELECT COUNT(*)
FROM products
WHERE rating IS NULL;
```

Result:

```text
0
```

## 8. Apache Airflow Automation

Apache Airflow is used to automate the complete ETL workflow.

**DAG File:** `dags/airflow_dag.py`

**DAG ID:** `scrapingsandbox_daily_pipeline`

### DAG Configuration

| Parameter | Value |
|-----------|-------|
| Schedule | @daily |
| Catchup | False |
| Retries | 2 |
| Tasks | scrape, clean, load |

### Workflow

```text
scrape
   |
   v
clean
   |
   v
load
```

Each task starts only after the previous task completes successfully.

Airflow provides:

- Automated scheduling.
- Task dependency management.
- Execution logs.
- Retry handling.
- Workflow monitoring.
- Task status visualization.

The pipeline was successfully executed through Airflow, with all three tasks completing successfully.

## 9. Docker Configuration

Docker is used to provide a consistent environment for Apache Airflow and the ETL pipeline.

Main configuration files:

- `Dockerfile`
- `docker-compose.yaml`

### Build the Docker Image

```powershell
docker compose build
```

### Start the Containers

```powershell
docker compose up -d
```

### Check Container Status

```powershell
docker compose ps
```

### Open Apache Airflow

Open the following address in your browser:

http://localhost:8080

Use the local Airflow administrator credentials generated during setup.

### Run the Pipeline

1. Open the Airflow web interface.
2. Find `scrapingsandbox_daily_pipeline`.
3. Enable the DAG if necessary.
4. Trigger a DAG run.
5. Monitor the execution of all three tasks.
6. Verify successful completion.

### View Logs

```powershell
docker compose logs airflow --tail 100
```

### Stop Containers

```powershell
docker compose down
```

### Airflow Metadata Permission Troubleshooting

If Airflow cannot write to `/opt/airflow/metadata`, the following commands can fix permissions in the local Docker environment:

```powershell
docker compose down
docker compose run --rm --user root --no-deps --entrypoint sh airflow -c "chown -R 50000:0 /opt/airflow/metadata && chmod -R u+rwX /opt/airflow/metadata"
docker compose up -d
docker compose exec airflow airflow db check
```

This workaround is only needed if the permissions error occurs.

## 10. Local Installation

### Requirements

- Python 3.11 recommended
- Docker Desktop
- Git
- Internet connection

### Create a Virtual Environment

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Install Playwright Browser

```powershell
python -m playwright install chromium
```

### Execute the Pipeline

```powershell
python -m src.scraper --output data/raw.csv
python -m src.cleaner --input data/raw.csv --output data/cleaned.csv
python -m src.loader --input data/cleaned.csv --db data/output.db
```

## 11. Automated Testing

The project includes automated tests implemented with pytest.

Test files:

- `tests/test_scraper_parser.py`
- `tests/test_cleaner.py`
- `tests/test_loader.py`

### Run Tests

```powershell
python -m pytest -q
```

Verified result:

```text
4 passed
```

The tests help verify:

- Product data parsing.
- Data cleaning behavior.
- Database loading.
- Handling of expected input records.

## 12. Exploratory Data Analysis (EDA)

An additional EDA module was implemented to explore the cleaned dataset and create visualizations for the project report and presentation.

**File:** `src/analysis.py`

The EDA module is independent of the main ETL pipeline.

It reads:

`data/cleaned.csv`

It does not modify the scraper, cleaner, loader, SQLite database, or Airflow DAG.

### Run EDA

```powershell
python -m src.analysis
```

### Dataset Overview

The analysis calculates:

- Total number of products.
- Number of unique SKUs.
- Number of brands.
- Number of product categories.
- Average product price.
- Median product price.
- Minimum and maximum prices.
- Average product rating.
- Percentage of available products.

### Descriptive Statistics

The script also generates descriptive statistics for numeric columns, including:

- Count
- Mean
- Standard deviation
- Minimum
- Quartiles
- Maximum

### Grouped Analysis

Products are grouped by category to calculate:

- Product count.
- Average price.
- Median price.
- Average rating.
- Number of available products.
- Availability percentage.

### Visualization 1 — Product Distribution by Category

**File:** `figures/01_products_by_category.png`

**Type:** Horizontal Bar Chart

Shows the number of products in each category.

This visualization helps identify which product categories contain the largest and smallest numbers of records.

### Visualization 2 — Product Price Distribution

**File:** `figures/02_price_distribution.png`

**Type:** Histogram

Shows the distribution of product prices.

The visualization includes:

- Price intervals.
- Product counts.
- Mean price.
- Median price.

This helps explain the general price distribution of the dataset.

### Visualization 3 — Average Price by Category

**File:** `figures/03_average_price_by_category.png`

**Type:** Lollipop Chart

Compares average product prices across categories.

This visualization helps identify categories with relatively higher or lower average prices.

### Generated Analytical Tables

The EDA module creates two CSV files.

**1. Dataset Overview**

`results/dataset_overview.csv`

Contains overall dataset statistics.

**2. Category Summary**

`results/category_summary.csv`

Contains category-level aggregations.

These tables can be used in the final report.

## 13. Project Structure

```text
Final_Data_Pipeline/
|
|-- src/
|   |-- scraper.py
|   |-- cleaner.py
|   |-- loader.py
|   |-- analysis.py
|
|-- dags/
|   |-- airflow_dag.py
|
|-- sql/
|   |-- create_tables.sql
|
|-- tests/
|   |-- test_scraper_parser.py
|   |-- test_cleaner.py
|   |-- test_loader.py
|
|-- data/
|   |-- raw.csv
|   |-- cleaned.csv
|   |-- output.db
|
|-- figures/
|   |-- 01_products_by_category.png
|   |-- 02_price_distribution.png
|   |-- 03_average_price_by_category.png
|
|-- results/
|   |-- dataset_overview.csv
|   |-- category_summary.csv
|
|-- docs/
|   |-- RESULTS_TO_FILL.md
|
|-- Dockerfile
|-- docker-compose.yaml
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
|-- TEAM.md
```

Generated data files and local databases are excluded from Git when configured in `.gitignore`.

## 14. Verified Project Results

The following results were verified during local testing on November 23, 2026.

| Metric | Result |
|--------|--------|
| Scraped products | 500 |
| Cleaned products | 500 |
| Products stored in SQLite | 500 |
| Unknown brands | 0 |
| Missing ratings | 0 |
| Automated tests | 4 passed |
| Airflow tasks | 3 successful |
| EDA visualizations | 3 implemented |
| EDA summary tables | 2 implemented |

The project demonstrates a working end-to-end ETL pipeline.

The main workflow successfully connects dynamic web scraping, data preprocessing, database storage, and automated orchestration.

## 15. Challenges and Solutions

### Dynamic Website Content

**Challenge:** The source website loads products dynamically using JavaScript and infinite scrolling.

**Solution:** Playwright was used to render the page, scroll through product listings, and extract product information.

### Data Quality

**Challenge:** Scraped records may contain missing values, inconsistent formats, or duplicates.

**Solution:** Pandas preprocessing and validation were implemented before database loading.

### Duplicate Database Records

**Challenge:** Repeated pipeline executions could insert duplicate products.

**Solution:** The SQLite loader uses SKU-based UPSERT operations.

### Workflow Integration

**Challenge:** Scraping, cleaning, and loading must execute in the correct order.

**Solution:** Apache Airflow manages dependencies, scheduling, retries, and logs.

### Container Configuration

**Challenge:** Local Docker environments may encounter Airflow metadata permission issues.

**Solution:** Container permissions were adjusted during setup when necessary.

## 16. Project Limitations

- The source website may change its structure.
- The scraper may require updates if HTML elements change.
- The pipeline depends on website availability.
- SQLite is suitable for this educational project but may not be appropriate for large production workloads.
- Airflow standalone mode is intended for local development and demonstration.
- The dataset comes from a scraping sandbox and should not be interpreted as representative of a real commercial market.

## 17. Conclusion

This project demonstrates the implementation of a complete automated data pipeline using Python, Playwright, Pandas, SQLite, Apache Airflow, and Docker.

The system successfully extracts structured product information from a dynamic website, cleans and validates the records, stores the results in SQLite, and automates the complete ETL workflow.

Automated testing and additional exploratory data analysis support data quality verification and result interpretation.

The project provides practical experience in web scraping, data engineering, workflow orchestration, database management, testing, and data visualization.

## 18. Team

The project was developed by a four-member team.

For individual responsibilities, collaboration workflow, and presentation roles, see [TEAM.md](TEAM.md).

## 19. Security Notes

Do not commit or publish:

- `.env` files containing secrets.
- Airflow administrator passwords.
- `standalone_admin_password.txt`.
- Local Airflow metadata.
- Virtual environments.
- Generated SQLite databases.
- Sensitive configuration files.

Review `.gitignore` before pushing changes to GitHub.
