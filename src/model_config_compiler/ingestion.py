"""
Ingestion & Dataset Management Module

Handles:
- Discovering local datasets matching `<provider>-models-<MMDDYY>.json`
- Ingesting models from live OpenAI-compatible `/models` endpoints
- Parsing raw JSON envelopes into uniform dictionaries / DataFrames
- Snapshotting timestamped dataset files
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

DATASET_PATTERN = re.compile(r"^(?P<provider>[a-zA-Z0-9_\-]+)-models-(?P<date>\d{6})\.json$")


@dataclass
class DatasetMetadata:
    """Metadata extracted from a standardized dataset filename."""
    provider: str
    date_str: str
    file_path: Path

    @property
    def formatted_date(self) -> str:
        """Parse MMDDYY into YYYY-MM-DD format if possible."""
        try:
            dt = datetime.strptime(self.date_str, "%m%d%y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return self.date_str


def parse_dataset_filename(filename_or_path: str | Path) -> Optional[DatasetMetadata]:
    """
    Parse a filename matching `<provider>-models-<MMDDYY>.json`.
    
    Returns:
        DatasetMetadata if matched, None otherwise.
    """
    path = Path(filename_or_path)
    match = DATASET_PATTERN.match(path.name)
    if not match:
        return None
    return DatasetMetadata(
        provider=match.group("provider"),
        date_str=match.group("date"),
        file_path=path,
    )


def discover_datasets(directory: str | Path = "datasets") -> List[DatasetMetadata]:
    """
    Scan a directory for all datasets matching `<provider>-models-<MMDDYY>.json`.
    
    Returns:
        List of DatasetMetadata objects sorted by filename.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    results = []
    for file in dir_path.glob("*.json"):
        meta = parse_dataset_filename(file)
        if meta:
            results.append(meta)
    return sorted(results, key=lambda x: x.file_path.name)


def unwrap_model_envelope(raw_data: Any) -> List[Dict[str, Any]]:
    """
    Unwrap varied API response envelopes (OpenAI `data`, aggregator `models`, or raw list).
    """
    if isinstance(raw_data, list):
        return raw_data
    if isinstance(raw_data, dict):
        if "data" in raw_data and isinstance(raw_data["data"], list):
            return raw_data["data"]
        if "models" in raw_data and isinstance(raw_data["models"], list):
            return raw_data["models"]
    raise ValueError("Unrecognized JSON envelope structure for models list.")


def load_dataset(file_path: str | Path) -> Tuple[pd.DataFrame, Optional[DatasetMetadata]]:
    """
    Load a local dataset JSON file into a pandas DataFrame.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    records = unwrap_model_envelope(data)
    df = pd.DataFrame(records)
    metadata = parse_dataset_filename(path)
    return df, metadata


def fetch_live_models(
    endpoint: str,
    api_key: Optional[str] = None,
    timeout_seconds: int = 15,
) -> List[Dict[str, Any]]:
    """
    Query an OpenAI-compatible `/models` endpoint.
    """
    url = f"{endpoint.rstrip('/')}/models"
    headers: Dict[str, str] = {
        "Accept": "application/json, text/event-stream"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    res = requests.get(url, headers=headers, timeout=timeout_seconds)
    res.raise_for_status()
    data = res.json()
    return unwrap_model_envelope(data)


def save_dataset_snapshot(
    records: List[Dict[str, Any]],
    provider: str,
    output_dir: str | Path = "datasets",
    custom_date: Optional[str] = None,
) -> Path:
    """
    Save records as a versioned snapshot `<provider>-models-<MMDDYY>.json`.
    """
    dir_path = Path(output_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    date_str = custom_date or datetime.now().strftime("%m%d%y")
    filename = f"{provider.lower()}-models-{date_str}.json"
    file_path = dir_path / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"data": records}, f, indent=2)
    
    return file_path
