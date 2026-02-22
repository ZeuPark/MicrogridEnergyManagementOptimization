"""Main optimization orchestrator for microgrid scheduling."""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from src.config.settings import Settings
from src.optimization.battery import BatteryModel
from src.optimization.solver import Solver, SolverResult, get_solver


@dataclass
class OptimizationResult:
    """Complete optimization result with all dispatch data.

    Attributes:
        timestamps: Time index for results.
        prices: Electricity prices used.
        p_solar: Solar generation profile.
        p_load: Load demand profile.
        p_charge: Optimal charging power.
        p_discharge: Optimal discharging power.
        p_grid_import: Grid import power.
        p_grid_export: Grid export power.
        soc: State of charge trajectory.
        total_cost: Total operating cost.
        solve_status: Solver status string.
        solve_time: Solver computation time.
    """

    timestamps: pd.DatetimeIndex
    prices: np.ndarray
    p_solar: np.ndarray
    p_load: np.ndarray
    p_charge: np.ndarray
    p_discharge: np.ndarray
    p_grid_import: np.ndarray
    p_grid_export: np.ndarray
    soc: np.ndarray
    total_cost: float
    solve_status: str
    solve_time: float

    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame."""
        return pd.DataFrame(
            {
                "price": self.prices,
                "solar": self.p_solar,
                "load": self.p_load,
                "charge": self.p_charge,
                "discharge": self.p_discharge,
                "grid_import": self.p_grid_import,
                "grid_export": self.p_grid_export,
                "soc": self.soc[:-1],  # Exclude final SOC
            },
            index=self.timestamps,
        )


class MicrogridScheduler:
    """Orchestrates microgrid battery optimization.

    This class handles the complete workflow:
    1. Load input data (prices, solar, load)
    2. Configure battery model from settings
    3. Run optimization solver
    4. Package and return results
    """

    def __init__(self, settings: Settings):
        """Initialize scheduler with configuration.

        Args:
            settings: Project configuration object.
        """
        self.settings = settings
        self.battery = BatteryModel(
            capacity_kwh=settings.battery.capacity_kwh,
            max_power_kw=settings.battery.max_power_kw,
            eta_charge=settings.battery.efficiency_charge,
            eta_discharge=settings.battery.efficiency_discharge,
            soc_min=settings.battery.soc_min,
            soc_max=settings.battery.soc_max,
            soc_initial=settings.battery.soc_initial,
        )
        self.solver: Solver = get_solver(
            settings.optimization.solver,
            settings.optimization.backend,
        )
        self.dt_hours = settings.resolution_minutes / 60.0

    def optimize(
        self,
        timestamps: pd.DatetimeIndex,
        prices: np.ndarray,
        p_solar: np.ndarray,
        p_load: np.ndarray,
    ) -> OptimizationResult:
        """Run optimization for given input data.

        Args:
            timestamps: Time index for the optimization horizon.
            prices: Electricity prices in $/kWh.
            p_solar: Solar generation in kW.
            p_load: Load demand in kW.

        Returns:
            OptimizationResult with optimal dispatch schedule.
        """
        result: SolverResult = self.solver.solve(
            prices=prices,
            p_solar=p_solar,
            p_load=p_load,
            battery_capacity=self.battery.capacity_kwh,
            battery_power=self.battery.max_power_kw,
            eta_charge=self.battery.eta_charge,
            eta_discharge=self.battery.eta_discharge,
            soc_min=self.battery.soc_min,
            soc_max=self.battery.soc_max,
            soc_initial=self.battery.soc_initial,
            feed_in_tariff=self.settings.grid.feed_in_tariff,
            max_import=self.settings.grid.max_import_kw,
            max_export=self.settings.grid.max_export_kw,
            dt_hours=self.dt_hours,
        )

        return OptimizationResult(
            timestamps=timestamps,
            prices=prices,
            p_solar=p_solar,
            p_load=p_load,
            p_charge=result.p_charge,
            p_discharge=result.p_discharge,
            p_grid_import=result.p_grid_import,
            p_grid_export=result.p_grid_export,
            soc=result.soc,
            total_cost=result.optimal_value,
            solve_status=result.status,
            solve_time=result.solve_time,
        )
