
import logging
import time

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]


def extract_stock_data(
    tickers=None,
    period="1y",
    retries=3
):
    """
    Extract historical daily stock prices
    from Yahoo Finance.
    """

    if tickers is None:
        tickers = TICKERS

    all_data = []

    for ticker in tickers:
        for attempt in range(1, retries + 1):
            try:
                logger.info("Extracting %s", ticker)

                stock = yf.Ticker(ticker)

                df = stock.history(
                    period=period,
                    interval="1d",
                    auto_adjust=False
                )

                if df.empty:
                    raise ValueError(
                        f"No data returned for {ticker}"
                    )

                df = df.reset_index()

                df["ticker"] = ticker

                df = df.rename(
                    columns={
                        "Date": "date",
                        "Adj Close": "adj_close"
                    }
                )

                all_data.append(df)

                logger.info(
                    "Extracted %s rows for %s",
                    len(df), ticker
                )

                break

            except Exception as error:
                logger.warning(
                    "Attempt %s failed for %s: %s",
                    attempt, ticker, error
                )

                if attempt == retries:
                    raise

                time.sleep(2 ** attempt)

    if not all_data:
        raise ValueError("No stock data extracted")

    result = pd.concat(
        all_data,
        ignore_index=True
    )

    return result
