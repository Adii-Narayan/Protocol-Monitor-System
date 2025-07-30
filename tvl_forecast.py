import pandas as pd
from prophet import Prophet

def forecast_tvl(df):
    """
    Forecasts Total Value Locked (TVL) using the Prophet library.

    Args:
        df (pd.DataFrame): A DataFrame with at least two columns:
                           'timestamp' (Unix timestamp in seconds) and
                           'tvl' (the TVL value).

    Returns:
        tuple: A tuple containing:
               - pd.DataFrame: A DataFrame with 'ds' (datetime) and 'yhat' (predicted TVL)
                               for the last 7 forecasted periods, or None if an error occurs.
               - str: An error message if an error occurs, otherwise None.
    """
    try:
        # ✅ Step 0: Basic validation of the input DataFrame
        if not isinstance(df, pd.DataFrame):
            return None, "Input is not a pandas DataFrame."
        if "timestamp" not in df.columns or "tvl" not in df.columns:
            return None, "Missing 'timestamp' or 'tvl' columns in the input DataFrame."
        if df.empty:
            return None, "Input DataFrame is empty."

        # ✅ Step 1: Prepare Data for Prophet
        # Rename columns to 'ds' (datestamp) and 'y' (value) as required by Prophet.
        prophet_df = df.rename(columns={"timestamp": "ds", "tvl": "y"})

        # Convert Unix timestamp (seconds) to datetime objects.
        # This is a crucial step for Prophet to interpret the time series correctly.
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"], unit="s")

        # Optional: Resample the data to a daily frequency and take the mean of 'tvl'
        # for each day. This helps in handling irregular timestamps or multiple
        # entries per day, providing a consistent daily series for Prophet.
        prophet_df = prophet_df.set_index("ds").resample("D").mean().reset_index()

        # Drop any rows that might have missing values after resampling (e.g., days
        # with no data).
        prophet_df = prophet_df.dropna()

        # Ensure there are enough data points for Prophet to fit a meaningful model.
        # Prophet generally requires at least a few data points to identify trends.
        if len(prophet_df) < 10:
            return None, "Not enough data points for forecasting. At least 10 data points are recommended."

        # ✅ Step 2: Initialize and Fit the Model
        # Initialize the Prophet model.
        # daily_seasonality and yearly_seasonality are set to False as per your original code.
        # Consider setting these to True if your data exhibits such patterns for better accuracy.
        model = Prophet(daily_seasonality=False, yearly_seasonality=False)

        # Fit the model to your historical TVL data.
        model.fit(prophet_df)

        # ✅ Step 3: Create future data
        # Create a DataFrame with future dates for which to make predictions.
        # Here, we are forecasting for the next 7 periods (days, due to resampling).
        future = model.make_future_dataframe(periods=7)

        # ✅ Step 4: Predict
        # Generate predictions for the future dates.
        forecast = model.predict(future)

        # ✅ Step 5: Return last 7 predictions
        # Extract the 'ds' (date) and 'yhat' (predicted value) columns
        # and return the last 7 predicted values.
        return forecast[["ds", "yhat"]].tail(7), None

    except Exception as e:
        # Catch any exceptions that occur during the process and return an error message.
        return None, f"Forecasting error: {str(e)}"
