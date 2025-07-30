import os
import tweepy
from textblob import TextBlob
from dotenv import load_dotenv

# Load .env and extract the bearer token
load_dotenv()
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# ✅ DEBUG: Check token loading
if not bearer_token:
    print("❌ Bearer token not loaded from .env. Check the file and path.")
    exit(1)
else:
    print("✅ Bearer token loaded. Starting Twitter client...")

# Initialize Twitter Client
try:
    client = tweepy.Client(bearer_token=bearer_token)
    print("✅ Twitter client initialized.")
except Exception as e:
    print(f"❌ Failed to initialize Twitter client: {e}")
    exit(1)

# Function to fetch tweets and analyze sentiment
def fetch_and_analyze_sentiment(query="bitcoin", max_results=20):
    print(f"🔍 Searching for tweets about: {query}")
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["text", "lang"]
        )

        tweets = response.data
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}

        if not tweets:
            print("⚠️ No tweets found.")
            return None, "No tweets found"

        for tweet in tweets:
            print("📝 Tweet:", tweet.text)
            if tweet.lang != "en":
                continue
            blob = TextBlob(tweet.text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                sentiments["positive"] += 1
            elif polarity < -0.1:
                sentiments["negative"] += 1
            else:
                sentiments["neutral"] += 1

        print("✅ Sentiment Analysis Complete")
        print("📊 Sentiments:", sentiments)
        return sentiments, None

    except Exception as e:
        print(f"❌ Twitter API Error: {e}")
        return None, str(e)

# Run test
if __name__ == "__main__":
    fetch_and_analyze_sentiment("ethereum")
