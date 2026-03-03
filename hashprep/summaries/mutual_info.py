"""
Mutual information between each feature and the target column.

Uses sklearn's mutual_info_classif (categorical target) or
mutual_info_regression (numeric target). Categorical features are
label-encoded before scoring.
"""

import pandas as pd
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from sklearn.preprocessing import LabelEncoder

from ..config import DEFAULT_CONFIG
from ..utils.logging import get_logger

_log = get_logger("summaries.mutual_info")
_MI = DEFAULT_CONFIG.mutual_info


def summarize_mutual_information(
    df: pd.DataFrame,
    target_col: str,
    column_types: dict[str, str],
) -> dict:
    """
    Compute mutual information between every feature and the target column.

    Returns a dict:
      {
        "target": target_col,
        "task": "classification" | "regression",
        "scores": {col: mi_score, ...},   # nats, sorted descending
      }
    or an empty dict when MI cannot be computed (too few samples, bad target, etc.).
    """
    if target_col not in df.columns:
        return {}

    target_type = column_types.get(target_col, "Unsupported")
    n = len(df.dropna(subset=[target_col]))
    if n < _MI.min_samples_for_mi:
        return {}

    # Determine task type
    if target_type in ("Numeric",):
        task = "regression"
        mi_fn = mutual_info_regression
    else:
        task = "classification"
        mi_fn = mutual_info_classif

    # Build feature matrix — include Numeric and low-cardinality Categorical cols
    feature_cols = []
    discrete_mask = []

    for col in df.columns:
        if col == target_col:
            continue
        typ = column_types.get(col, "Unsupported")
        if typ == "Numeric":
            feature_cols.append(col)
            discrete_mask.append(False)
        elif typ == "Categorical" and df[col].nunique() <= _MI.max_categories_for_mi:
            feature_cols.append(col)
            discrete_mask.append(True)

    if not feature_cols:
        return {}

    # Build X: label-encode categoricals, drop rows missing target
    sub = df[feature_cols + [target_col]].dropna(subset=[target_col])
    X = sub[feature_cols].copy()

    for col, is_discrete in zip(feature_cols, discrete_mask):
        if is_discrete:
            le = LabelEncoder()
            filled = X[col].fillna("__missing__").astype(str)
            X[col] = le.fit_transform(filled)
        else:
            X[col] = X[col].fillna(X[col].median())

    y_raw = sub[target_col]
    if task == "classification":
        le_y = LabelEncoder()
        y = le_y.fit_transform(y_raw.fillna("__missing__").astype(str))
    else:
        y = y_raw.values

    try:
        mi_scores = mi_fn(X.values, y, discrete_features=discrete_mask, random_state=0)
    except Exception as e:
        _log.debug("Mutual information computation failed: %s", e)
        return {}

    scores = {col: float(score) for col, score in zip(feature_cols, mi_scores)}
    # Sort descending by MI score
    scores = dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))

    return {
        "target": target_col,
        "task": task,
        "scores": scores,
    }
