"""Baseline cost calculation without battery storage."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BaselineResult:
    """Baseline scenario results without battery.

    Attributes:
        total_cost: Total electricity cost.
        total_import_kwh: Total grid import energy.
        total_export_kwh: Total grid export energy.
        peak_import_kw: Maximum import power.
        self_consumption_ratio: Fraction of solar used on-site.
    """

    total_cost: float
    total_import_kwh: float
    total_export_kwh: float
    peak_import_kw: float
    self_consumption_ratio: float


def compute_baseline_cost(
    prices: np.ndarray,
    p_solar: np.ndarray,
    p_load: np.ndarray,
    feed_in_tariff: float,
    dt_hours: float = 1.0,
) -> BaselineResult:
    """Compute cost for baseline scenario (no battery).

    In the baseline case, all excess solar is exported and all
    deficit is imported from the grid.

    Args:
        prices: Electricity prices in $/kWh.
        p_solar: Solar generation in kW.
        p_load: Load demand in kW.
        feed_in_tariff: Export tariff in $/kWh.
        dt_hours: Time step duration in hours.

    Returns:
        BaselineResult with cost and energy metrics.
    """
    # Net load: positive = import, negative = export
    net_load = p_load - p_solar

    p_import = np.maximum(net_load, 0)
    p_export = np.maximum(-net_load, 0)

    # Calculate costs
    import_cost = np.sum(prices * p_import * dt_hours)
    export_revenue = np.sum(feed_in_tariff * p_export * dt_hours)
    total_cost = import_cost - export_revenue

    # Energy metrics
    total_import_kwh = np.sum(p_import * dt_hours)
    total_export_kwh = np.sum(p_export * dt_hours)
    peak_import_kw = np.max(p_import)

    # Self-consumption: solar used on-site / total solar
    total_solar = np.sum(p_solar * dt_hours)
    solar_used = total_solar - total_export_kwh
    self_consumption = solar_used / total_solar if total_solar > 0 else 0.0

    return BaselineResult(
        total_cost=total_cost,
        total_import_kwh=total_import_kwh,
        total_export_kwh=total_export_kwh,
        peak_import_kw=peak_import_kw,
        self_consumption_ratio=self_consumption,
    )


def compute_no_solar_baseline(
    prices: np.ndarray,
    p_load: np.ndarray,
    dt_hours: float = 1.0,
) -> float:
    """Compute cost with no solar and no battery.

    Useful for calculating total value of solar + battery system.

    Args:
        prices: Electricity prices in $/kWh.
        p_load: Load demand in kW.
        dt_hours: Time step duration in hours.

    Returns:
        Total electricity cost.
    """
    return float(np.sum(prices * p_load * dt_hours))
