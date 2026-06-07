from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()

# construct the BigQuery client
client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))

# set the table id in the format project.dataset.table
table_id = "financial-sentiment-pipeline.sentiment_data.raw_sentiment"

# define the schema — one field for each piece of data we are storing
schema = [
    bigquery.SchemaField("headline", "STRING"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("published_at", "STRING"),
    bigquery.SchemaField("sentiment", "STRING"),
    bigquery.SchemaField("ticker", "STRING"),
    bigquery.SchemaField("reason", "STRING"),
    bigquery.SchemaField("ingested_at", "STRING"),
]

# create the table object with the schema
table = bigquery.Table(table_id, schema=schema)

# actually create the table in BigQuery
table = client.create_table(table)

print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")