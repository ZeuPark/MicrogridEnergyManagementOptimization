"""NSW NEM electricity price API client using OpenElectricity API."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


OPENELECTRICITY_BASE_URL = "https://data.openelectricity.org.au/v3/stats/au/NEM"


def fetch_nem_data(
    region: str = "NSW1",
    period: str = "7d",
) -> pd.DataFrame:
    """Fetch real NEM data from OpenElectricity API.

    Args:
        region: NEM region (NSW1, VIC1, QLD1, SA1, TAS1).
        period: Time period (7d, 30d, 1y).

    Returns:
        DataFrame with timestamp index and price, demand columns.
    """
    url = f"{OPENELECTRICITY_BASE_URL}/{region}/power/{period}.json"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    # Extract price and demand data
    price_data = None
    demand_data = None
    solar_data = None

    for item in data.get("data", []):
        item_id = item.get("id", "")

        if item_id == f"au.nem.{region.lower()}.price":
            price_data = item
        elif item_id == f"au.nem.{region.lower()}.demand":
            demand_data = item
        elif item_id == f"au.nem.{region.lower()}.fuel_tech.solar_rooftop.power":
            solar_data = item

    if not price_data:
        raise ValueError(f"No price data found for region {region}")

    # Build DataFrame from price history
    history = price_data["history"]
    start_time = pd.to_datetime(history["start"])
    interval_minutes = history.get("interval", "5m")

    # Parse interval
    if interval_minutes.endswith("m"):
        freq = f"{interval_minutes[:-1]}min"
    else:
        freq = interval_minutes

    # Create time index
    timestamps = pd.date_range(
        start=start_time,
        periods=len(history["data"]),
        freq=freq,
    )

    # Create DataFrame
    df = pd.DataFrame(index=timestamps)
    df.index.name = "timestamp"

    # Price in $/MWh -> $/kWh
    df["price"] = [v / 1000 if v is not None else None for v in history["data"]]

    # Add demand if available (scale down for residential simulation)
    if demand_data and "history" in demand_data:
        demand_values = demand_data["history"]["data"]
        if len(demand_values) == len(df):
            # Scale NSW demand (GW range) to residential load (kW range)
            # Use normalized profile shape
            demand_series = pd.Series(demand_values)
            demand_min = demand_series.min()
            demand_max = demand_series.max()
            # Normalize to 0.3-2.0 kW residential range
            df["load"] = 0.3 + (demand_series.values - demand_min) / (demand_max - demand_min) * 1.7

    # Add solar if available
    if solar_data and "history" in solar_data:
        solar_hist = solar_data["history"]
        solar_values = solar_hist["data"]
        solar_start = pd.to_datetime(solar_hist["start"])
        solar_interval = solar_hist.get("interval", "30m")

        # Parse solar interval
        if solar_interval.endswith("m"):
            solar_freq = f"{solar_interval[:-1]}min"
        else:
            solar_freq = solar_interval

        # Create solar time index
        solar_timestamps = pd.date_range(
            start=solar_start,
            periods=len(solar_values),
            freq=solar_freq,
        )

        # Create solar series with proper index
        solar_series = pd.Series(solar_values, index=solar_timestamps)
        solar_series = solar_series.fillna(0)

        # Scale to residential (6.6 kW system)
        solar_max = solar_series.max() if solar_series.max() > 0 else 1
        solar_series = (solar_series / solar_max) * 6.6

        # Reindex to match price data timestamps (forward fill for alignment)
        df["solar"] = solar_series.reindex(df.index, method="ffill").fillna(0)
    else:
        # Generate synthetic solar profile based on time of day
        df["solar"] = _generate_solar_profile(df.index, capacity_kw=6.6)

    # Fill any missing values
    df = df.ffill().bfill()

    # Ensure no negative values for solar
    df["solar"] = df["solar"].clip(lower=0)

    return df


def _generate_solar_profile(timestamps: pd.DatetimeIndex, capacity_kw: float = 6.6) -> pd.Series:
    """Generate realistic solar generation profile based on time of day.

    Args:
        timestamps: DatetimeIndex of timestamps.
        capacity_kw: Peak solar capacity in kW.

    Returns:
        Series of solar generation values.
    """
    import numpy as np

    hours = timestamps.hour + timestamps.minute / 60

    # Solar profile: peaks at noon, zero at night
    # Using a shifted cosine function
    solar = np.zeros(len(hours))

    for i, h in enumerate(hours):
        if 6 <= h <= 18:
            # Solar hours: 6 AM to 6 PM
            # Peak at noon (h=12)
            solar[i] = capacity_kw * np.sin(np.pi * (h - 6) / 12)
        else:
            solar[i] = 0.0

    # Add some daily variation (cloud cover simulation)
    np.random.seed(42)
    daily_factor = np.random.uniform(0.7, 1.0, size=len(timestamps) // 24 + 1)
    daily_factor = np.repeat(daily_factor, 24)[: len(timestamps)]
    solar = solar * daily_factor

    return pd.Series(solar, index=timestamps)


def fetch_nem_prices(
    region: str,
    start_date: str,
    end_date: str,
    cache_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """Fetch NEM Regional Reference Price (RRP) data.

    This is a wrapper for backward compatibility.

    Args:
        region: NEM region (NSW1, VIC1, QLD1, SA1, TAS1).
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).
        cache_dir: Optional directory to cache downloaded data.

    Returns:
        DataFrame with timestamp index and RRP column.
    """
    # Calculate period from date range
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    days = (end - start).days

    if days <= 7:
        period = "7d"
    elif days <= 30:
        period = "30d"
    else:
        period = "1y"

    return fetch_nem_data(region=region, period=period)


def load_nem_csv(filepath: Path, region: str) -> pd.DataFrame:
    """Load NEM price data from downloaded CSV.

    Args:
        filepath: Path to AEMO CSV file.
        region: NEM region to filter.

    Returns:
        DataFrame with datetime index and price column.
    """
    df = pd.read_csv(filepath, skiprows=1)

    # Filter for dispatch prices
    df = df[df["REGIONID"] == region]

    # Parse settlement date
    df["timestamp"] = pd.to_datetime(df["SETTLEMENTDATE"])
    df = df.set_index("timestamp")

    # RRP is in $/MWh, convert to $/kWh
    df["price"] = df["RRP"] / 1000

    return df[["price"]].sort_index()


def resample_to_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Resample data to hourly resolution.

    Args:
        df: DataFrame with price, load, solar columns.

    Returns:
        Resampled DataFrame with hourly data.
    """
    return df.resample("1h").mean()
