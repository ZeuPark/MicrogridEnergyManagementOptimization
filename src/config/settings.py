"""Configuration loader and validation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class BatteryConfig:
    """Battery system parameters."""
    capacity_kwh: float
    max_power_kw: float
    efficiency_charge: float
    efficiency_discharge: float
    soc_min: float
    soc_max: float
    soc_initial: float
    cycle_cost_per_kwh: float = 0.0


@dataclass
class GridConfig:
    """Grid connection parameters."""
    feed_in_tariff: float
    max_import_kw: float
    max_export_kw: float


@dataclass
class OptimizationConfig:
    """Optimization settings."""
    solver: str
    backend: str
    objective: str
    lookahead_hours: int


@dataclass
class Settings:
    """Main configuration container."""
    battery: BatteryConfig
    grid: GridConfig
    optimization: OptimizationConfig
    region: str
    start_date: str
    end_date: str
    resolution_minutes: int
    timezone: str
    solar_capacity_kw: float
    results_dir: Path
    figures_dir: Path
    log_level: str

    @property
    def n_steps(self) -> int:
        """Number of time steps per day."""
        return 24 * 60 // self.resolution_minutes


def load_config(config_path: str | Path = "config/config.yaml") -> Settings:
    """Load and validate configuration from YAML file.

    Args:
        config_path: Path to configuration YAML file.

    Returns:
        Validated Settings object.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If required fields are missing or invalid.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    battery = BatteryConfig(
        capacity_kwh=cfg["battery"]["capacity_kwh"],
        max_power_kw=cfg["battery"]["max_power_kw"],
        efficiency_charge=cfg["battery"]["efficiency_charge"],
        efficiency_discharge=cfg["battery"]["efficiency_discharge"],
        soc_min=cfg["battery"]["soc_min"],
        soc_max=cfg["battery"]["soc_max"],
        soc_initial=cfg["battery"]["soc_initial"],
        cycle_cost_per_kwh=cfg["battery"].get("cycle_cost_per_kwh", 0.0),
    )

    grid = GridConfig(
        feed_in_tariff=cfg["grid"]["feed_in_tariff"],
        max_import_kw=cfg["grid"]["max_import_kw"],
        max_export_kw=cfg["grid"]["max_export_kw"],
    )

    optimization = OptimizationConfig(
        solver=cfg["optimization"]["solver"],
        backend=cfg["optimization"]["backend"],
        objective=cfg["optimization"]["objective"],
        lookahead_hours=cfg["optimization"]["lookahead_hours"],
    )

    return Settings(
        battery=battery,
        grid=grid,
        optimization=optimization,
        region=cfg["data"]["region"],
        start_date=cfg["data"]["start_date"],
        end_date=cfg["data"]["end_date"],
        resolution_minutes=cfg["data"]["resolution_minutes"],
        timezone=cfg["data"]["timezone"],
        solar_capacity_kw=cfg["solar"]["capacity_kw"],
        results_dir=Path(cfg["output"]["results_dir"]),
        figures_dir=Path(cfg["output"]["figures_dir"]),
        log_level=cfg["output"]["log_level"],
    )
