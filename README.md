# Financial Sentiment Pipeline

An end-to-end data pipeline that fetches financial news headlines, analyzes sentiment using AI, stores results in BigQuery, and visualizes trends in a Looker Studio dashboard.

## Architecture

NewsAPI → Python (Groq AI) → BigQuery → dbt → Looker Studio

## Tech Stack

- **Python** — data ingestion and sentiment analysis
- **NewsAPI** — financial headline source
- **Groq AI (LLaMA)** — LLM-powered sentiment analysis
- **Google Cloud BigQuery** — cloud data warehouse
- **dbt** — data transformation and modeling
- **Apache Airflow** — pipeline orchestration (DAG)
- **Looker Studio** — dashboard and visualization

## Project Structure



## Setup

1. Clone the repo
2. Create a virtual environment and install dependencies:
pip install -r requirements.txt
3. Add your API keys to `.env`
4. Run the pipeline:
python ingestion/fetch_news.py
5. Run dbt transformation:
dbt run --project-dir transformation

## Dashboard

Live Looker Studio dashboard showing sentiment trends by ticker and date.