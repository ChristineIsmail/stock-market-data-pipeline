
import logging

from src.extract import extract_stock_data
from src.transform import transform_stock_data
from src.database import (
    create_tables,
    load_stock_data,
    get_record_count
)
from src.report import generate_reports


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(levelname)s - "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


def run_pipeline():

    logger.info("Starting stock market pipeline")

    try:

        # STEP 1: EXTRACT
        raw_data = extract_stock_data()

        if raw_data.empty:
            raise ValueError(
                "No stock data extracted"
            )

        logger.info(
            "Extracted %s records",
            len(raw_data)
        )

        # STEP 2: TRANSFORM
        clean_data = transform_stock_data(
            raw_data
        )

        if clean_data.empty:
            raise ValueError(
                "No valid records after transformation"
            )

        logger.info(
            "Transformed %s records",
            len(clean_data)
        )

        # STEP 3: CREATE DATABASE TABLES
        create_tables()

        # STEP 4: LOAD DATA INTO DATABASE
        load_stock_data(clean_data)

        # STEP 5: VALIDATE DATABASE
        total_records = get_record_count()

        logger.info(
            "Total database records: %s",
            total_records
        )

        # STEP 6: GENERATE REPORTS
        generated_reports = generate_reports()

        logger.info(
            "Generated %s reports",
            len(generated_reports)
        )

        logger.info(
            "Pipeline completed successfully"
        )

        return {
            "status": "success",
            "extracted": len(raw_data),
            "transformed": len(clean_data),
            "database_records": total_records,
            "reports_generated": len(generated_reports)
        }

    except Exception:

        logger.exception(
            "Stock market pipeline failed"
        )

        raise
