"""Data ingestion and loading functions."""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


def load_processed_data(
    data_dir: Path,
    start_date: str = None,
    end_date: str = None,
) -> pd.DataFrame:
    """Load processed data from CSV files.

    Args:
        data_dir: Directory containing processed data.
        start_date: Optional start date string (YYYY-MM-DD). If None, uses data start.
        end_date: Optional end date string (YYYY-MM-DD). If None, uses data end.

    Returns:
        DataFrame with columns: timestamp, price, solar, load.
    """
    filepath = data_dir / "microgrid_data.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Processed data not found: {filepath}")

    df = pd.read_csv(filepath, parse_dates=["timestamp"], index_col="timestamp")

    # If date range specified, try to filter; otherwise use all data
    if start_date and end_date:
        filtered = df.loc[start_date:end_date]
        # If filter results in empty dataframe, use all data
        if len(filtered) == 0:
            return df
        return filtered

    return df


def generate_synthetic_data(
    start_date: str,
    end_date: str,
    resolution_minutes: int = 60,
    solar_capacity_kw: float = 6.6,
    annual_load_kwh: float = 7000,
    timezone: str = "Australia/Sydney",
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """Generate synthetic microgrid data for testing.

    Creates realistic profiles for:
    - Solar generation (bell curve with weather variation)
    - Load demand (residential pattern with morning/evening peaks)
    - Electricity prices (time-of-use with volatility)

    Args:
        start_date: Start date string.
        end_date: End date string.
        resolution_minutes: Time step resolution.
        solar_capacity_kw: PV system capacity.
        annual_load_kwh: Annual consumption estimate.
        timezone: Timezone for timestamps.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with timestamp index and price, solar, load columns.
    """
    if seed is not None:
        np.random.seed(seed)

    # Create timestamp index
    timestamps = pd.date_range(
        start=start_date,
        end=end_date,
        freq=f"{resolution_minutes}min",
        tz=timezone,
    )[:-1]  # Exclude end

    n_steps = len(timestamps)
    hours = timestamps.hour + timestamps.minute / 60

    # Solar generation: bell curve centered at solar noon
    solar_noon = 12.5
    solar_width = 3.5
    solar_base = np.exp(-((hours - solar_noon) ** 2) / (2 * solar_width**2))
    solar_base = np.where((hours >= 6) & (hours <= 19), solar_base, 0)
    cloud_factor = 0.7 + 0.3 * np.random.random(n_steps)
    p_solar = solar_capacity_kw * solar_base * cloud_factor

    # Load profile: residential pattern
    daily_kwh = annual_load_kwh / 365
    hourly_base = daily_kwh / 24

    # Morning peak (7-9), evening peak (18-21)
    load_pattern = np.ones(n_steps)
    morning_mask = (hours >= 7) & (hours <= 9)
    evening_mask = (hours >= 18) & (hours <= 21)
    night_mask = (hours >= 23) | (hours <= 5)

    load_pattern[morning_mask] = 1.5
    load_pattern[evening_mask] = 2.0
    load_pattern[night_mask] = 0.5

    noise = 0.8 + 0.4 * np.random.random(n_steps)
    p_load = hourly_base * load_pattern * noise

    # Electricity prices: time-of-use structure ($/kWh)
    price_base = 0.10
    prices = np.ones(n_steps) * price_base

    # Peak pricing
    peak_mask = (hours >= 14) & (hours <= 20)
    shoulder_mask = ((hours >= 7) & (hours <= 14)) | ((hours >= 20) & (hours <= 22))
    off_peak_mask = ~(peak_mask | shoulder_mask)

    prices[peak_mask] = 0.35 + 0.15 * np.random.random(np.sum(peak_mask))
    prices[shoulder_mask] = 0.20 + 0.05 * np.random.random(np.sum(shoulder_mask))
    prices[off_peak_mask] = 0.08 + 0.04 * np.random.random(np.sum(off_peak_mask))

    return pd.DataFrame(
        {
            "price": prices,
            "solar": p_solar,
            "load": p_load,
        },
        index=timestamps,
    )


def save_processed_data(df: pd.DataFrame, output_path: Path) -> None:
    """Save processed data to CSV.

    Args:
        df: DataFrame to save.
        output_path: Output file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index_label="timestamp")
