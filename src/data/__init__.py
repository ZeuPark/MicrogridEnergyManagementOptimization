"""Data loading and processing module."""

from .loaders import load_processed_data, generate_synthetic_data
from .nem_api import fetch_nem_prices

__all__ = ["load_processed_data", "generate_synthetic_data", "fetch_nem_prices"]
