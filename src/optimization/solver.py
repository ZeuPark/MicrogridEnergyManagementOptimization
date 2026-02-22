"""Solver abstraction layer for optimization backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np


@dataclass
class SolverResult:
    """Container for solver output."""

    status: str
    optimal_value: float
    p_charge: np.ndarray
    p_discharge: np.ndarray
    p_grid_import: np.ndarray
    p_grid_export: np.ndarray
    soc: np.ndarray
    solve_time: float


class Solver(ABC):
    """Abstract base class for optimization solvers."""

    @abstractmethod
    def solve(
        self,
        prices: np.ndarray,
        p_solar: np.ndarray,
        p_load: np.ndarray,
        battery_capacity: float,
        battery_power: float,
        eta_charge: float,
        eta_discharge: float,
        soc_min: float,
        soc_max: float,
        soc_initial: float,
        feed_in_tariff: float,
        max_import: float,
        max_export: float,
        dt_hours: float,
    ) -> SolverResult:
        """Solve the optimization problem."""
        pass


class CVXPYSolver(Solver):
    """CVXPY-based LP solver for battery scheduling."""

    def __init__(self, backend: str = "HIGHS"):
        """Initialize solver with specified backend.

        Args:
            backend: Solver backend (HIGHS, GLPK, ECOS, SCS).
        """
        self.backend = backend

    def solve(
        self,
        prices: np.ndarray,
        p_solar: np.ndarray,
        p_load: np.ndarray,
        battery_capacity: float,
        battery_power: float,
        eta_charge: float,
        eta_discharge: float,
        soc_min: float,
        soc_max: float,
        soc_initial: float,
        feed_in_tariff: float,
        max_import: float,
        max_export: float,
        dt_hours: float,
    ) -> SolverResult:
        """Solve battery dispatch optimization using CVXPY.

        Formulates and solves the LP:
            min  sum(price[t] * P_import[t] - FiT * P_export[t]) * dt

        Subject to:
            - Power balance at each time step
            - SOC dynamics constraints
            - Battery power limits
            - SOC bounds
            - Grid connection limits
        """
        import time
        import cvxpy as cp

        n_steps = len(prices)
        start_time = time.time()

        # Decision variables
        p_charge = cp.Variable(n_steps, nonneg=True)
        p_discharge = cp.Variable(n_steps, nonneg=True)
        p_import = cp.Variable(n_steps, nonneg=True)
        p_export = cp.Variable(n_steps, nonneg=True)
        soc = cp.Variable(n_steps + 1)

        # Objective: minimize import cost minus export revenue
        cost = cp.sum(cp.multiply(prices, p_import) * dt_hours)
        revenue = cp.sum(feed_in_tariff * p_export * dt_hours)
        objective = cp.Minimize(cost - revenue)

        constraints = []

        # Power balance: solar + discharge + import = load + charge + export
        for t in range(n_steps):
            constraints.append(
                p_solar[t] + p_discharge[t] + p_import[t]
                == p_load[t] + p_charge[t] + p_export[t]
            )

        # SOC dynamics
        constraints.append(soc[0] == soc_initial)
        for t in range(n_steps):
            energy_change = (
                eta_charge * p_charge[t] - p_discharge[t] / eta_discharge
            ) * dt_hours / battery_capacity
            constraints.append(soc[t + 1] == soc[t] + energy_change)

        # Battery constraints
        constraints.append(p_charge <= battery_power)
        constraints.append(p_discharge <= battery_power)
        constraints.append(soc >= soc_min)
        constraints.append(soc <= soc_max)

        # Grid constraints
        constraints.append(p_import <= max_import)
        constraints.append(p_export <= max_export)

        # Solve
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=getattr(cp, self.backend, cp.HIGHS))

        solve_time = time.time() - start_time

        return SolverResult(
            status=problem.status,
            optimal_value=problem.value,
            p_charge=p_charge.value,
            p_discharge=p_discharge.value,
            p_grid_import=p_import.value,
            p_grid_export=p_export.value,
            soc=soc.value,
            solve_time=solve_time,
        )


class PuLPSolver(Solver):
    """PuLP-based LP solver for battery scheduling."""

    def __init__(self, backend: str = "PULP_CBC_CMD"):
        """Initialize solver with specified backend."""
        self.backend = backend

    def solve(
        self,
        prices: np.ndarray,
        p_solar: np.ndarray,
        p_load: np.ndarray,
        battery_capacity: float,
        battery_power: float,
        eta_charge: float,
        eta_discharge: float,
        soc_min: float,
        soc_max: float,
        soc_initial: float,
        feed_in_tariff: float,
        max_import: float,
        max_export: float,
        dt_hours: float,
    ) -> SolverResult:
        """Solve battery dispatch optimization using PuLP."""
        import time
        from pulp import (
            LpProblem, LpMinimize, LpVariable, lpSum, value, LpStatus
        )

        n_steps = len(prices)
        start_time = time.time()

        prob = LpProblem("BatteryScheduling", LpMinimize)

        # Decision variables
        p_charge = [LpVariable(f"p_ch_{t}", lowBound=0, upBound=battery_power) for t in range(n_steps)]
        p_discharge = [LpVariable(f"p_dis_{t}", lowBound=0, upBound=battery_power) for t in range(n_steps)]
        p_import = [LpVariable(f"p_imp_{t}", lowBound=0, upBound=max_import) for t in range(n_steps)]
        p_export = [LpVariable(f"p_exp_{t}", lowBound=0, upBound=max_export) for t in range(n_steps)]
        soc = [LpVariable(f"soc_{t}", lowBound=soc_min, upBound=soc_max) for t in range(n_steps + 1)]

        # Objective
        prob += lpSum(
            prices[t] * p_import[t] * dt_hours - feed_in_tariff * p_export[t] * dt_hours
            for t in range(n_steps)
        )

        # Constraints
        prob += soc[0] == soc_initial

        for t in range(n_steps):
            # Power balance
            prob += (
                p_solar[t] + p_discharge[t] + p_import[t]
                == p_load[t] + p_charge[t] + p_export[t]
            )
            # SOC dynamics
            energy_change = (
                eta_charge * p_charge[t] - p_discharge[t] / eta_discharge
            ) * dt_hours / battery_capacity
            prob += soc[t + 1] == soc[t] + energy_change

        prob.solve()
        solve_time = time.time() - start_time

        return SolverResult(
            status=LpStatus[prob.status],
            optimal_value=value(prob.objective),
            p_charge=np.array([value(p) for p in p_charge]),
            p_discharge=np.array([value(p) for p in p_discharge]),
            p_grid_import=np.array([value(p) for p in p_import]),
            p_grid_export=np.array([value(p) for p in p_export]),
            soc=np.array([value(s) for s in soc]),
            solve_time=solve_time,
        )


def get_solver(solver_type: str, backend: str) -> Solver:
    """Factory function to get solver instance.

    Args:
        solver_type: "CVXPY" or "PULP".
        backend: Solver backend name.

    Returns:
        Solver instance.
    """
    if solver_type.upper() == "CVXPY":
        return CVXPYSolver(backend)
    elif solver_type.upper() == "PULP":
        return PuLPSolver(backend)
    else:
        raise ValueError(f"Unknown solver type: {solver_type}")
