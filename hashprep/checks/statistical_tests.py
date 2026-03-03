"""
Statistical tests: normality (Shapiro-Wilk / D'Agostino-Pearson) and
variance homogeneity (Levene's test across target-column groups).
"""

import numpy as np
from scipy.stats import levene, normaltest, shapiro

from ..config import DEFAULT_CONFIG
from .core import Issue

_ST = DEFAULT_CONFIG.statistical_tests


def _run_normality_test(series) -> tuple[str, float, float]:
    """
    Return (test_name, statistic, p_value) for the most appropriate normality test.
    Uses Shapiro-Wilk for n <= shapiro_max_n, D'Agostino-Pearson otherwise.
    """
    n = len(series)
    if n <= _ST.shapiro_max_n:
        stat, p = shapiro(series)
        return "shapiro_wilk", float(stat), float(p)
    else:
        stat, p = normaltest(series)
        return "dagostino_pearson", float(stat), float(p)


def _check_normality(analyzer) -> list[Issue]:
    """
    Flag numeric columns whose distribution is significantly non-normal.
    Uses Shapiro-Wilk for n <= 5000, D'Agostino-Pearson for larger samples.
    Non-normality matters for linear models, t-tests, and certain imputation strategies.
    """
    issues = []

    for col in analyzer.df.select_dtypes(include="number").columns:
        series = analyzer.df[col].dropna()
        n = len(series)
        if n < _ST.normality_min_n:
            continue
        if series.nunique() <= 1:
            continue

        test_name, stat, p_val = _run_normality_test(series)

        if p_val < _ST.normality_p_value:
            # Severity: very small p → critical (strong evidence), otherwise warning
            severity = "critical" if p_val < 0.001 else "warning"
            impact = "high" if severity == "critical" else "medium"
            test_label = "Shapiro-Wilk" if test_name == "shapiro_wilk" else "D'Agostino-Pearson"

            issues.append(
                Issue(
                    category="normality",
                    severity=severity,
                    column=col,
                    description=(
                        f"Column '{col}' is non-normal ({test_label}: stat={stat:.4f}, p={p_val:.4g}, n={n})"
                    ),
                    impact_score=impact,
                    quick_fix=(
                        "Options:\n"
                        "- Transform: Log, sqrt, or Box-Cox/Yeo-Johnson often normalise skewed data.\n"
                        "- Use robust models: Tree-based models (XGBoost, RF) make no normality assumption.\n"
                        "- Normalise for linear models: Required for OLS residuals and LDA.\n"
                        "- Investigate outliers: Extreme values are a common cause of non-normality."
                    ),
                )
            )

    return issues


def _check_variance_homogeneity(analyzer) -> list[Issue]:
    """
    Run Levene's test across groups defined by the target column.
    Unequal variances (heteroscedasticity) across classes violate assumptions of
    linear discriminant analysis and ANOVA; they also indicate scale differences
    that may harm distance-based models.

    Only runs when a target column is set and has at least 2 groups with
    sufficient data.
    """
    issues = []

    if analyzer.target_col is None:
        return issues

    target = analyzer.df[analyzer.target_col].dropna()
    groups_labels = target.unique()

    for col in analyzer.df.select_dtypes(include="number").columns:
        if col == analyzer.target_col:
            continue

        series = analyzer.df[col]

        # Build per-group arrays, filtering out groups that are too small
        groups = []
        for label in groups_labels:
            mask = analyzer.df[analyzer.target_col] == label
            grp = series[mask].dropna().values
            if len(grp) >= _ST.levene_min_group_size:
                groups.append(grp)

        if len(groups) < 2:
            continue

        try:
            stat, p_val = levene(*groups, center="median")  # median-centre is most robust
        except ValueError:
            continue

        if p_val < _ST.levene_p_value:
            # Compute per-group stds to add colour to the description
            stds = [float(np.std(g, ddof=1)) for g in groups]
            std_ratio = max(stds) / min(stds) if min(stds) > 0 else float("inf")
            severity = "critical" if std_ratio > 3.0 else "warning"
            impact = "high" if severity == "critical" else "medium"

            issues.append(
                Issue(
                    category="variance_homogeneity",
                    severity=severity,
                    column=col,
                    description=(
                        f"Column '{col}' has unequal variances across '{analyzer.target_col}' groups "
                        f"(Levene: stat={stat:.4f}, p={p_val:.4g}; std ratio={std_ratio:.2f}×)"
                    ),
                    impact_score=impact,
                    quick_fix=(
                        "Options:\n"
                        "- Scale per class: Normalise within each target group before training.\n"
                        "- Transform feature: Log or sqrt often equalises spread.\n"
                        "- Use Welch's t-test / robust ANOVA: Accounts for unequal variances.\n"
                        "- Use tree-based models: Decision trees are invariant to feature scaling."
                    ),
                )
            )

    return issues
