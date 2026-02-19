import numpy as np
import pandas as pd
from scipy.stats import chisquare, ks_2samp

from ..config import DEFAULT_CONFIG
from ..utils.logging import get_logger
from .core import Issue

_log = get_logger("checks.drift")

_DRIFT = DEFAULT_CONFIG.drift
CRITICAL_P_VALUE = _DRIFT.critical_p_value
MAX_CATEGORIES_FOR_CHI2 = _DRIFT.max_categories_for_chi2


def check_drift(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    threshold: float = _DRIFT.p_value,
) -> list[Issue]:
    """
    Check for distribution shift between two datasets.
    Uses Kolmogorov-Smirnov test for numeric columns and Chi-square for categorical.
    """
    if not isinstance(df_train, pd.DataFrame) or not isinstance(df_test, pd.DataFrame):
        raise TypeError("Both df_train and df_test must be pandas DataFrames")

    issues = []

    issues.extend(_check_numeric_drift(df_train, df_test, threshold))
    issues.extend(_check_categorical_drift(df_train, df_test, threshold))

    return issues


def _check_numeric_drift(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    threshold: float,
) -> list[Issue]:
    """Check numeric columns for distribution drift using KS-test."""
    issues = []
    num_cols = df_train.select_dtypes(include="number").columns

    for col in num_cols:
        if col not in df_test.columns:
            continue

        train_vals = df_train[col].dropna()
        test_vals = df_test[col].dropna()

        if len(train_vals) == 0 or len(test_vals) == 0:
            continue

        stat, p_val = ks_2samp(train_vals, test_vals)

        if p_val < threshold:
            severity = "critical" if p_val < CRITICAL_P_VALUE else "warning"
            issues.append(
                Issue(
                    category="dataset_drift",
                    severity=severity,
                    column=col,
                    description=f"Drift detected in numeric column '{col}' (KS p-value: {p_val:.4f})",
                    impact_score="high" if severity == "critical" else "medium",
                    quick_fix="Options:\n- Re-train model with recent data.\n- Investigate data collection differences.\n- Use drift-robust features.",
                )
            )

    return issues


def _check_categorical_drift(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    threshold: float,
) -> list[Issue]:
    """Check categorical columns for distribution drift using Chi-square test."""
    issues = []
    cat_cols = df_train.select_dtypes(include=["object", "category"]).columns

    for col in cat_cols:
        if col not in df_test.columns:
            continue

        train_counts = df_train[col].value_counts()
        test_counts = df_test[col].value_counts()

        new_categories = set(test_counts.index) - set(train_counts.index)
        if new_categories:
            sample_new = list(new_categories)[: _DRIFT.max_new_category_samples]
            issues.append(
                Issue(
                    category="dataset_drift",
                    severity="warning",
                    column=col,
                    description=f"New categories in test set for '{col}': {sample_new}{'...' if len(new_categories) > _DRIFT.max_new_category_samples else ''}",
                    impact_score="medium",
                    quick_fix="Handle unseen categories in preprocessing pipeline (e.g., OrdinalEncoder with unknown_value).",
                )
            )

        all_cats = list(set(train_counts.index) | set(test_counts.index))
        if len(all_cats) > MAX_CATEGORIES_FOR_CHI2:
            continue

        train_total = train_counts.sum()
        test_total = test_counts.sum()

        if train_total == 0 or test_total == 0:
            continue

        observed = []
        expected = []

        for cat in all_cats:
            observed.append(test_counts.get(cat, 0))
            train_freq = train_counts.get(cat, 0) / train_total
            expected.append(train_freq * test_total)

        observed_arr = np.array(observed, dtype=float)
        expected_arr = np.array(expected, dtype=float)

        expected_arr = np.where(expected_arr < 1e-10, 1e-10, expected_arr)

        try:
            chi2_stat, p_val = chisquare(observed_arr, f_exp=expected_arr)

            if p_val < threshold:
                severity = "critical" if p_val < CRITICAL_P_VALUE else "warning"
                issues.append(
                    Issue(
                        category="dataset_drift",
                        severity=severity,
                        column=col,
                        description=f"Drift detected in categorical column '{col}' (Chi-square p-value: {p_val:.4f})",
                        impact_score="high" if severity == "critical" else "medium",
                        quick_fix="Options:\n- Re-train model with recent data.\n- Investigate category distribution changes.\n- Consider rebalancing categories.",
                    )
                )
        except (ValueError, RuntimeWarning) as e:
            _log.debug("Chi-square drift test failed for '%s': %s", col, e)

    return issues
