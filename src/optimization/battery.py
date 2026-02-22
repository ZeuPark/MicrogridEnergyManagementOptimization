"""Battery dynamics and constraints for optimization."""

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass
class BatteryModel:
    """Battery energy storage system model.

    Attributes:
        capacity_kwh: Total usable energy capacity.
        max_power_kw: Maximum charge/discharge power.
        eta_charge: Charging efficiency (0-1).
        eta_discharge: Discharging efficiency (0-1).
        soc_min: Minimum state of charge (0-1).
        soc_max: Maximum state of charge (0-1).
        soc_initial: Initial state of charge (0-1).
    """

    capacity_kwh: float
    max_power_kw: float
    eta_charge: float
    eta_discharge: float
    soc_min: float
    soc_max: float
    soc_initial: float

    def __post_init__(self) -> None:
        """Validate battery parameters."""
        if not 0 < self.eta_charge <= 1:
            raise ValueError("Charging efficiency must be in (0, 1]")
        if not 0 < self.eta_discharge <= 1:
            raise ValueError("Discharging efficiency must be in (0, 1]")
        if not 0 <= self.soc_min < self.soc_max <= 1:
            raise ValueError("SOC limits must satisfy 0 <= soc_min < soc_max <= 1")

    @property
    def energy_min_kwh(self) -> float:
        """Minimum allowable stored energy."""
        return self.soc_min * self.capacity_kwh

    @property
    def energy_max_kwh(self) -> float:
        """Maximum allowable stored energy."""
        return self.soc_max * self.capacity_kwh

    @property
    def energy_initial_kwh(self) -> float:
        """Initial stored energy."""
        return self.soc_initial * self.capacity_kwh


def soc_dynamics(
    soc_prev: float,
    p_charge: float,
    p_discharge: float,
    capacity_kwh: float,
    eta_charge: float,
    eta_discharge: float,
    dt_hours: float = 1.0,
) -> float:
    """Compute next SOC given charge/discharge power.

    Implements the discrete-time SOC update equation:
        SOC[t+1] = SOC[t] + (eta_c * P_charge - P_discharge / eta_d) * dt / C

    Args:
        soc_prev: Previous state of charge (0-1).
        p_charge: Charging power in kW (>= 0).
        p_discharge: Discharging power in kW (>= 0).
        capacity_kwh: Battery capacity in kWh.
        eta_charge: Charging efficiency.
        eta_discharge: Discharging efficiency.
        dt_hours: Time step duration in hours.

    Returns:
        Next state of charge (0-1).
    """
    energy_in = eta_charge * p_charge * dt_hours
    energy_out = (p_discharge / eta_discharge) * dt_hours
    delta_soc = (energy_in - energy_out) / capacity_kwh
    return soc_prev + delta_soc


def simulate_soc_trajectory(
    battery: BatteryModel,
    p_charge: np.ndarray,
    p_discharge: np.ndarray,
    dt_hours: float = 1.0,
) -> np.ndarray:
    """Simulate SOC trajectory over time horizon.

    Args:
        battery: Battery model parameters.
        p_charge: Array of charging power per time step.
        p_discharge: Array of discharging power per time step.
        dt_hours: Time step duration.

    Returns:
        Array of SOC values (length = len(p_charge) + 1).
    """
    n_steps = len(p_charge)
    soc = np.zeros(n_steps + 1)
    soc[0] = battery.soc_initial

    for t in range(n_steps):
        soc[t + 1] = soc_dynamics(
            soc_prev=soc[t],
            p_charge=p_charge[t],
            p_discharge=p_discharge[t],
            capacity_kwh=battery.capacity_kwh,
            eta_charge=battery.eta_charge,
            eta_discharge=battery.eta_discharge,
            dt_hours=dt_hours,
        )

    return soc
