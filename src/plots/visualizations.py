"""Visualization functions for microgrid analysis."""

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from src.optimization.scheduler import OptimizationResult
from src.evaluation.sensitivity import SensitivityResult


def set_plot_style() -> None:
    """Set consistent plot style for all figures."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.figsize": (12, 6),
            "axes.labelsize": 12,
            "axes.titlesize": 14,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


def plot_dispatch_schedule(
    result: OptimizationResult,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Plot power dispatch schedule.

    Shows solar, load, battery charge/discharge, and grid flows.

    Args:
        result: Optimization results.
        save_path: Optional path to save figure.

    Returns:
        Matplotlib figure.
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    timestamps = result.timestamps

    # Panel 1: Generation and Load
    ax1 = axes[0]
    ax1.fill_between(timestamps, result.p_solar, alpha=0.7, label="Solar", color="gold")
    ax1.plot(timestamps, result.p_load, label="Load", color="black", linewidth=2)
    ax1.set_ylabel("Power (kW)")
    ax1.set_title("Generation and Demand")
    ax1.legend(loc="upper right")
    ax1.set_ylim(bottom=0)

    # Panel 2: Battery and Grid
    ax2 = axes[1]
    ax2.bar(
        timestamps,
        result.p_charge,
        width=0.03,
        label="Battery Charge",
        color="green",
        alpha=0.7,
    )
    ax2.bar(
        timestamps,
        -result.p_discharge,
        width=0.03,
        label="Battery Discharge",
        color="red",
        alpha=0.7,
    )
    ax2.plot(
        timestamps,
        result.p_grid_import,
        label="Grid Import",
        color="blue",
        linewidth=1.5,
    )
    ax2.plot(
        timestamps,
        -result.p_grid_export,
        label="Grid Export",
        color="purple",
        linewidth=1.5,
        linestyle="--",
    )
    ax2.axhline(0, color="gray", linewidth=0.5)
    ax2.set_ylabel("Power (kW)")
    ax2.set_title("Battery and Grid Flows")
    ax2.legend(loc="upper right")

    # Panel 3: Prices
    ax3 = axes[2]
    ax3.step(timestamps, result.prices, where="post", color="darkblue", linewidth=1.5)
    ax3.fill_between(
        timestamps, result.prices, step="post", alpha=0.3, color="blue"
    )
    ax3.set_ylabel("Price ($/kWh)")
    ax3.set_xlabel("Time")
    ax3.set_title("Electricity Price")

    # Format x-axis
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax3.xaxis.set_major_locator(mdates.HourLocator(interval=4))

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def plot_soc_trajectory(
    result: OptimizationResult,
    soc_min: float,
    soc_max: float,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Plot battery state of charge over time.

    Args:
        result: Optimization results.
        soc_min: Minimum SOC constraint.
        soc_max: Maximum SOC constraint.
        save_path: Optional path to save figure.

    Returns:
        Matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    # SOC timestamps include final value
    soc_times = pd.date_range(
        start=result.timestamps[0],
        periods=len(result.soc),
        freq=result.timestamps.freq,
    )

    ax.plot(soc_times, result.soc * 100, linewidth=2, color="green", label="SOC")
    ax.axhline(soc_min * 100, color="red", linestyle="--", label=f"Min ({soc_min*100:.0f}%)")
    ax.axhline(soc_max * 100, color="red", linestyle="--", label=f"Max ({soc_max*100:.0f}%)")
    ax.fill_between(soc_times, soc_min * 100, soc_max * 100, alpha=0.1, color="green")

    ax.set_xlabel("Time")
    ax.set_ylabel("State of Charge (%)")
    ax.set_title("Battery State of Charge")
    ax.legend()
    ax.set_ylim(0, 100)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def plot_cost_comparison(
    baseline_cost: float,
    optimized_cost: float,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Plot cost comparison bar chart.

    Args:
        baseline_cost: Cost without battery.
        optimized_cost: Cost with optimization.
        save_path: Optional path to save figure.

    Returns:
        Matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ["Baseline\n(No Battery)", "Optimized\n(With Battery)"]
    costs = [baseline_cost, optimized_cost]
    colors = ["#ff7f7f", "#7fbf7f"]

    bars = ax.bar(categories, costs, color=colors, width=0.5, edgecolor="black")

    # Add value labels
    for bar, cost in zip(bars, costs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(costs) * 0.02,
            f"${cost:.2f}",
            ha="center",
            fontsize=12,
            fontweight="bold",
        )

    savings = baseline_cost - optimized_cost
    savings_pct = savings / baseline_cost * 100 if baseline_cost > 0 else 0

    ax.set_ylabel("Total Cost ($)")
    ax.set_title(f"Cost Comparison (Savings: ${savings:.2f}, {savings_pct:.1f}%)")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def plot_sensitivity_results(
    sensitivity: SensitivityResult,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Plot sensitivity analysis results.

    Args:
        sensitivity: Sensitivity analysis results.
        save_path: Optional path to save figure.

    Returns:
        Matplotlib figure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    x = sensitivity.parameter_values

    # Left: Absolute costs
    ax1.plot(x, sensitivity.baseline_costs, "o-", label="Baseline", color="red")
    ax1.plot(x, sensitivity.optimized_costs, "s-", label="Optimized", color="green")
    ax1.fill_between(
        x,
        sensitivity.optimized_costs,
        sensitivity.baseline_costs,
        alpha=0.3,
        color="green",
    )
    ax1.set_xlabel(_format_param_label(sensitivity.parameter_name))
    ax1.set_ylabel("Cost ($)")
    ax1.set_title("Cost vs Parameter Value")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Right: Savings percentage
    ax2.plot(x, sensitivity.savings_pct, "o-", color="blue", linewidth=2)
    ax2.fill_between(x, sensitivity.savings_pct, alpha=0.3, color="blue")
    ax2.set_xlabel(_format_param_label(sensitivity.parameter_name))
    ax2.set_ylabel("Savings (%)")
    ax2.set_title("Savings vs Parameter Value")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def _format_param_label(param_name: str) -> str:
    """Format parameter name for plot labels."""
    labels = {
        "battery.capacity_kwh": "Battery Capacity (kWh)",
        "battery.max_power_kw": "Battery Power (kW)",
        "solar.capacity_kw": "Solar Capacity (kW)",
        "grid.feed_in_tariff": "Feed-in Tariff ($/kWh)",
    }
    return labels.get(param_name, param_name)
