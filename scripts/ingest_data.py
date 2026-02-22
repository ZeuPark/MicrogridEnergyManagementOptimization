#!/usr/bin/env python
"""CLI script to ingest and preprocess microgrid data.

Usage:
    # Fetch real NEM data (default)
    python scripts/ingest_data.py --config config/config.yaml

    # Use synthetic data for testing
    python scripts/ingest_data.py --config config/config.yaml --synthetic

This script:
1. Loads configuration
2. Fetches real NEM data from OpenElectricity API (or generates synthetic)
3. Saves processed data to data/processed/
"""

import argparse
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import load_config
from src.data.loaders import generate_synthetic_data, save_processed_data
from src.data.nem_api import fetch_nem_data, resample_to_hourly
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
        "--synthetic",
        action="store_true",
        help="Use synthetic data instead of real NEM data",
    )
    parser.add_argument(
        "--period",
        type=str,
        default="7d",
        choices=["7d", "30d", "1y"],
        help="Time period for real data (7d, 30d, 1y)",
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

    if args.synthetic:
        # Generate synthetic data
        logger.info("Generating synthetic data...")
        logger.info(f"Date range: {settings.start_date} to {settings.end_date}")
        df = generate_synthetic_data(
            start_date=settings.start_date,
            end_date=settings.end_date,
            resolution_minutes=settings.resolution_minutes,
            solar_capacity_kw=settings.solar_capacity_kw,
            timezone=settings.timezone,
        )
    else:
        # Fetch real NEM data
        logger.info(f"Fetching real NEM data (period: {args.period})...")
        df = fetch_nem_data(region=settings.region, period=args.period)

        # Resample to hourly if needed
        if settings.resolution_minutes == 60:
            logger.info("Resampling to hourly resolution...")
            df = resample_to_hourly(df)

        logger.info(f"Fetched {len(df)} records from OpenElectricity API")

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
    print(f"Data source: {'Synthetic' if args.synthetic else 'Real NEM (OpenElectricity API)'}")
    print("\nColumn statistics:")
    print(df.describe().round(3))

    # Show price volatility metrics
    if "price" in df.columns:
        print("\n=== Price Volatility ===")
        print(f"Min price: ${df['price'].min():.4f}/kWh (${df['price'].min()*1000:.2f}/MWh)")
        print(f"Max price: ${df['price'].max():.4f}/kWh (${df['price'].max()*1000:.2f}/MWh)")
        print(f"Price ratio (max/min): {df['price'].max()/df['price'].min():.1f}x")
        print(f"Std dev: ${df['price'].std():.4f}/kWh")


if __name__ == "__main__":
    main()
