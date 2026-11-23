
import sqlite3
import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "stock_market.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(db_path=DB_PATH):

    db_path = Path(db_path)

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(db_path)


def create_tables(db_path=DB_PATH):

    connection = get_connection(db_path)

    try:
        schema = SCHEMA_PATH.read_text(
            encoding="utf-8"
        )

        connection.executescript(schema)

        connection.commit()

    finally:
        connection.close()


def load_stock_data(
    df,
    db_path=DB_PATH
):

    if df.empty:
        raise ValueError("Cannot load empty data")

    connection = get_connection(db_path)

    try:

        records = []

        for row in df.itertuples(index=False):

            daily_return = row.daily_return_pct

            if pd.isna(daily_return):
                daily_return = None
            else:
                daily_return = float(daily_return)

            records.append((
                row.ticker,
                row.date,
                float(row.Open),
                float(row.High),
                float(row.Low),
                float(row.Close),
                float(row.adj_close),
                int(row.Volume),
                daily_return
            ))

        query = """
        INSERT INTO stock_prices (
            ticker,
            date,
            open,
            high,
            low,
            close,
            adj_close,
            volume,
            daily_return_pct
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(ticker, date)

        DO UPDATE SET

            open = excluded.open,
            high = excluded.high,
            low = excluded.low,
            close = excluded.close,
            adj_close = excluded.adj_close,
            volume = excluded.volume,
            daily_return_pct = excluded.daily_return_pct;
        """

        connection.executemany(
            query,
            records
        )

        connection.commit()

        logger.info(
            "Loaded %s records",
            len(records)
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_record_count(db_path=DB_PATH):

    connection = get_connection(db_path)

    try:
        cursor = connection.execute(
            "SELECT COUNT(*) FROM stock_prices"
        )

        return cursor.fetchone()[0]

    finally:
        connection.close()
