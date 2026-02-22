"""Smoke tests using synthetic 24-hour data.

These tests verify the core functionality works end-to-end
with minimal synthetic data.
"""

import numpy as np
import pandas as pd
import pytest

from src.optimization.battery import BatteryModel, soc_dynamics, simulate_soc_trajectory
from src.optimization.solver import CVXPYSolver
from src.optimization.objective import build_cost_objective, compute_energy_balance
from src.evaluation.baseline import compute_baseline_cost


class TestBatteryModel:
    """Test battery model and SOC dynamics."""

    def test_battery_validation(self):
        """Battery parameters are validated correctly."""
        battery = BatteryModel(
            capacity_kwh=13.5,
            max_power_kw=5.0,
            eta_charge=0.95,
            eta_discharge=0.95,
            soc_min=0.1,
            soc_max=0.9,
            soc_initial=0.5,
        )
        assert battery.energy_min_kwh == 1.35
        assert battery.energy_max_kwh == 12.15

    def test_soc_dynamics_charge(self):
        """SOC increases when charging."""
        soc_next = soc_dynamics(
            soc_prev=0.5,
            p_charge=5.0,
            p_discharge=0.0,
            capacity_kwh=10.0,
            eta_charge=1.0,
            eta_discharge=1.0,
            dt_hours=1.0,
        )
        assert soc_next == 1.0  # 5 kWh into 10 kWh = 50% increase

    def test_soc_dynamics_discharge(self):
        """SOC decreases when discharging."""
        soc_next = soc_dynamics(
            soc_prev=0.5,
            p_charge=0.0,
            p_discharge=2.5,
            capacity_kwh=10.0,
            eta_charge=1.0,
            eta_discharge=1.0,
            dt_hours=1.0,
        )
        assert soc_next == 0.25  # 2.5 kWh out of 10 kWh = 25% decrease

    def test_soc_trajectory(self):
        """SOC trajectory simulation works correctly."""
        battery = BatteryModel(
            capacity_kwh=10.0,
            max_power_kw=5.0,
            eta_charge=1.0,
            eta_discharge=1.0,
            soc_min=0.1,
            soc_max=0.9,
            soc_initial=0.5,
        )
        p_charge = np.array([2.0, 0.0, 0.0])
        p_discharge = np.array([0.0, 1.0, 1.0])

        soc = simulate_soc_trajectory(battery, p_charge, p_discharge)

        assert len(soc) == 4
        assert soc[0] == 0.5
        assert soc[1] == 0.7  # Charged 2 kWh
        assert soc[2] == 0.6  # Discharged 1 kWh


class TestOptimization:
    """Test optimization solver."""

    @pytest.fixture
    def synthetic_24h_data(self):
        """Generate 24-hour synthetic data."""
        np.random.seed(42)
        n_steps = 24

        # Simple price profile: low at night, high in evening
        prices = np.array([0.10] * 6 + [0.20] * 6 + [0.15] * 6 + [0.35] * 6)

        # Solar: bell curve during day
        hours = np.arange(24)
        solar = 5.0 * np.exp(-((hours - 12) ** 2) / 18)
        solar = np.where((hours >= 6) & (hours <= 18), solar, 0)

        # Load: morning and evening peaks
        load = np.ones(24) * 0.8
        load[7:9] = 1.5
        load[18:22] = 2.0

        timestamps = pd.date_range("2024-01-01", periods=24, freq="h")

        return {
            "timestamps": timestamps,
            "prices": prices,
            "solar": solar,
            "load": load,
        }

    def test_cvxpy_solver_runs(self, synthetic_24h_data):
        """CVXPY solver runs without error."""
        solver = CVXPYSolver(backend="HIGHS")

        result = solver.solve(
            prices=synthetic_24h_data["prices"],
            p_solar=synthetic_24h_data["solar"],
            p_load=synthetic_24h_data["load"],
            battery_capacity=10.0,
            battery_power=5.0,
            eta_charge=0.95,
            eta_discharge=0.95,
            soc_min=0.1,
            soc_max=0.9,
            soc_initial=0.5,
            feed_in_tariff=0.05,
            max_import=10.0,
            max_export=5.0,
            dt_hours=1.0,
        )

        assert result.status == "optimal"
        assert result.optimal_value is not None
        assert len(result.p_charge) == 24
        assert len(result.soc) == 25

    def test_optimization_respects_soc_bounds(self, synthetic_24h_data):
        """SOC stays within bounds."""
        solver = CVXPYSolver(backend="HIGHS")

        result = solver.solve(
            prices=synthetic_24h_data["prices"],
            p_solar=synthetic_24h_data["solar"],
            p_load=synthetic_24h_data["load"],
            battery_capacity=10.0,
            battery_power=5.0,
            eta_charge=0.95,
            eta_discharge=0.95,
            soc_min=0.1,
            soc_max=0.9,
            soc_initial=0.5,
            feed_in_tariff=0.05,
            max_import=10.0,
            max_export=5.0,
            dt_hours=1.0,
        )

        assert np.all(result.soc >= 0.1 - 1e-6)
        assert np.all(result.soc <= 0.9 + 1e-6)

    def test_optimization_reduces_cost(self, synthetic_24h_data):
        """Optimized cost is less than or equal to baseline."""
        # Baseline cost
        baseline = compute_baseline_cost(
            prices=synthetic_24h_data["prices"],
            p_solar=synthetic_24h_data["solar"],
            p_load=synthetic_24h_data["load"],
            feed_in_tariff=0.05,
            dt_hours=1.0,
        )

        # Optimized cost
        solver = CVXPYSolver(backend="HIGHS")
        result = solver.solve(
            prices=synthetic_24h_data["prices"],
            p_solar=synthetic_24h_data["solar"],
            p_load=synthetic_24h_data["load"],
            battery_capacity=10.0,
            battery_power=5.0,
            eta_charge=0.95,
            eta_discharge=0.95,
            soc_min=0.1,
            soc_max=0.9,
            soc_initial=0.5,
            feed_in_tariff=0.05,
            max_import=10.0,
            max_export=5.0,
            dt_hours=1.0,
        )

        assert result.optimal_value <= baseline.total_cost


class TestBaseline:
    """Test baseline cost calculation."""

    def test_baseline_cost_positive(self):
        """Baseline cost is computed correctly."""
        prices = np.array([0.20, 0.20, 0.20])
        p_solar = np.array([0.0, 2.0, 0.0])
        p_load = np.array([1.0, 1.0, 1.0])

        result = compute_baseline_cost(
            prices=prices,
            p_solar=p_solar,
            p_load=p_load,
            feed_in_tariff=0.05,
            dt_hours=1.0,
        )

        # Hour 0: import 1 kWh @ $0.20 = $0.20
        # Hour 1: export 1 kWh @ $0.05 = -$0.05
        # Hour 2: import 1 kWh @ $0.20 = $0.20
        expected = 0.20 - 0.05 + 0.20
        assert abs(result.total_cost - expected) < 1e-6

    def test_self_consumption_ratio(self):
        """Self-consumption ratio is correct."""
        prices = np.ones(4) * 0.20
        p_solar = np.array([0.0, 3.0, 3.0, 0.0])  # 6 kWh total
        p_load = np.array([1.0, 2.0, 2.0, 1.0])   # 6 kWh total

        result = compute_baseline_cost(
            prices=prices,
            p_solar=p_solar,
            p_load=p_load,
            feed_in_tariff=0.05,
            dt_hours=1.0,
        )

        # 4 kWh of solar used on-site, 2 kWh exported
        assert abs(result.self_consumption_ratio - 4/6) < 1e-6


class TestEnergyBalance:
    """Test energy balance calculations."""

    def test_energy_balance(self):
        """Power balance equation holds."""
        p_solar = np.array([3.0, 0.0])
        p_load = np.array([1.0, 2.0])
        p_charge = np.array([1.0, 0.0])
        p_discharge = np.array([0.0, 1.0])

        p_import, p_export = compute_energy_balance(
            p_solar, p_load, p_charge, p_discharge
        )

        # Hour 0: solar=3, load=1, charge=1 -> export=1
        # Hour 1: solar=0, load=2, discharge=1 -> import=1
        assert p_export[0] == 1.0
        assert p_import[0] == 0.0
        assert p_import[1] == 1.0
        assert p_export[1] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
