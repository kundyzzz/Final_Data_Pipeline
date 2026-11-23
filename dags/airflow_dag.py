"""Scheduled daily scrape -> clean -> load pipeline."""
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator

ROOT=Path('/opt/airflow/project')
sys.path.insert(0,str(ROOT))
from src.scraper import scrape_products
from src.cleaner import clean_products
from src.loader import load_products

DATA=ROOT/'data'
DEFAULT_ARGS={'owner':'team4','retries':2,'retry_delay':timedelta(minutes=3)}

def do_scrape():
    n=scrape_products(str(DATA/'raw.csv'),min_records=200)
    logging.info('Scrape completed with %s records',n)

def do_clean():
    n=clean_products(str(DATA/'raw.csv'),str(DATA/'cleaned.csv'),min_records=200)
    logging.info('Clean completed with %s records',n)

def do_load():
    n=load_products(str(DATA/'cleaned.csv'),str(DATA/'output.db'),min_records=200)
    logging.info('SQLite completed with %s records',n)

with DAG(
    dag_id='scrapingsandbox_daily_pipeline',
    description='JS infinite scroll -> pandas -> SQLite',
    start_date=datetime(2026,11,1),
    schedule_interval='@daily',
    catchup=False,
    default_args=DEFAULT_ARGS,
    max_active_runs=1,
    tags=['final-project','scraping'],
) as dag:
    scrape=PythonOperator(task_id='scrape',python_callable=do_scrape)
    clean=PythonOperator(task_id='clean',python_callable=do_clean)
    load=PythonOperator(task_id='load',python_callable=do_load)
    scrape >> clean >> load
