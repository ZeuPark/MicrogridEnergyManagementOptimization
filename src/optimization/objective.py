"""Cost objective function for optimization."""

import numpy as np


def build_cost_objective(
    prices: np.ndarray,
    feed_in_tariff: float,
    p_grid_import: np.ndarray,
    p_grid_export: np.ndarray,
    dt_hours: float = 1.0,
) -> float:
    """Build total cost objective for grid interaction.

    Cost = sum(price[t] * P_import[t] * dt) - sum(FiT * P_export[t] * dt)

    Args:
        prices: Electricity spot prices in $/kWh per time step.
        feed_in_tariff: Export tariff in $/kWh.
        p_grid_import: Grid import power array in kW.
        p_grid_export: Grid export power array in kW.
        dt_hours: Time step duration in hours.

    Returns:
        Total cost in $.
    """
    import_cost = np.sum(prices * p_grid_import * dt_hours)
    export_revenue = np.sum(feed_in_tariff * p_grid_export * dt_hours)
    return import_cost - export_revenue


def compute_energy_balance(
    p_solar: np.ndarray,
    p_load: np.ndarray,
    p_charge: np.ndarray,
    p_discharge: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute grid import/export from energy balance.

    Power balance: P_solar + P_discharge + P_import = P_load + P_charge + P_export

    Args:
        p_solar: Solar generation power array.
        p_load: Load demand power array.
        p_charge: Battery charging power array.
        p_discharge: Battery discharging power array.

    Returns:
        Tuple of (p_grid_import, p_grid_export) arrays.
    """
    net_load = p_load + p_charge - p_solar - p_discharge
    p_grid_import = np.maximum(net_load, 0)
    p_grid_export = np.maximum(-net_load, 0)
    return p_grid_import, p_grid_export
