from .columns import _check_duplicates, _check_high_cardinality, _check_mixed_data_types, _check_single_value_columns
from .core import Issue as Issue
from .correlations import calculate_correlations
from .distribution import _check_uniform_distribution, _check_unique_values
from .drift import check_drift
from .imbalance import _check_class_imbalance
from .leakage import _check_data_leakage, _check_target_leakage_patterns
from .missing_values import (
    _check_dataset_missingness,
    _check_empty_columns,
    _check_high_missing_values,
    _check_missing_patterns,
)
from .outliers import (
    _check_constant_length,
    _check_datetime_skew,
    _check_empty_dataset,
    _check_extreme_text_lengths,
    _check_high_zero_counts,
    _check_infinite_values,
    _check_outliers,
    _check_skewness,
)


def _check_dataset_drift(analyzer):
    """Wrapper for drift detection that uses analyzer's comparison_df."""
    if hasattr(analyzer, "comparison_df") and analyzer.comparison_df is not None:
        return check_drift(analyzer.df, analyzer.comparison_df)
    return []


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
    "skewness": _check_skewness,
    "dataset_drift": _check_dataset_drift,
    "uniform_distribution": _check_uniform_distribution,
    "unique_values": _check_unique_values,
    "infinite_values": _check_infinite_values,
    "constant_length": _check_constant_length,
    "empty_dataset": _check_empty_dataset,
}

CORRELATION_CHECKS = {"feature_correlation", "categorical_correlation", "mixed_correlation"}


def run_checks(analyzer, checks_to_run: list[str]):
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
