#!/usr/bin/env python
"""CLI script to run battery dispatch optimization.

Usage:
    python scripts/run_optimization.py --config config/config.yaml

This script:
1. Loads configuration and data
2. Runs LP optimization for battery scheduling
3. Computes and displays savings metrics
4. Generates visualization plots
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import load_config
from src.data.loaders import load_processed_data, generate_synthetic_data
from src.optimization.scheduler import MicrogridScheduler
from src.evaluation.baseline import compute_baseline_cost
from src.evaluation.metrics import compute_savings_metrics, format_metrics_report
from src.plots.visualizations import (
    set_plot_style,
    plot_dispatch_schedule,
    plot_soc_trajectory,
    plot_cost_comparison,
)
from src.utils.logger import setup_logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run battery dispatch optimization"
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
        help="Use synthetic data",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip generating plots",
    )
    args = parser.parse_args()

    # Load configuration
    settings = load_config(args.config)
    logger = setup_logger("microgrid", settings.log_level)

    logger.info("Starting optimization")
    logger.info(f"Solver: {settings.optimization.solver}")
    logger.info(f"Battery: {settings.battery.capacity_kwh} kWh, {settings.battery.max_power_kw} kW")

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
        df = load_processed_data(
            data_dir=settings.results_dir,
            start_date=settings.start_date,
            end_date=settings.end_date,
        )

    dt_hours = settings.resolution_minutes / 60.0

    # Compute baseline
    logger.info("Computing baseline...")
    baseline = compute_baseline_cost(
        prices=df["price"].values,
        p_solar=df["solar"].values,
        p_load=df["load"].values,
        feed_in_tariff=settings.grid.feed_in_tariff,
        dt_hours=dt_hours,
    )

    # Run optimization
    logger.info("Running optimization...")
    scheduler = MicrogridScheduler(settings)
    result = scheduler.optimize(
        timestamps=df.index,
        prices=df["price"].values,
        p_solar=df["solar"].values,
        p_load=df["load"].values,
    )

    logger.info(f"Solver status: {result.solve_status}")
    logger.info(f"Solve time: {result.solve_time:.3f}s")

    # Compute metrics
    metrics = compute_savings_metrics(
        baseline=baseline,
        optimized=result,
        battery_capacity_kwh=settings.battery.capacity_kwh,
        dt_hours=dt_hours,
    )

    # Display results
    print(format_metrics_report(metrics))

    # Generate plots
    if not args.no_plots:
        logger.info("Generating plots...")
        set_plot_style()

        figures_dir = settings.figures_dir
        figures_dir.mkdir(parents=True, exist_ok=True)

        plot_dispatch_schedule(result, save_path=figures_dir / "dispatch_schedule.png")
        plot_soc_trajectory(
            result,
            soc_min=settings.battery.soc_min,
            soc_max=settings.battery.soc_max,
            save_path=figures_dir / "soc_trajectory.png",
        )
        plot_cost_comparison(
            baseline.total_cost,
            result.total_cost,
            save_path=figures_dir / "cost_comparison.png",
        )

        logger.info(f"Plots saved to {figures_dir}")

    # Save results
    results_df = result.to_dataframe()
    output_path = settings.results_dir / "optimization_results.csv"
    results_df.to_csv(output_path)
    logger.info(f"Results saved to {output_path}")

    logger.info("Optimization complete")


if __name__ == "__main__":
    main()
