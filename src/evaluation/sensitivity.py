"""Sensitivity analysis for parameter sweeps."""

from dataclasses import dataclass
from typing import Any, Callable, List

import numpy as np
import pandas as pd

from src.config.settings import Settings
from src.optimization.scheduler import MicrogridScheduler, OptimizationResult
from src.evaluation.baseline import compute_baseline_cost, BaselineResult
from src.evaluation.metrics import compute_savings_metrics, SavingsMetrics


@dataclass
class SensitivityResult:
    """Results from sensitivity analysis sweep.

    Attributes:
        parameter_name: Name of varied parameter.
        parameter_values: List of parameter values tested.
        baseline_costs: Baseline cost for each value.
        optimized_costs: Optimized cost for each value.
        savings: Absolute savings for each value.
        savings_pct: Relative savings for each value.
    """

    parameter_name: str
    parameter_values: List[float]
    baseline_costs: List[float]
    optimized_costs: List[float]
    savings: List[float]
    savings_pct: List[float]

    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to DataFrame."""
        return pd.DataFrame(
            {
                self.parameter_name: self.parameter_values,
                "baseline_cost": self.baseline_costs,
                "optimized_cost": self.optimized_costs,
                "savings": self.savings,
                "savings_pct": self.savings_pct,
            }
        )


def run_sensitivity_analysis(
    base_settings: Settings,
    parameter_name: str,
    parameter_values: List[float],
    timestamps: pd.DatetimeIndex,
    prices: np.ndarray,
    p_solar: np.ndarray,
    p_load: np.ndarray,
) -> SensitivityResult:
    """Run sensitivity analysis over parameter range.

    Supports the following parameters:
    - battery.capacity_kwh
    - battery.max_power_kw
    - solar.capacity_kw
    - grid.feed_in_tariff

    Args:
        base_settings: Base configuration to modify.
        parameter_name: Dot-notation parameter path.
        parameter_values: List of values to test.
        timestamps: Time index for optimization.
        prices: Price data.
        p_solar: Solar generation data.
        p_load: Load demand data.

    Returns:
        SensitivityResult with costs and savings for each value.
    """
    dt_hours = base_settings.resolution_minutes / 60.0

    baseline_costs = []
    optimized_costs = []
    savings = []
    savings_pct = []

    for value in parameter_values:
        # Create modified settings
        settings = _modify_parameter(base_settings, parameter_name, value)

        # Scale solar if capacity changed
        if parameter_name == "solar.capacity_kw":
            scale = value / base_settings.solar_capacity_kw
            current_solar = p_solar * scale
        else:
            current_solar = p_solar

        # Compute baseline
        baseline = compute_baseline_cost(
            prices=prices,
            p_solar=current_solar,
            p_load=p_load,
            feed_in_tariff=settings.grid.feed_in_tariff,
            dt_hours=dt_hours,
        )

        # Run optimization
        scheduler = MicrogridScheduler(settings)
        result = scheduler.optimize(
            timestamps=timestamps,
            prices=prices,
            p_solar=current_solar,
            p_load=p_load,
        )

        # Record results
        baseline_costs.append(baseline.total_cost)
        optimized_costs.append(result.total_cost)
        savings.append(baseline.total_cost - result.total_cost)
        savings_pct.append(
            (baseline.total_cost - result.total_cost) / baseline.total_cost * 100
            if baseline.total_cost > 0
            else 0.0
        )

    return SensitivityResult(
        parameter_name=parameter_name,
        parameter_values=parameter_values,
        baseline_costs=baseline_costs,
        optimized_costs=optimized_costs,
        savings=savings,
        savings_pct=savings_pct,
    )


def _modify_parameter(settings: Settings, param_path: str, value: float) -> Settings:
    """Create new settings with modified parameter.

    Args:
        settings: Original settings.
        param_path: Dot-notation path (e.g., "battery.capacity_kwh").
        value: New value.

    Returns:
        New Settings object with modified value.
    """
    import copy

    new_settings = copy.deepcopy(settings)

    parts = param_path.split(".")
    if len(parts) == 2:
        section, param = parts
        if section == "battery":
            setattr(new_settings.battery, param, value)
        elif section == "grid":
            setattr(new_settings.grid, param, value)
        elif section == "solar":
            if param == "capacity_kw":
                new_settings.solar_capacity_kw = value
    else:
        raise ValueError(f"Unsupported parameter path: {param_path}")

    return new_settings
