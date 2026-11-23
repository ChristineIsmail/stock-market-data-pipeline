
import pandas as pd
import pytest

from src.transform import transform_stock_data


@pytest.fixture
def sample_data():
    """Create sample stock market data for testing."""

    return pd.DataFrame({
        "date": [
            "2026-01-01",
            "2026-01-02",
            "2026-01-02"
        ],
        "ticker": [
            "AAPL",
            "AAPL",
            "AAPL"
        ],
        "Open": [100, 105, 105],
        "High": [110, 115, 115],
        "Low": [95, 100, 100],
        "Close": [105, 110, 110],
        "Volume": [1000, 1200, 1200],
        "adj_close": [105, 110, 110]
    })


# TEST 1: Duplicate records are removed
def test_duplicates_are_removed(sample_data):

    result = transform_stock_data(sample_data)

    assert len(result) == 2

    assert not result.duplicated(
        ["ticker", "date"]
    ).any()


# TEST 2: Daily returns are calculated correctly
def test_daily_return_calculation(sample_data):

    result = transform_stock_data(sample_data)

    second_day = result.iloc[1]

    assert round(
        second_day["daily_return_pct"], 2
    ) == 4.76


# TEST 3: Missing required columns raise an error
def test_missing_columns_raise_error():

    df = pd.DataFrame({
        "ticker": ["AAPL"]
    })

    with pytest.raises(ValueError, match="Missing columns"):
        transform_stock_data(df)


# TEST 4: Invalid prices are removed
def test_invalid_prices_are_removed(sample_data):

    sample_data.loc[0, "Close"] = -10

    result = transform_stock_data(sample_data)

    assert len(result) == 1

    assert (result["Close"] > 0).all()


# TEST 5: Records are sorted by date
def test_sorted_by_date(sample_data):

    result = transform_stock_data(sample_data)

    dates = result["date"].tolist()

    assert dates == sorted(dates)


# TEST 6: Missing values are removed
def test_missing_values_are_removed(sample_data):

    # Use only two rows with different dates
    data = sample_data.iloc[:2].copy()

    # Make the second row incomplete
    data.loc[1, "Volume"] = None

    result = transform_stock_data(data)

    # Only one valid row should remain
    assert len(result) == 1

    assert result["Volume"].notna().all()
