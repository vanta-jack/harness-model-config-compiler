"""
Curation, Search & Pinning Module

Handles:
- Vectorized regex filtering across model IDs and metadata
- Safe pagination slicing for Deepnote UI performance
- Pinning state management
"""

from __future__ import annotations

from typing import List, Optional, Tuple
import pandas as pd


def filter_by_regex(
    df: pd.DataFrame,
    regex_pattern: str = "*",
    search_column: str = "id",
) -> pd.DataFrame:
    """
    Filter DataFrame using regex pattern against a specified column.
    """
    if df.empty or not regex_pattern or regex_pattern.strip() in ("*", ""):
        return df
    
    pattern = regex_pattern.strip()
    # Normalize wildcard '*' to '.*' if passed as loose glob
    if pattern == "*":
        return df
    if not pattern.startswith(".*") and pattern.startswith("*"):
        pattern = "." + pattern

    try:
        mask = df[search_column].astype(str).str.contains(pattern, case=False, na=False, regex=True)
        return df[mask]
    except Exception:
        # Fallback to literal substring matching if regex syntax is invalid during typing
        return df[df[search_column].astype(str).str.contains(regex_pattern, case=False, na=False, regex=False)]


def paginate_models(
    df: pd.DataFrame,
    page_size: int | str = 10,
    page_number: int = 1,
) -> Tuple[pd.DataFrame, int, int]:
    """
    Slice DataFrame for interactive paginated UI.
    
    Returns:
        (page_df, total_rows, total_pages)
    """
    size = int(page_size) if str(page_size).isdigit() else 10
    total_rows = len(df)
    total_pages = max(1, (total_rows + size - 1) // size)
    
    page = max(1, min(page_number, total_pages))
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    
    return df.iloc[start_idx:end_idx], total_rows, total_pages


def pin_model(
    pinned_list: List[str],
    model_id: str,
    valid_ids: Optional[pd.Series | List[str]] = None,
) -> List[str]:
    """
    Append a model ID to the pinned list if valid and not already pinned.
    """
    target = model_id.strip()
    if not target or target in pinned_list:
        return pinned_list
    
    if valid_ids is not None and target not in set(valid_ids):
        return pinned_list
    
    return [*pinned_list, target]


def unpin_model(pinned_list: List[str], model_id: str) -> List[str]:
    """Remove a model ID from the pinned list."""
    target = model_id.strip()
    return [m for m in pinned_list if m != target]
