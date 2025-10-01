from typing import Optional, Dict

import pandas as pd
import numpy as np
import hashlib


def get_dataset_preview(df):
    # replace NaN with None before conversion to dictionary
    df = df.replace({pd.NA: None, np.nan: None})
    head = df.head().to_dict(orient="records")
    tail = df.tail().to_dict(orient="records")
    sample = df.sample(min(10, len(df))).to_dict(orient="records")
    return {"head": head, "tail": tail, "sample": sample}


def summarize_dataset_info(df):
    return {
        "dataset_info": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "memory_mb": float(round(df.memory_usage(deep=True).sum() / 1024**2, 1)),
            "missing_cells": int(df.isnull().sum().sum()),
            "total_cells": int(df.shape[0] * df.shape[1]),
            "missing_percentage": float(
                round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2)
            ),
        }
    }


def summarize_variable_types(df: pd.DataFrame, column_types: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Summarize column types using infer_types if column_types not provided.
    """
    if column_types is None:
        from ..checks.type_inference import infer_types
        column_types = infer_types(df)
    return column_types


def add_reproduction_info(df):
    dataset_hash = hashlib.md5(
        pd.util.hash_pandas_object(df, index=True).values
    ).hexdigest()
    timestamp = pd.Timestamp.now().isoformat()
    return {"dataset_hash": dataset_hash, "analysis_timestamp": timestamp}



