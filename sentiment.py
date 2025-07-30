import tweepy
from textblob import TextBlob
import os
from dotenv import load_dotenv

# 📦 Load environment variables
load_dotenv()
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# ✅ Validate token
if not bearer_token:
    raise ValueError("❌ Bearer token not found in .env")

# ✅ Initialize Twitter client
client = tweepy.Client(bearer_token=bearer_token)

def fetch_and_analyze_sentiment(query, max_results=50):
    """
    Search for recent tweets and analyze sentiment (positive/neutral/negative)
    using TextBlob's polarity scoring.
    """
    try:
        print(f"🔍 Searching for tweets about: {query}")
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["text", "lang"]
        )

        sentiments = {"positive": 0, "neutral": 0, "negative": 0}

        if response.data:
            for tweet in response.data:
                if tweet.lang != "en":
                    continue
                text = tweet.text
                polarity = TextBlob(text).sentiment.polarity
                if polarity > 0.1:
                    sentiments["positive"] += 1
                elif polarity < -0.1:
                    sentiments["negative"] += 1
                else:
                    sentiments["neutral"] += 1
            return sentiments, None
        else:
            return None, "No tweets found for sentiment analysis"

    except tweepy.TweepyException as api_err:
        return None, f"Tweepy API error: {str(api_err)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
