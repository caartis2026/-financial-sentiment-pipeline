from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
import sys
import os

# add the ingestion folder to the path so we can import fetch_news
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from fetch_news import run

# default arguments applied to all tasks
default_args = {
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# define the DAG
with DAG(
    "financial_sentiment_pipeline",
    default_args=default_args,
    description="Fetches financial headlines, analyzes sentiment, loads to BigQuery",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finance", "sentiment", "bigquery"],
) as dag:

    # single task that calls the run() function from fetch_news.py
    run_pipeline = PythonOperator(
        task_id="run_sentiment_pipeline",
        python_callable=run,
    )