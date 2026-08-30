"""
Schema Profiling & Normalization Module

Handles:
- Profiling key population and missing attributes across 20k+ models
- Detecting schema discrepancies (context_length vs max_tokens, pricing formats)
- Applying explicit user overrides
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd


def profile_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profile key population and presence statistics across the dataset.
    
    Returns:
        DataFrame with columns: ['column', 'populated_count', 'missing_count', 'population_pct', 'sample_value']
    """
    if df.empty:
        return pd.DataFrame(columns=["column", "populated_count", "missing_count", "population_pct", "sample_value"])
    
    rows = []
    total = len(df)
    for col in df.columns:
        populated = df[col].notna().sum()
        missing = total - populated
        pct = (populated / total) * 100
        sample = df[col].dropna().iloc[0] if populated > 0 else None
        rows.append({
            "column": col,
            "populated_count": populated,
            "missing_count": missing,
            "population_pct": round(pct, 2),
            "sample_value": str(sample)[:50] if sample is not None else None,
        })
    
    return pd.DataFrame(rows).sort_values(by="population_pct", ascending=False)


def normalize_context_length(
    df: pd.DataFrame,
    default_context: int = 8192,
) -> pd.DataFrame:
    """
    Ensure a canonical `context_length` column exists across varied provider schemas.
    """
    normalized_df = df.copy()
    if "context_length" not in normalized_df.columns:
        if "max_tokens" in normalized_df.columns:
            normalized_df["context_length"] = normalized_df["max_tokens"]
        elif "max_input_tokens" in normalized_df.columns:
            normalized_df["context_length"] = normalized_df["max_input_tokens"]
        else:
            normalized_df["context_length"] = default_context
    else:
        normalized_df["context_length"] = normalized_df["context_length"].fillna(default_context)
    
    return normalized_df


def apply_overrides(
    df: pd.DataFrame,
    overrides: Optional[Dict[str, Dict[str, Any]]] = None,
) -> pd.DataFrame:
    """
    Apply model-specific overrides (e.g. `{"model_id": {"context_length": 32768}}`).
    """
    if not overrides:
        return df
    
    out_df = df.copy()
    for model_id, field_map in overrides.items():
        mask = out_df["id"] == model_id
        for field, val in field_map.items():
            if field not in out_df.columns:
                out_df[field] = None
            out_df.loc[mask, field] = val
    return out_df
