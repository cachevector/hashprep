import hashlib

import numpy as np
import pandas as pd

import hashprep


def get_dataset_preview(df):
    # replace NaN with None before conversion to dictionary
    df = df.replace({pd.NA: None, np.nan: None})
    head = df.head(5).to_dict(orient="records")
    tail = df.tail(5).to_dict(orient="records")
    sample = df.sample(min(10, len(df)), random_state=42).to_dict(orient="records")
    return {"head": head, "tail": tail, "sample": sample}


def summarize_dataset_info(df: pd.DataFrame) -> dict:
    rows = df.shape[0]
    cols = df.shape[1]
    total_cells = rows * cols
    missing_cells = int(df.isnull().sum().sum())
    total_memory_bytes = df.memory_usage(deep=True).sum()

    return {
        "dataset_info": {
            "rows": int(rows),
            "columns": int(cols),
            "memory_bytes": int(total_memory_bytes),
            "memory_kib": float(round(total_memory_bytes / 1024, 1)),
            "memory_mb": float(round(total_memory_bytes / 1024**2, 1)),
            "average_record_size_bytes": float(round(total_memory_bytes / rows, 1)) if rows > 0 else 0.0,
            "missing_cells": missing_cells,
            "total_cells": int(total_cells),
            "missing_percentage": float(round(missing_cells / total_cells * 100, 1)) if total_cells > 0 else 0.0,
        }
    }


def get_duplicate_info(df: pd.DataFrame) -> dict:
    """Return duplicate row count and percentage."""
    rows = len(df)
    duplicate_count = int(df.duplicated().sum())
    duplicate_percentage = float(round(duplicate_count / rows * 100, 1)) if rows > 0 else 0.0
    return {
        "duplicate_rows": duplicate_count,
        "duplicate_percentage": duplicate_percentage,
    }


def summarize_variable_type_counts(df: pd.DataFrame, column_types: dict[str, str]) -> dict[str, int]:
    """Count variables by inferred type."""
    type_counts = {
        "Numeric": 0,
        "Categorical": 0,
        "Text": 0,
        "DateTime": 0,
        "Boolean": 0,
        "Unsupported": 0,
    }
    for _col, typ in column_types.items():
        if typ in type_counts:
            type_counts[typ] += 1
        else:
            type_counts["Unsupported"] += 1
    return type_counts


def summarize_variable_types(df: pd.DataFrame, column_types: dict[str, str] | None = None) -> dict[str, str]:
    """
    Summarize column types using infer_types if column_types not provided.
    """
    if column_types is None:
        from ..utils.type_inference import infer_types

        column_types = infer_types(df)
    return column_types


def add_reproduction_info(df: pd.DataFrame) -> dict:
    """Generate reproduction metadata for the analysis."""
    dataset_hash = hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
    return {
        "dataset_hash": dataset_hash,
        "software_version": hashprep.__version__,
    }
