-- summarize sentiment by ticker and date
SELECT
    ticker,
    DATE(ingested_at) as date,
    COUNT(*) as total_articles,
    COUNTIF(sentiment = 'positive') as positive_count,
    COUNTIF(sentiment = 'negative') as negative_count,
    COUNTIF(sentiment = 'neutral') as neutral_count,
    ROUND(COUNTIF(sentiment = 'positive') / COUNT(*) * 100, 2) as positive_pct
FROM
    `financial-sentiment-pipeline.sentiment_data.raw_sentiment`
GROUP BY
    ticker, date
ORDER BY
    date DESC, total_articles DESC