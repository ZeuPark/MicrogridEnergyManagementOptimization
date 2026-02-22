"""Load demand forecasting and profile generation."""

from typing import Literal

import numpy as np
import pandas as pd


ProfileType = Literal["residential", "commercial", "industrial"]


def generate_load_profile(
    timestamps: pd.DatetimeIndex,
    annual_kwh: float,
    profile_type: ProfileType = "residential",
    noise_std: float = 0.1,
) -> np.ndarray:
    """Generate load demand profile.

    Args:
        timestamps: Time index for load profile.
        annual_kwh: Annual energy consumption in kWh.
        profile_type: Type of load profile pattern.
        noise_std: Standard deviation of random noise.

    Returns:
        Array of load demand in kW.
    """
    hours = timestamps.hour + timestamps.minute / 60
    pattern = get_hourly_pattern(profile_type)

    # Interpolate pattern to timestamps
    load_factor = np.interp(hours, np.arange(24), pattern)

    # Scale to match annual consumption
    daily_kwh = annual_kwh / 365
    base_hourly = daily_kwh / 24
    load = base_hourly * load_factor

    # Add noise
    noise = np.random.normal(1.0, noise_std, len(timestamps))
    load = load * np.maximum(noise, 0.5)

    return load


def get_hourly_pattern(profile_type: ProfileType) -> np.ndarray:
    """Get normalized hourly load pattern for profile type.

    Args:
        profile_type: Type of load profile.

    Returns:
        24-element array of hourly load factors.
    """
    patterns = {
        "residential": np.array([
            0.4, 0.3, 0.3, 0.3, 0.3, 0.4,  # 00-05
            0.6, 1.2, 1.5, 1.2, 0.9, 0.8,  # 06-11
            0.8, 0.8, 0.9, 1.0, 1.2, 1.5,  # 12-17
            2.0, 2.2, 1.8, 1.2, 0.8, 0.5,  # 18-23
        ]),
        "commercial": np.array([
            0.3, 0.3, 0.3, 0.3, 0.3, 0.4,  # 00-05
            0.6, 1.0, 1.5, 1.8, 1.8, 1.7,  # 06-11
            1.5, 1.8, 1.8, 1.8, 1.7, 1.5,  # 12-17
            1.0, 0.6, 0.4, 0.3, 0.3, 0.3,  # 18-23
        ]),
        "industrial": np.array([
            0.8, 0.8, 0.8, 0.8, 0.8, 0.9,  # 00-05
            1.0, 1.2, 1.3, 1.3, 1.3, 1.2,  # 06-11
            1.0, 1.3, 1.3, 1.3, 1.2, 1.0,  # 12-17
            0.9, 0.8, 0.8, 0.8, 0.8, 0.8,  # 18-23
        ]),
    }
    return patterns[profile_type]


def apply_load_pattern(
    base_load: np.ndarray,
    multiplier: float,
) -> np.ndarray:
    """Apply scaling factor to load profile.

    Args:
        base_load: Original load profile.
        multiplier: Scaling factor.

    Returns:
        Scaled load profile.
    """
    return base_load * multiplier
