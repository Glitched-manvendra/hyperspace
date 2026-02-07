"""
Data Loader Utilities — Orbital Nexus

Helpers for loading CSV/JSON datasets from the data/ folder.
Used by the fusion service to read raw and processed data.
"""

import os
import json
from pathlib import Path

import pandas as pd

# Project root is two levels up from this file
DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def load_csv(filename: str, subfolder: str = "raw") -> pd.DataFrame:
    """
    Load a CSV file from the data directory.

    Args:
        filename: Name of the CSV file (e.g., 'weather.csv')
        subfolder: 'raw' or 'processed'

    Returns:
        pandas DataFrame with the loaded data
    """
    filepath = DATA_DIR / subfolder / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found: {filepath}")
    return pd.read_csv(filepath, comment="#")


def load_json(filename: str, subfolder: str = "processed") -> dict:
    """
    Load a JSON file from the data directory.

    Args:
        filename: Name of the JSON file
        subfolder: 'raw' or 'processed'

    Returns:
        Parsed JSON as a dictionary
    """
    filepath = DATA_DIR / subfolder / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found: {filepath}")
    with open(filepath) as f:
        return json.load(f)


def list_datasets(subfolder: str = "raw") -> list[str]:
    """List all dataset files in a subfolder."""
    folder = DATA_DIR / subfolder
    if not folder.exists():
        return []
    return [f.name for f in folder.iterdir() if f.is_file() and f.name != ".gitkeep"]
