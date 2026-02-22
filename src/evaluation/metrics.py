"""Cost savings and performance metrics."""

from dataclasses import dataclass

import numpy as np

from src.evaluation.baseline import BaselineResult
from src.optimization.scheduler import OptimizationResult


@dataclass
class SavingsMetrics:
    """Comparison metrics between optimized and baseline scenarios.

    Attributes:
        baseline_cost: Cost without battery.
        optimized_cost: Cost with optimized battery dispatch.
        absolute_savings: Dollar savings.
        relative_savings: Percentage savings.
        peak_reduction_kw: Reduction in peak import.
        peak_reduction_pct: Peak reduction percentage.
        self_consumption_improvement: Increase in self-consumption ratio.
        battery_throughput_kwh: Total energy cycled through battery.
        equivalent_cycles: Number of full battery cycles.
    """

    baseline_cost: float
    optimized_cost: float
    absolute_savings: float
    relative_savings: float
    peak_reduction_kw: float
    peak_reduction_pct: float
    self_consumption_improvement: float
    battery_throughput_kwh: float
    equivalent_cycles: float


def compute_savings_metrics(
    baseline: BaselineResult,
    optimized: OptimizationResult,
    battery_capacity_kwh: float,
    dt_hours: float = 1.0,
) -> SavingsMetrics:
    """Compute savings and performance metrics.

    Args:
        baseline: Baseline scenario results.
        optimized: Optimization results.
        battery_capacity_kwh: Battery capacity for cycle calculation.
        dt_hours: Time step duration.

    Returns:
        SavingsMetrics comparing the two scenarios.
    """
    # Cost savings
    absolute_savings = baseline.total_cost - optimized.total_cost
    relative_savings = (
        absolute_savings / baseline.total_cost * 100
        if baseline.total_cost > 0
        else 0.0
    )

    # Peak reduction
    optimized_peak = np.max(optimized.p_grid_import)
    peak_reduction_kw = baseline.peak_import_kw - optimized_peak
    peak_reduction_pct = (
        peak_reduction_kw / baseline.peak_import_kw * 100
        if baseline.peak_import_kw > 0
        else 0.0
    )

    # Self-consumption improvement
    total_solar = np.sum(optimized.p_solar * dt_hours)
    total_export = np.sum(optimized.p_grid_export * dt_hours)
    optimized_self_consumption = (
        (total_solar - total_export) / total_solar if total_solar > 0 else 0.0
    )
    self_consumption_improvement = (
        optimized_self_consumption - baseline.self_consumption_ratio
    ) * 100

    # Battery utilization
    throughput = np.sum(optimized.p_charge + optimized.p_discharge) * dt_hours / 2
    equivalent_cycles = throughput / battery_capacity_kwh

    return SavingsMetrics(
        baseline_cost=baseline.total_cost,
        optimized_cost=optimized.total_cost,
        absolute_savings=absolute_savings,
        relative_savings=relative_savings,
        peak_reduction_kw=peak_reduction_kw,
        peak_reduction_pct=peak_reduction_pct,
        self_consumption_improvement=self_consumption_improvement,
        battery_throughput_kwh=throughput,
        equivalent_cycles=equivalent_cycles,
    )


def format_metrics_report(metrics: SavingsMetrics) -> str:
    """Format metrics as human-readable report.

    Args:
        metrics: Computed savings metrics.

    Returns:
        Formatted string report.
    """
    return f"""
=== Optimization Results ===

Cost Analysis:
  Baseline Cost:    ${metrics.baseline_cost:,.2f}
  Optimized Cost:   ${metrics.optimized_cost:,.2f}
  Savings:          ${metrics.absolute_savings:,.2f} ({metrics.relative_savings:.1f}%)

Peak Demand:
  Peak Reduction:   {metrics.peak_reduction_kw:.2f} kW ({metrics.peak_reduction_pct:.1f}%)

Solar Utilization:
  Self-Consumption Improvement: {metrics.self_consumption_improvement:+.1f}%

Battery Usage:
  Energy Throughput: {metrics.battery_throughput_kwh:.1f} kWh
  Equivalent Cycles: {metrics.equivalent_cycles:.2f}
"""
