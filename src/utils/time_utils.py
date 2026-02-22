"""Time and timezone utilities."""

from typing import Union

import pandas as pd


def localize_timestamps(
    timestamps: pd.DatetimeIndex,
    timezone: str,
) -> pd.DatetimeIndex:
    """Localize naive timestamps to timezone.

    Args:
        timestamps: DatetimeIndex (naive or localized).
        timezone: Target timezone string.

    Returns:
        Localized DatetimeIndex.
    """
    if timestamps.tz is None:
        return timestamps.tz_localize(timezone)
    else:
        return timestamps.tz_convert(timezone)


def get_resolution_freq(resolution_minutes: int) -> str:
    """Convert resolution in minutes to pandas frequency string.

    Args:
        resolution_minutes: Time step in minutes.

    Returns:
        Pandas frequency string.
    """
    if resolution_minutes == 60:
        return "h"
    elif resolution_minutes < 60:
        return f"{resolution_minutes}min"
    else:
        hours = resolution_minutes // 60
        return f"{hours}h"


def create_time_index(
    start_date: str,
    end_date: str,
    resolution_minutes: int,
    timezone: str,
) -> pd.DatetimeIndex:
    """Create time index for optimization horizon.

    Args:
        start_date: Start date string.
        end_date: End date string.
        resolution_minutes: Time step in minutes.
        timezone: Timezone string.

    Returns:
        DatetimeIndex with specified resolution.
    """
    freq = get_resolution_freq(resolution_minutes)
    return pd.date_range(
        start=start_date,
        end=end_date,
        freq=freq,
        tz=timezone,
    )[:-1]  # Exclude end timestamp
