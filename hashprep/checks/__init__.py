from typing import List, Optional

from .core import Issues
from .leakage import _check_data_leakage, _check_target_leakage_patterns
from .missing_values import _check_high_missing_values, _check_empty_columns, _check_dataset_missingness, \
    _check_missing_patterns
from .columns import _check_single_value_columns, _check_high_cardinality, _check_duplicates, _check_mixed_data_types
from .outliers import _check_outliers, _check_high_zero_counts, _check_extreme_text_lengths, _check_datetime_skew
from .correlations import calculate_correlations
from .imbalance import _check_class_imbalance

CHECKS = {
    "data_leakage": _check_data_leakage,
    "high_missing_values": _check_high_missing_values,
    "empty_columns": _check_empty_columns,
    "single_value_columns": _check_single_value_columns,
    "target_leakage_patterns": _check_target_leakage_patterns,
    "class_imbalance": _check_class_imbalance,
    "high_cardinality": _check_high_cardinality,
    "duplicates": _check_duplicates,
    "mixed_data_types": _check_mixed_data_types,
    "outliers": _check_outliers,
    "dataset_missingness": _check_dataset_missingness,
    "high_zero_counts": _check_high_zero_counts,
    "extreme_text_lengths": _check_extreme_text_lengths,
    "datetime_skew": _check_datetime_skew,
    "missing_patterns": _check_missing_patterns,
}

CORRELATION_CHECKS = {"feature_correlation", "categorical_correlation", "mixed_correlation"}


def run_checks(analyzer, checks_to_run: List[str]):
    issues = []
    correlation_requested = False

    for check in checks_to_run:
        if check in CORRELATION_CHECKS:
            correlation_requested = True
            continue  # Skip individual correlation checks; handle via calculate_correlations
        if check in CHECKS:
            issues.extend(CHECKS[check](analyzer))

    if correlation_requested:
        issues.extend(calculate_correlations(analyzer))

    return issues