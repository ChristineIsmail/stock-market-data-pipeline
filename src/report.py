
import logging
import sqlite3
from pathlib import Path

import pandas as pd

from src.database import DB_PATH


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

SQL_PATH = BASE_DIR / "sql" / "analytics.sql"
REPORTS_DIR = BASE_DIR / "reports"


# Names of the CSV reports to generate
REPORT_NAMES = [
    "latest_stock_prices",
    "total_stock_returns",
    "daily_return_statistics",
    "top_trading_volumes",
    "duplicate_check",
    "moving_average_7d"
]


def generate_reports(
    db_path=DB_PATH,
    sql_path=SQL_PATH,
    reports_dir=REPORTS_DIR
):
    """
    Execute SQL analytics queries and save
    their results as CSV reports.
    """

    db_path = Path(db_path)
    sql_path = Path(sql_path)
    reports_dir = Path(reports_dir)

    # Check that required files exist
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}"
        )

    if not sql_path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_path}"
        )

    # Read SQL queries
    sql_content = sql_path.read_text(
        encoding="utf-8"
    )

    queries = [
        statement.strip()
        for statement in sql_content.split(";")
        if statement.strip()
    ]

    if len(queries) != len(REPORT_NAMES):
        raise ValueError(
            f"Expected {len(REPORT_NAMES)} SQL queries, "
            f"but found {len(queries)}"
        )

    # Create reports directory if necessary
    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(db_path)

    generated_reports = []

    try:

        for name, query in zip(
            REPORT_NAMES,
            queries
        ):

            logger.info(
                "Generating report: %s",
                name
            )

            # Execute SQL query and load results
            df = pd.read_sql_query(
                query,
                connection
            )

            # Save results as CSV
            report_path = reports_dir / f"{name}.csv"

            df.to_csv(
                report_path,
                index=False
            )

            generated_reports.append(
                report_path
            )

            logger.info(
                "Saved %s (%s rows)",
                report_path.name,
                len(df)
            )

    finally:
        connection.close()

    logger.info(
        "Successfully generated %s reports",
        len(generated_reports)
    )

    return generated_reports
