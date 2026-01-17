import pandas as pd
import numpy as np
from typing import Dict, List
from scipy.stats import chi2_contingency  # For potential future use

# Config-like thresholds (mimic ydata's Settings; tune as needed)
CONFIG = {
    'cat_cardinality_threshold': 50,  # Max unique for Categorical (ydata default ~50)
    'cat_percentage_threshold': 0.05,  # % unique for Categorical
    'num_low_cat_threshold': 10,       # Low unique numerics → Categorical
    'bool_mappings': {'true': True, 'false': False, 'yes': True, 'no': False, 't': True, 'f': False},  # For bool inference
}

def infer_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infer semantic types per ydata logic.
    Returns: {col: 'Numeric' | 'Categorical' | 'Text' | 'Unsupported'}
    """
    types = {}
    for col in df.columns:
        series = df[col].dropna()
        if series.empty:
            types[col] = 'Unsupported'
            continue

        # Numeric inference (ydata's Numeric.contains_op + numeric_is_category)
        if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
            n_unique = series.nunique()
            if 1 <= n_unique <= CONFIG['num_low_cat_threshold']:
                types[col] = 'Categorical'  # Low-card numeric → Categorical (e.g., SibSp, Parch)
            else:
                types[col] = 'Numeric'  # High-card numeric (e.g., Age, Fare)

        # String/Text inference (ydata's Text.contains_op + string_is_category)
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            n_unique = series.nunique()
            unique_pct = n_unique / len(series)
            is_bool = all(s.lower() in CONFIG['bool_mappings'] for s in series[:5])  # Quick bool check
            if is_bool:
                types[col] = 'Categorical'  # Bool-like → Categorical
            elif 1 <= n_unique <= CONFIG['cat_cardinality_threshold'] and unique_pct < CONFIG['cat_percentage_threshold']:
                types[col] = 'Categorical'  # Low-card string → Categorical (e.g., Sex, Embarked)
            else:
                types[col] = 'Text'  # High-card/unique → Text (e.g., Name, Cabin, Ticket)

        # Categorical dtype
        elif pd.api.types.is_categorical_dtype(series):
            types[col] = 'Categorical'

        else:
            types[col] = 'Unsupported'

    return types

# Helper: Check if series is constant/empty (skip corr)
def is_usable_for_corr(series: pd.Series) -> bool:
    return series.nunique() > 1 and len(series.dropna()) > 1