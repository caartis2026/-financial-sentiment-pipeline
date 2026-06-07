import os
import requests
from groq import Groq
from google.cloud import bigquery
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")

groq_client = Groq(api_key=GROQ_API_KEY)
bq_client = bigquery.Client(project=GCP_PROJECT_ID)

def fetch_headlines():
        # the NewsAPI endpoint we are sending our request to
    url = "https://newsapi.org/v2/everything"
    # the NewsAPI endpoint we are sending our request to

      # parameters we are sending with the request, like filling out a search form
    params = {
        "q": "stock market OR earnings OR Fed OR inflation",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY
    }
    # send the GET request to NewsAPI with our parameters and store the response
    response = requests.get(url, params=params)
    
    # convert the response to a python dictionary and pull out the articles list
    articles = response.json().get("articles", [])
    return articles

def analyze_sentiment(headline):
    
    # build the prompt we are sending to Groq, inserting the headline into the text
    prompt = f"""Analyze this financial news headline and respond in exactly this format:
SENTIMENT: [positive/negative/neutral]
TICKER: [stock ticker if mentioned, else NONE]
REASON: [one sentence explanation]

Headline: {headline}"""

    # send the prompt to Groq and store the response
    response = groq_client.chat.completions.create(
        # the model we are using to analyze the headline
        model="llama-3.1-8b-instant",
        # the messages we are sending — system sets the behavior, user sends the prompt
        messages=[
            {"role": "system", "content": "You are a financial news analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # pull the text response out of the response object and return it
    return response.choices[0].message.content


def parse_sentiment(raw):
    # split the raw text into individual lines and remove extra whitespace
    lines = raw.strip().split("\n")
    
    # create an empty dictionary to store the results
    result = {}
    
    # loop through each line in the response
    for line in lines:
        
        # if the line starts with SENTIMENT, grab everything after the colon
        if line.startswith("SENTIMENT:"):
            result["sentiment"] = line.split(":")[1].strip().lower()
        
        # if the line starts with TICKER, grab everything after the colon
        elif line.startswith("TICKER:"):
            result["ticker"] = line.split(":")[1].strip()
        
        # if the line starts with REASON, split on the first colon only
        # (reason text might contain colons so we use split(":", 1))
        elif line.startswith("REASON:"):
            result["reason"] = line.split(":", 1)[1].strip()
    
    # return the completed dictionary
    return result


def load_to_bigquery(rows):
    import json
    import tempfile

    # set the full table path
    table_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.raw_sentiment"

    # write rows to a temporary json file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
        temp_path = f.name

    # load the file into BigQuery using batch load
    with open(temp_path, "rb") as f:
        job = bq_client.load_table_from_file(
            f,
            table_id,
            job_config=bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition="WRITE_APPEND"
            )
        )
    job.result()
    print(f"Loaded {len(rows)} rows to BigQuery")

def run():
    #fetch the headlines from NewsAPI
    print("Fetchiing headlines...")
    articles=fetch_headlines()

    rows=[]

    #loop throgh article
    for article in articles:
        headline=article.get("title","")
        if not headline:
            continue
         # analyze the sentiment of each headline
        print(f"Analyzing: {headline[:60]}...")
        raw=analyze_sentiment(headline)
        parsed=parse_sentiment(raw)

        #build a row of dictinary to load into BigQuery

        rows.append({
            "headline": headline,
            "source": article.get("source", {}).get("name", ""),
            "published_at": article.get("publishedAt", ""),
            "sentiment": parsed.get("sentiment", "unknown"),
            "ticker": parsed.get("ticker", "NONE"),
            "reason": parsed.get("reason", ""),
            "ingested_at": datetime.now(timezone.utc).isoformat()
        })


         # load all rows to BigQuery
    load_to_bigquery(rows)


# run the pipeline
run()    
        
                       


# test_raw = """SENTIMENT: Positive
# TICKER: AAPL
# REASON: The stock has reacted favorably to Apple's strong earnings report."""

# print(parse_sentiment(test_raw))


# print(analyze_sentiment("Apple stock surges to record high after blowout earnings"))