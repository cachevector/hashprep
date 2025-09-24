from .core import Issues
import pandas as pd
import numpy as np

def _check_outliers(analyzer, z_threshold: float = 4.0):
    issues = []
    for col in analyzer.df.select_dtypes(include="number").columns:
        series = analyzer.df[col].dropna()
        if len(series) == 0:
            continue
        z_scores = (series - series.mean()) / series.std(ddof=0)
        outlier_count = int((abs(z_scores) > z_threshold).sum())
        if outlier_count > 0:
            outlier_ratio = float(outlier_count / len(series))
            severity = "critical" if outlier_ratio > 0.1 else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Remove outliers: Improves model stability (Pros: Reduces noise; Cons: Loses data).\n- Winsorize: Cap extreme values (Pros: Retains data; Cons: Alters distribution).\n- Transform: Apply log/sqrt to reduce impact (Pros: Preserves info; Cons: Changes interpretation)."
                if severity == "critical"
                else "Options: \n- Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming).\n- Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation).\n- Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models)."
            )
            issues.append(
                Issues(
                    category="outliers",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' has {outlier_count} potential outliers ({outlier_ratio:.1%} of non-missing values)",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_high_zero_counts(analyzer, threshold: float = 0.5, critical_threshold: float = 0.8):
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
                Issues(
                    category="high_zero_counts",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' has {zero_pct:.1%} zero values",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_extreme_text_lengths(analyzer, max_threshold: int = 1000, min_threshold: int = 1):
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
            severity = "critical" if extreme_ratio > 0.1 else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Truncate values: Cap extreme lengths (Pros: Stabilizes model; Cons: Loses info).\n- Filter outliers: Remove extreme entries (Pros: Reduces noise; Cons: Loses data).\n- Transform: Normalize lengths (e.g., log) (Pros: Retains info; Cons: Changes interpretation)."
                if severity == "critical"
                else "Options: \n- Investigate extremes: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming).\n- Transform: Truncate or normalize lengths (Pros: Retains info; Cons: Changes interpretation).\n- Retain and test: Use robust models (Pros: Keeps info; Cons: May affect sensitive models)."
            )
            issues.append(
                Issues(
                    category="extreme_text_lengths",
                    severity=severity,
                    column=col,
                    description=f"Column '{col}' has extreme lengths (min: {int(lengths.min())}, max: {int(lengths.max())}; {extreme_ratio:.1%} extreme)",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_datetime_skew(analyzer, threshold: float = 0.8):
    issues = []
    for col in analyzer.df.select_dtypes(include="datetime64").columns:
        series = pd.to_datetime(analyzer.df[col], errors="coerce").dropna()
        if series.empty:
            continue
        year_counts = series.dt.year.value_counts(normalize=True)
        if year_counts.max() > threshold:
            issues.append(
                Issues(
                    category="datetime_skew",
                    severity="warning",
                    column=col,
                    description=f"Column '{col}' has {float(year_counts.max()):.1%} in one year",
                    impact_score="medium",
                    quick_fix="Options: \n- Subsample data: Balance temporal distribution (Pros: Reduces bias; Cons: Loses data).\n- Engineer features: Extract year/month (Pros: Retains info; Cons: Adds complexity).\n- Retain and test: Use robust models (Pros: Keeps info; Cons: May skew results).",
                )
            )
    return issues