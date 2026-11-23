
import pandas as pd


REQUIRED_COLUMNS = [
    "date",
    "ticker",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "adj_close"
]


def transform_stock_data(df):

    df = df.copy()

    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Keep only required columns
    df = df[REQUIRED_COLUMNS]

    # Convert date to consistent format
    df["date"] = pd.to_datetime(
        df["date"],
        utc=True
    ).dt.strftime("%Y-%m-%d")

    # Remove duplicate stock/date records
    df = df.drop_duplicates(
        subset=["ticker", "date"],
        keep="last"
    )

    # Convert numeric fields
    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "adj_close"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Remove invalid records
    df = df.dropna(
        subset=[
            "ticker",
            "date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "adj_close"
        ]
    )

    # Validate prices and volume
    price_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "adj_close"
    ]

    for col in price_columns:
        df = df[df[col] > 0]

    df = df[df["Volume"] >= 0]

    # Check high and low consistency
    df = df[
        (df["High"] >= df["Low"]) &
        (df["High"] >= df["Open"]) &
        (df["High"] >= df["Close"]) &
        (df["Low"] <= df["Open"]) &
        (df["Low"] <= df["Close"])
    ]

    # Sort records
    df = df.sort_values(
        ["ticker", "date"]
    ).reset_index(drop=True)

    # Calculate daily percentage returns
    df["daily_return_pct"] = (
        df.groupby("ticker")["adj_close"]
        .pct_change() * 100
    )

    # Replace first-day NaN returns with NULL
    df["daily_return_pct"] = (
        df["daily_return_pct"].round(4)
    )

    return df
