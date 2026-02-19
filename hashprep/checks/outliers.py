from .core import Issue
import pandas as pd
import numpy as np
from ..config import DEFAULT_CONFIG

_THRESHOLDS = DEFAULT_CONFIG.outliers

def _check_outliers(analyzer, z_threshold: float = _THRESHOLDS.z_score):
    issues = []
    for col in analyzer.df.select_dtypes(include="number").columns:
        series = analyzer.df[col].dropna()
        if len(series) == 0:
            continue
        z_scores = (series - series.mean()) / series.std(ddof=0)
        outlier_count = int((abs(z_scores) > z_threshold).sum())
        if outlier_count > 0:
            outlier_ratio = float(outlier_count / len(series))
            severity = "critical" if outlier_ratio > _THRESHOLDS.outlier_ratio_critical else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Remove outliers: Improves model stability (Pros: Reduces noise; Cons: Loses data).\n- Winsorize: Cap extreme values (Pros: Retains data; Cons: Alters distribution).\n- Transform: Apply log/sqrt to reduce impact (Pros: Preserves info; Cons: Changes interpretation)."
                if severity == "critical"
                else "Options: \n- Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming).\n- Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation).\n- Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models)."
            )
            issues.append(
                Issue(
                    category="outliers",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' has {outlier_count} potential outliers ({outlier_ratio:.1%} of non-missing values)",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_high_zero_counts(analyzer, threshold: float = _THRESHOLDS.zero_count_warning, critical_threshold: float = _THRESHOLDS.zero_count_critical):
    issues = []
    for col in analyzer.df.select_dtypes(include="number").columns:
        series = analyzer.df[col].dropna()
        if len(series) == 0:
            continue
        zero_pct = float((series == 0).mean())
        if zero_pct > threshold:
            severity = "critical" if zero_pct > critical_threshold else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Drop column: If zeros are not meaningful (Pros: Simplifies model; Cons: Loses info).\n- Transform: Use binary indicator or log transform (Pros: Retains info; Cons: Changes interpretation).\n- Verify zeros: Check if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming)."
                if severity == "critical"
                else "Options: \n- Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity).\n- Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results).\n- Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming)."
            )
            issues.append(
                Issue(
                    category="high_zero_counts",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' has {zero_pct:.1%} zero values",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_extreme_text_lengths(analyzer, max_threshold: int = _THRESHOLDS.text_length_max, min_threshold: int = _THRESHOLDS.text_length_min):
    issues = []
    for col in analyzer.df.select_dtypes(include="object").columns:
        series = analyzer.df[col].dropna().astype(str)
        if series.empty:
            continue
        lengths = series.str.len()
        if lengths.max() > max_threshold or lengths.min() < min_threshold:
            extreme_ratio = float(
                ((lengths > max_threshold) | (lengths < min_threshold)).mean()
            )
            severity = "critical" if extreme_ratio > _THRESHOLDS.extreme_ratio_critical else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Truncate values: Cap extreme lengths (Pros: Stabilizes model; Cons: Loses info).\n- Filter outliers: Remove extreme entries (Pros: Reduces noise; Cons: Loses data).\n- Transform: Normalize lengths (e.g., log) (Pros: Retains info; Cons: Changes interpretation)."
                if severity == "critical"
                else "Options: \n- Investigate extremes: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming).\n- Transform: Truncate or normalize lengths (Pros: Retains info; Cons: Changes interpretation).\n- Retain and test: Use robust models (Pros: Keeps info; Cons: May affect sensitive models)."
            )
            issues.append(
                Issue(
                    category="extreme_text_lengths",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' has extreme lengths (min: {int(lengths.min())}, max: {int(lengths.max())}; {extreme_ratio:.1%} extreme)",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_skewness(analyzer, skew_threshold: float = _THRESHOLDS.skewness_warning, critical_skew_threshold: float = _THRESHOLDS.skewness_critical):
    issues = []
    for col in analyzer.df.select_dtypes(include="number").columns:
        series = analyzer.df[col].dropna()
        if len(series) < _THRESHOLDS.min_sample_size:
            continue
        skewness = float(series.skew())
        abs_skew = abs(skewness)
        
        if abs_skew > skew_threshold:
            severity = "critical" if abs_skew > critical_skew_threshold else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Log transformation: Handles right skew (Pros: Normalizes; Cons: Only for positive).\n- Box-Cox/Yeo-Johnson: General power transforms (Pros: Robust; Cons: More complex).\n- Retain: Some models (trees) handle skewness well."
                if severity == "critical"
                else "Options: \n- Square root transform: Reduces moderate skew.\n- Monitor: Evaluate model performance on skewed data."
            )
            issues.append(
                Issue(
                    category="skewness",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' is highly skewed (skewness: {skewness:.2f})",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_datetime_skew(analyzer, threshold: float = _THRESHOLDS.datetime_skew):
    issues = []
    for col in analyzer.df.select_dtypes(include="datetime64").columns:
        series = pd.to_datetime(analyzer.df[col], errors="coerce").dropna()
        if series.empty:
            continue
        year_counts = series.dt.year.value_counts(normalize=True)
        if year_counts.max() > threshold:
            issues.append(
                Issue(
                    category="datetime_skew",
                    severity="warning",
                    column=col,
                    description=f"Column '{col}' has {float(year_counts.max()):.1%} in one year",
                    impact_score="medium",
                    quick_fix="Options: \n- Subsample data: Balance temporal distribution (Pros: Reduces bias; Cons: Loses data).\n- Engineer features: Extract year/month (Pros: Retains info; Cons: Adds complexity).\n- Retain and test: Use robust models (Pros: Keeps info; Cons: May skew results).",
                )
            )
    return issues


def _check_infinite_values(analyzer, threshold: float = _THRESHOLDS.infinite_ratio_critical):
    """Detect columns with infinite values."""
    issues = []
    for col in analyzer.df.select_dtypes(include="number").columns:
        series = analyzer.df[col]
        inf_count = int(np.isinf(series).sum())
        if inf_count > 0:
            inf_ratio = inf_count / len(series)
            severity = "critical" if inf_ratio > threshold else "warning"
            impact = "high" if severity == "critical" else "medium"
            issues.append(
                Issue(
                    category="infinite_values",
                    severity=severity,
                    column=col,
                    description=f"'{col}' has {inf_count} infinite values ({inf_ratio:.1%})",
                    impact_score=impact,
                    quick_fix=(
                        "Options:\n"
                        "- Replace with NaN: Treat as missing (Pros: Clean; Cons: Loses info).\n"
                        "- Replace with max/min: Cap to finite bounds (Pros: Retains data; Cons: Alters distribution).\n"
                        "- Investigate source: Find cause of infinities (Pros: Root cause fix; Cons: Time-consuming)."
                    ),
                )
            )
    return issues


def _check_constant_length(analyzer, threshold: float = _THRESHOLDS.constant_length_ratio):
    """Detect string columns where all values have the same length (e.g., IDs, codes)."""
    issues = []
    for col in analyzer.df.select_dtypes(include="object").columns:
        series = analyzer.df[col].dropna().astype(str)
        if len(series) < _THRESHOLDS.min_sample_size:
            continue
        lengths = series.str.len()
        most_common_length_ratio = lengths.value_counts(normalize=True).iloc[0] if len(lengths) > 0 else 0

        if most_common_length_ratio >= threshold:
            most_common_length = int(lengths.mode().iloc[0])
            issues.append(
                Issue(
                    category="constant_length",
                    severity="warning",
                    column=col,
                    description=f"'{col}' has constant length ({most_common_length} chars for {most_common_length_ratio:.1%} of values)",
                    impact_score="low",
                    quick_fix=(
                        "Options:\n"
                        "- Likely an ID/code: Consider dropping if not predictive.\n"
                        "- Extract patterns: Parse for meaningful substrings.\n"
                        "- Verify: Constant length may indicate structured data."
                    ),
                )
            )
    return issues


def _check_empty_dataset(analyzer):
    """Check if the dataset is empty or has no valid data."""
    issues = []
    if len(analyzer.df) == 0:
        issues.append(
            Issue(
                category="empty_dataset",
                severity="critical",
                column="__all__",
                description="Dataset is empty (0 rows)",
                impact_score="high",
                quick_fix="The dataset has no data. Verify the data source and loading process.",
            )
        )
    elif analyzer.df.dropna(how="all").empty:
        issues.append(
            Issue(
                category="empty_dataset",
                severity="critical",
                column="__all__",
                description="All rows contain only missing values",
                impact_score="high",
                quick_fix="All data is missing. Check data extraction and verify the source.",
            )
        )
    return issues