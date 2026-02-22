"""Solar generation forecasting and profile generation."""

from typing import Optional

import numpy as np
import pandas as pd


def generate_solar_profile(
    timestamps: pd.DatetimeIndex,
    capacity_kw: float,
    latitude: float = -33.87,  # Sydney default
    cloud_factor: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Generate solar generation profile.

    Uses a simplified clear-sky model with optional cloud factor.

    Args:
        timestamps: Time index for generation.
        capacity_kw: PV system capacity in kW.
        latitude: Site latitude (for solar geometry).
        cloud_factor: Optional array of cloud cover (0-1).

    Returns:
        Array of solar generation in kW.
    """
    hours = timestamps.hour + timestamps.minute / 60
    day_of_year = timestamps.dayofyear

    # Solar declination angle (simplified)
    declination = 23.45 * np.sin(np.radians((284 + day_of_year) * 360 / 365))

    # Hour angle
    hour_angle = 15 * (hours - 12)

    # Solar elevation (simplified)
    lat_rad = np.radians(latitude)
    decl_rad = np.radians(declination)
    ha_rad = np.radians(hour_angle)

    sin_elevation = (
        np.sin(lat_rad) * np.sin(decl_rad)
        + np.cos(lat_rad) * np.cos(decl_rad) * np.cos(ha_rad)
    )

    # Clear sky irradiance (normalized)
    clear_sky = np.maximum(sin_elevation, 0)

    # Apply cloud factor if provided
    if cloud_factor is None:
        cloud_factor = np.ones(len(timestamps))

    generation = capacity_kw * clear_sky * cloud_factor

    return generation


def scale_solar_capacity(
    base_profile: np.ndarray,
    base_capacity: float,
    new_capacity: float,
) -> np.ndarray:
    """Scale solar profile to different capacity.

    Args:
        base_profile: Original generation profile.
        base_capacity: Original system capacity.
        new_capacity: Target system capacity.

    Returns:
        Scaled generation profile.
    """
    return base_profile * (new_capacity / base_capacity)
