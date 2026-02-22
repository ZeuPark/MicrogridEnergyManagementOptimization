#!/usr/bin/env python
"""CLI script to ingest and preprocess microgrid data.

Usage:
    python scripts/ingest_data.py --config config/config.yaml

This script:
1. Loads configuration
2. Generates synthetic data (or fetches from API)
3. Saves processed data to data/processed/
"""

import argparse
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import load_config
from src.data.loaders import generate_synthetic_data, save_processed_data
from src.utils.logger import setup_logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest and preprocess microgrid data"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Override output directory",
    )
    args = parser.parse_args()

    # Load configuration
    settings = load_config(args.config)
    logger = setup_logger("microgrid", settings.log_level)

    logger.info("Starting data ingestion")
    logger.info(f"Region: {settings.region}")
    logger.info(f"Date range: {settings.start_date} to {settings.end_date}")

    # Generate synthetic data
    logger.info("Generating synthetic data...")
    df = generate_synthetic_data(
        start_date=settings.start_date,
        end_date=settings.end_date,
        resolution_minutes=settings.resolution_minutes,
        solar_capacity_kw=settings.solar_capacity_kw,
        timezone=settings.timezone,
    )

    # Save to processed directory
    output_dir = Path(args.output) if args.output else settings.results_dir
    output_path = output_dir / "microgrid_data.csv"
    save_processed_data(df, output_path)

    logger.info(f"Saved {len(df)} records to {output_path}")
    logger.info("Data ingestion complete")

    # Print summary
    print("\n=== Data Summary ===")
    print(f"Time range: {df.index.min()} to {df.index.max()}")
    print(f"Records: {len(df)}")
    print(f"Resolution: {settings.resolution_minutes} minutes")
    print("\nColumn statistics:")
    print(df.describe().round(3))


if __name__ == "__main__":
    main()
