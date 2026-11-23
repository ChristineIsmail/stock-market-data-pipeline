

import pandas as pd
import pytest

from src.database import (
    get_connection,
    create_tables,
    load_stock_data,
    get_record_count
)


@pytest.fixture
def sample_data():

    return pd.DataFrame({

        "ticker": ["AAPL", "AAPL"],

        "date": [
            "2026-01-01",
            "2026-01-02"
        ],

        "Open": [100, 105],
        "High": [110, 115],
        "Low": [95, 100],
        "Close": [105, 110],
        "adj_close": [105, 110],
        "Volume": [1000, 1200],
        "daily_return_pct": [None, 4.76]

    })


# TEST 1: Database connection works
def test_database_connection(tmp_path):

    db_path = tmp_path / "test.db"

    connection = get_connection(db_path)

    assert connection is not None

    connection.close()


# TEST 2: Database tables are created
def test_create_tables(tmp_path):

    db_path = tmp_path / "test.db"

    create_tables(db_path)

    connection = get_connection(db_path)

    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'stock_prices'
        """
    )

    result = cursor.fetchone()

    connection.close()

    assert result is not None


# TEST 3: Stock data loads correctly
def test_database_load(tmp_path, sample_data):

    db_path = tmp_path / "test.db"

    create_tables(db_path)

    load_stock_data(sample_data, db_path)

    assert get_record_count(db_path) == 2


# TEST 4: UPSERT prevents duplicate records
def test_database_upsert(tmp_path, sample_data):

    db_path = tmp_path / "test.db"

    create_tables(db_path)

    load_stock_data(sample_data, db_path)

    assert get_record_count(db_path) == 2

    # Load the same records again
    load_stock_data(sample_data, db_path)

    # Record count should remain unchanged
    assert get_record_count(db_path) == 2


# TEST 5: Empty data raises an error
def test_empty_data_raises_error(tmp_path):

    db_path = tmp_path / "test.db"

    create_tables(db_path)

    empty_df = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="Cannot load empty data"
    ):
        load_stock_data(empty_df, db_path)
