#!/usr/bin/env python
"""CLI script to compute baseline costs (no battery).

Usage:
    python scripts/run_baseline.py --config config/config.yaml

This script:
1. Loads processed data
2. Computes baseline costs without battery
3. Outputs cost summary and metrics
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import load_config
from src.data.loaders import load_processed_data, generate_synthetic_data
from src.evaluation.baseline import compute_baseline_cost
from src.utils.logger import setup_logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute baseline costs without battery"
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
        help="Use synthetic data instead of loading from file",
    )
    args = parser.parse_args()

    # Load configuration
    settings = load_config(args.config)
    logger = setup_logger("microgrid", settings.log_level)

    logger.info("Computing baseline costs")

    # Load or generate data
    if args.synthetic:
        logger.info("Using synthetic data")
        df = generate_synthetic_data(
            start_date=settings.start_date,
            end_date=settings.end_date,
            resolution_minutes=settings.resolution_minutes,
            solar_capacity_kw=settings.solar_capacity_kw,
            timezone=settings.timezone,
        )
    else:
        logger.info(f"Loading data from {settings.results_dir}")
        df = load_processed_data(
            data_dir=settings.results_dir,
            start_date=settings.start_date,
            end_date=settings.end_date,
        )

    dt_hours = settings.resolution_minutes / 60.0

    # Compute baseline
    result = compute_baseline_cost(
        prices=df["price"].values,
        p_solar=df["solar"].values,
        p_load=df["load"].values,
        feed_in_tariff=settings.grid.feed_in_tariff,
        dt_hours=dt_hours,
    )

    # Output results
    print("\n" + "=" * 50)
    print("BASELINE RESULTS (No Battery)")
    print("=" * 50)
    print(f"\nTotal Cost:           ${result.total_cost:.2f}")
    print(f"Grid Import:          {result.total_import_kwh:.1f} kWh")
    print(f"Grid Export:          {result.total_export_kwh:.1f} kWh")
    print(f"Peak Import:          {result.peak_import_kw:.2f} kW")
    print(f"Self-Consumption:     {result.self_consumption_ratio*100:.1f}%")
    print("=" * 50)

    logger.info("Baseline computation complete")


if __name__ == "__main__":
    main()
