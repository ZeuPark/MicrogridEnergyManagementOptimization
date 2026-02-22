"""NSW NEM electricity price API client."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


NEM_DATA_URL = "https://nemweb.com.au/Reports/Current/Dispatch_SCADA/"


def fetch_nem_prices(
    region: str,
    start_date: str,
    end_date: str,
    cache_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """Fetch NEM Regional Reference Price (RRP) data.

    Note: This is a simplified implementation. For production use,
    consider using the official AEMO API or nempy package.

    Args:
        region: NEM region (NSW1, VIC1, QLD1, SA1, TAS1).
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).
        cache_dir: Optional directory to cache downloaded data.

    Returns:
        DataFrame with timestamp index and RRP column.
    """
    # For portfolio demonstration, use sample data or synthetic
    # In production, integrate with AEMO MMS Data Model
    raise NotImplementedError(
        "NEM API integration requires AEMO credentials. "
        "Use generate_synthetic_data() for demonstration."
    )


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


def resample_prices(
    df: pd.DataFrame,
    target_resolution: str = "1h",
) -> pd.DataFrame:
    """Resample price data to target resolution.

    Args:
        df: DataFrame with price column.
        target_resolution: Pandas frequency string.

    Returns:
        Resampled DataFrame.
    """
    return df.resample(target_resolution).mean()
