import requests
import openai
import pandas as pd

NEWS_API_KEY = "38ede88b65c442b5b27cd6ef6bedd6b9"

def get_events(symbol):
    # Gets economic events/earnings - extend as needed
    return [{"date":"2025-11-20","event":"Earnings","impact":"medium"}]

def get_headlines(symbol, count=5):
    url = f"https://newsapi.org/v2/everything?q={symbol}&language=en&pageSize={count}&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url)
        articles = r.json().get('articles', [])
        headlines = [a['title'] for a in articles]
        return headlines
    except Exception:
        return []

def sentiment_score(texts):
    results = []
    for txt in texts:
        response = openai.Completion.create(
            model="text-davinci-003", prompt=f"Is this news positive, negative, or neutral? Headline: {txt}", max_tokens=15
        )
        results.append(response.choices[0].text.strip())
    return results

def news_with_sentiment(symbol):
    headlines = get_headlines(symbol)
    sentiments = sentiment_score(headlines)
    return pd.DataFrame({'headline': headlines, 'sentiment': sentiments})

def event_driven_signal(symbol):
    events = get_events(symbol)
    # For demo: if positive event soon, return Buy
    for ev in events:
        if 'positive' in ev.get('impact',''):
            return 'Buy'
    return 'Hold'