import requests
import pandas as pd
from datetime import datetime
from prophet import Prophet

def get_tvl_history(protocol_slug, days=90):
    """Fetches historical TVL data for a protocol from DeFiLlama."""
    try:
        url = f"https://api.llama.fi/protocol/{protocol_slug}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "tvl" not in data or not isinstance(data["tvl"], list):
            return None, "No TVL data available"

        df = pd.DataFrame(data["tvl"])
        df = df.dropna(subset=["totalLiquidityUSD"])
        df = df.rename(columns={"date": "ds", "totalLiquidityUSD": "y"})
        df["ds"] = pd.to_datetime(df["ds"], unit="s")
        df = df.sort_values("ds").tail(days)
        return df, None

    except Exception as e:
        return None, str(e)

def forecast_tvl(df, periods=5):
    """Uses Facebook Prophet to forecast TVL for future days."""
    try:
        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]], None
    except Exception as e:
        return None, str(e)
