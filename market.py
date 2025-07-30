import requests
import pandas as pd
import time

# 📈 Token Price from CoinGecko with retry + delay
def get_token_price(token_id="ethereum", retries=3):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return {
                "price": data[token_id]["usd"],
                "change_24h": data[token_id]["usd_24h_change"]
            }
        except Exception as e:
            print(f"❌ CoinGecko error (attempt {attempt}):", e)
            time.sleep(2 * attempt)  # Exponential backoff

    return {"price": None, "change_24h": None}

# 💧 TVL from DeFiLlama (using fallback-safe logic)
def get_tvl(protocol_slug):
    try:
        response = requests.get("https://api.llama.fi/protocols", timeout=5)
        response.raise_for_status()
        protocols = response.json()

        for p in protocols:
            if p.get("slug") == protocol_slug:
                return {
                    "latest": p.get("tvl"),
                    "change": p.get("change1d", 0)
                }
        print(f"⚠️ Protocol '{protocol_slug}' not found in DeFiLlama")
    except Exception as e:
        print("❌ DeFiLlama error:", e)

    return {"latest": None, "change": None}

# 📉 Token Price History with retry + delay
def get_token_price_history(token_id="ethereum", days=30, retries=3):
    for attempt in range(1, retries + 1):
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            prices = data.get("prices", [])  # [[timestamp, price], ...]
            if not prices:
                return None

            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df

        except Exception as e:
            print(f"❌ CoinGecko History Error (attempt {attempt}):", e)
            time.sleep(2 * attempt)

    return None
    