#!/usr/bin/env python
"""CLI script to run sensitivity analysis.

Usage:
    python scripts/run_sensitivity.py --config config/config.yaml
    python scripts/run_sensitivity.py --param battery.capacity_kwh --values 5,10,15,20

This script:
1. Loads configuration and data
2. Runs optimization across parameter range
3. Generates sensitivity plots
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import load_config
from src.data.loaders import generate_synthetic_data
from src.evaluation.sensitivity import run_sensitivity_analysis
from src.plots.visualizations import set_plot_style, plot_sensitivity_results
from src.utils.logger import setup_logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run sensitivity analysis"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--param",
        type=str,
        default=None,
        help="Parameter to vary (e.g., battery.capacity_kwh)",
    )
    parser.add_argument(
        "--values",
        type=str,
        default=None,
        help="Comma-separated parameter values",
    )
    args = parser.parse_args()

    # Load configuration
    settings = load_config(args.config)
    logger = setup_logger("microgrid", settings.log_level)

    # Determine parameter and values
    if args.param:
        param_name = args.param
        param_values = [float(v) for v in args.values.split(",")]
    else:
        # Use config defaults
        import yaml
        with open(args.config) as f:
            cfg = yaml.safe_load(f)
        param_name = cfg["sensitivity"]["parameter"]
        param_values = cfg["sensitivity"]["values"]

    logger.info(f"Running sensitivity analysis for {param_name}")
    logger.info(f"Values: {param_values}")

    # Generate data
    df = generate_synthetic_data(
        start_date=settings.start_date,
        end_date=settings.end_date,
        resolution_minutes=settings.resolution_minutes,
        solar_capacity_kw=settings.solar_capacity_kw,
        timezone=settings.timezone,
    )

    # Run sensitivity analysis
    result = run_sensitivity_analysis(
        base_settings=settings,
        parameter_name=param_name,
        parameter_values=param_values,
        timestamps=df.index,
        prices=df["price"].values,
        p_solar=df["solar"].values,
        p_load=df["load"].values,
    )

    # Display results
    print("\n" + "=" * 60)
    print(f"SENSITIVITY ANALYSIS: {param_name}")
    print("=" * 60)
    print(result.to_dataframe().to_string(index=False))
    print("=" * 60)

    # Generate plot
    set_plot_style()
    figures_dir = settings.figures_dir
    figures_dir.mkdir(parents=True, exist_ok=True)

    plot_sensitivity_results(
        result,
        save_path=figures_dir / f"sensitivity_{param_name.replace('.', '_')}.png",
    )

    # Save results
    output_path = settings.results_dir / "sensitivity_results.csv"
    result.to_dataframe().to_csv(output_path, index=False)
    logger.info(f"Results saved to {output_path}")

    logger.info("Sensitivity analysis complete")


if __name__ == "__main__":
    main()
