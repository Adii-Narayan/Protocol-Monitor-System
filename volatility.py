import yfinance as yf
from arch import arch_model
import pandas as pd

def forecast_volatility(symbol="ETH-USD", period="90d"):
    # Step 1: Fetch historical data
    data = yf.download(symbol, period=period, interval="1d")
    if data.empty:
        return None, "No price data available."

    returns = 100 * data["Close"].pct_change().dropna()

    # Step 2: Fit GARCH(1,1) model
    model = arch_model(returns, vol="GARCH", p=1, q=1)
    model_fit = model.fit(disp="off")

    # Step 3: Forecast volatility
    forecast = model_fit.forecast(horizon=5)
    future_vol = forecast.variance.values[-1]
    return future_vol, None
