import numpy as np
import pandas as pd

from ..config import DEFAULT_CONFIG
from .core import Issue

_DT_CFG = DEFAULT_CONFIG.datetime


def _coerce_datetime(series: pd.Series) -> pd.Series:
    """Return a datetime Series regardless of whether the source is datetime64 or object."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series.dropna()
    return pd.to_datetime(series, errors="coerce").dropna()


def _datetime_cols(analyzer) -> list[str]:
    """Return columns inferred as DateTime."""
    return [col for col, typ in analyzer.column_types.items() if typ == "DateTime"]


def _check_datetime_future_dates(analyzer) -> list[Issue]:
    """Flag datetime columns that contain values in the future (likely data errors)."""
    issues = []
    now = pd.Timestamp.now()

    for col in _datetime_cols(analyzer):
        dt = _coerce_datetime(analyzer.df[col])
        if dt.empty:
            continue

        future_count = int((dt > now).sum())
        if future_count == 0:
            continue

        future_ratio = future_count / len(dt)
        severity = "critical" if future_ratio > _DT_CFG.future_date_critical_ratio else "warning"
        impact = "high" if severity == "critical" else "medium"
        issues.append(
            Issue(
                category="datetime_future_dates",
                severity=severity,
                column=col,
                description=(
                    f"Column '{col}' has {future_count} future-dated values "
                    f"({future_ratio:.1%} of non-missing) — latest: {dt.max().date()}"
                ),
                impact_score=impact,
                quick_fix=(
                    "Options:\n"
                    "- Investigate source: Future dates often indicate data entry errors or clock skew.\n"
                    "- Cap to present: Replace future dates with today or NaN.\n"
                    "- Exclude rows: Drop records with future timestamps before training."
                ),
            )
        )
    return issues


def _check_datetime_gaps(analyzer) -> list[Issue]:
    """Detect anomalously large gaps in datetime columns (broken time series)."""
    issues = []

    for col in _datetime_cols(analyzer):
        dt = _coerce_datetime(analyzer.df[col]).sort_values()
        if len(dt) < _DT_CFG.min_rows_for_gap_check:
            continue

        diffs = dt.diff().dropna()
        if diffs.empty:
            continue

        # Work in total seconds for a unit-agnostic comparison
        diff_seconds = diffs.dt.total_seconds()
        median_gap = float(diff_seconds.median())
        if median_gap <= 0:
            continue

        max_gap = float(diff_seconds.max())
        ratio = max_gap / median_gap

        if ratio >= _DT_CFG.gap_multiplier_warning:
            severity = "critical" if ratio >= _DT_CFG.gap_multiplier_critical else "warning"
            impact = "high" if severity == "critical" else "medium"

            # Locate the gap for a human-readable description
            gap_idx = int(np.argmax(diff_seconds.values))
            gap_start = dt.iloc[gap_idx]
            gap_end = dt.iloc[gap_idx + 1]
            gap_days = (gap_end - gap_start).days

            issues.append(
                Issue(
                    category="datetime_gaps",
                    severity=severity,
                    column=col,
                    description=(
                        f"Column '{col}' has an anomalous gap of {gap_days} days "
                        f"({ratio:.0f}× the median gap) between {gap_start.date()} and {gap_end.date()}"
                    ),
                    impact_score=impact,
                    quick_fix=(
                        "Options:\n"
                        "- Investigate gap: May indicate missing data collection periods.\n"
                        "- Impute missing periods: Forward-fill or interpolate for time-series models.\n"
                        "- Flag as a feature: Create a binary 'gap_present' indicator.\n"
                        "- Segment model: Train separate models for each contiguous period."
                    ),
                )
            )
    return issues


def _check_datetime_monotonicity(analyzer) -> list[Issue]:
    """Warn when a datetime column that looks like a time-series index is non-monotonic."""
    issues = []

    for col in _datetime_cols(analyzer):
        dt = _coerce_datetime(analyzer.df[col])
        if len(dt) < _DT_CFG.min_rows_for_gap_check:
            continue

        # Only flag if the column has mostly unique values (i.e., likely an index/timestamp)
        unique_ratio = dt.nunique() / len(dt)
        if unique_ratio < 0.9:
            continue

        if not (dt.is_monotonic_increasing or dt.is_monotonic_decreasing):
            # Count out-of-order entries
            sorted_dt = dt.sort_values()
            out_of_order = int((dt.reset_index(drop=True) != sorted_dt.reset_index(drop=True)).sum())
            out_ratio = out_of_order / len(dt)
            severity = "warning"
            impact = "medium"
            issues.append(
                Issue(
                    category="datetime_monotonicity",
                    severity=severity,
                    column=col,
                    description=(
                        f"Column '{col}' is non-monotonic: {out_of_order} rows "
                        f"({out_ratio:.1%}) are out of temporal order"
                    ),
                    impact_score=impact,
                    quick_fix=(
                        "Options:\n"
                        "- Sort by this column: Restores temporal order before time-series modeling.\n"
                        "- Investigate duplicates: Non-monotonicity may reveal duplicate or misaligned records.\n"
                        "- Retain if intentional: Some datasets (e.g., event logs) are legitimately unordered."
                    ),
                )
            )
    return issues
