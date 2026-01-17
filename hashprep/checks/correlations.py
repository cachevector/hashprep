from .core import Issue
import pandas as pd
import numpy as np
from scipy.stats import f_oneway, spearmanr, pearsonr, kendalltau, chi2_contingency
from itertools import combinations
from .discretizer import Discretizer, DiscretizationType
from ..utils.type_inference import infer_types, is_usable_for_corr


# Thresholds
CORR_THRESHOLDS = {
    'numeric': {
        'spearman': {'warning': 0.7, 'critical': 0.95},
        'pearson': {'warning': 0.7, 'critical': 0.95},
        'kendall': {'warning': 0.6, 'critical': 0.85},  # Lower for Kendall (typically smaller values)
    },
    'categorical': {'warning': 0.5, 'critical': 0.8},
    'mixed': {'warning': 0.5, 'critical': 0.8},  # Updated to coefficient thresholds (matching categorical) for Cramer's V
}
CAT_MAX_DISTINCT = 50
LOW_CARD_NUM_THRESHOLD = 10  # From type_inference.py

def _cramers_v_corrected(table: pd.DataFrame) -> float:
    if table.empty or (table.shape[0] == 1 or table.shape[1] == 1):
        return 0.0
    chi2 = chi2_contingency(table, correction=True)[0]
    n = table.sum().sum()
    phi2 = chi2 / n
    r, k = table.shape
    with np.errstate(divide='ignore', invalid='ignore'):
        phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
        rcorr = r - ((r-1)**2)/(n-1)
        kcorr = k - ((k-1)**2)/(n-1)
        rkcorr = min((kcorr-1), (rcorr-1))
        if rkcorr == 0:
            return 1.0
        return np.sqrt(phi2corr / rkcorr)


def calculate_correlations(analyzer, thresholds=None):
    """
    Compute correlations using internal defaults: Spearman + Pearson for numerics,
    with Kendall added automatically for low-cardinality pairs.
    """
    if thresholds is None:
        thresholds = CORR_THRESHOLDS

    inferred_types = analyzer.column_types  # Use analyzer.column_types for inferred types dict
    issues = []

    numeric_cols = [col for col, typ in inferred_types.items() if
                    typ == 'Numeric' and is_usable_for_corr(analyzer.df[col])]
    cat_cols = [col for col, typ in inferred_types.items() if typ == 'Categorical' and
                1 < analyzer.df[col].nunique() <= CAT_MAX_DISTINCT and is_usable_for_corr(analyzer.df[col])]
    text_cols = [col for col, typ in inferred_types.items() if typ == 'Text']

    # Internal default methods
    default_methods = ['spearman', 'pearson']
    issues.extend(_check_numeric_correlation(analyzer, numeric_cols, thresholds['numeric'], default_methods))
    issues.extend(_check_categorical_correlation(analyzer, cat_cols, thresholds['categorical']))
    issues.extend(_check_mixed_correlation(analyzer, numeric_cols, cat_cols, thresholds['mixed']))

    return issues


def _check_numeric_correlation(analyzer, numeric_cols: list, thresholds: dict, methods: list):
    issues = []
    if len(numeric_cols) < 2:
        return issues

    num_df = analyzer.df[numeric_cols].dropna(how='all')
    corr_methods = {
        'spearman': lambda x, y: spearmanr(x, y),
        'pearson': lambda x, y: pearsonr(x, y),
        'kendall': lambda x, y: kendalltau(x, y)
    }

    for col1, col2 in combinations(numeric_cols, 2):
        series1, series2 = num_df[col1].dropna(), num_df[col2].dropna()
        common_idx = series1.index.intersection(series2.index)
        if len(common_idx) < 2:
            continue
        series1, series2 = series1.loc[common_idx], series2.loc[common_idx]

        # Spearman (default, robust)
        spearman_corr, spearman_p = spearmanr(series1, series2)
        spearman_corr = abs(spearman_corr)

        # Pearson (linear, for comparison)
        pearson_corr, pearson_p = pearsonr(series1, series2)
        pearson_corr = abs(pearson_corr)

        # Kendall (only for low-cardinality numerics)
        kendall_corr, kendall_p = None, None
        is_low_card = (series1.nunique() <= LOW_CARD_NUM_THRESHOLD or
                       series2.nunique() <= LOW_CARD_NUM_THRESHOLD)
        if is_low_card:
            kendall_corr, kendall_p = kendalltau(series1, series2)
            kendall_corr = abs(kendall_corr)

        # Flag if any metric exceeds threshold
        metrics = [('Spearman', spearman_corr, spearman_p, thresholds['spearman']),
                   ('Pearson', pearson_corr, pearson_p, thresholds['pearson'])]
        if kendall_corr is not None:
            metrics.append(('Kendall', kendall_corr, kendall_p, thresholds['kendall']))

        for method, corr, p_val, thresh in metrics:
            if corr > thresh['warning']:
                severity = 'critical' if corr > thresh['critical'] else 'warning'
                impact = 'high' if severity == 'critical' else 'medium'
                quick_fix = (
                    f"Options: \n- Drop one feature (e.g., {col2}): Reduces multicollinearity.\n- PCA/combine: Retains info.\n- Use tree-based models."
                    if severity == 'critical' else
                    f"Options: \n- Monitor in modeling.\n- Drop if redundant."
                )
                issues.append(Issue(
                    category="feature_correlation",
                    severity=severity,
                    column=f"{col1},{col2}",
                    description=f"Numeric columns '{col1}' and '{col2}' highly correlated ({method}: {corr:.3f}, p={p_val:.4f})",
                    impact_score=impact,
                    quick_fix=quick_fix,
                ))

    return issues


def _check_feature_correlation(
    analyzer, threshold: float = 0.95, critical_threshold: float = 0.98
):
    issues = []
    numeric_df = analyzer.df.select_dtypes(include="number")
    if numeric_df.empty:
        return issues
    corr_matrix = numeric_df.corr().abs()
    upper = corr_matrix.where(np.tril(np.ones(corr_matrix.shape)).astype(bool))
    correlated_pairs = [
        (col, row, float(val))
        for row in upper.index
        for col, val in upper[row].dropna().items()
        if val > threshold and col != row
    ]
    for col1, col2, corr in correlated_pairs:
        severity = "critical" if corr > critical_threshold else "warning"
        impact = "high" if severity == "critical" else "medium"
        quick_fix = (
            "Options: \n- Drop one feature: Reduces multicollinearity (Pros: Simplifies model; Cons: Loses info).\n- Combine features: Create composite feature (e.g., PCA) (Pros: Retains info; Cons: Less interpretable).\n- Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models)."
            if severity == "critical"
            else "Options: \n- Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info).\n- Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of multicollinearity).\n- Engineer feature: Combine or transform features (Pros: Reduces redundancy; Cons: Adds complexity)."
        )
        issues.append(
            Issue(
                category="feature_correlation",
                severity=severity,
                column=f"{col1},{col2}",
                description=f"Columns '{col1}' and '{col2}' are highly correlated ({corr:.2f})",
                impact_score=impact,
                quick_fix=quick_fix,
            )
        )
    return issues


def _check_categorical_correlation(analyzer, cat_cols: list, thresholds: dict):
    issues = []
    if len(cat_cols) < 2:
        return issues

    for col1, col2 in combinations(cat_cols, 2):
        table = pd.crosstab(analyzer.df[col1], analyzer.df[col2])
        cramers_v = _cramers_v_corrected(table)
        if cramers_v > thresholds['warning']:
            severity = 'critical' if cramers_v > thresholds['critical'] else 'warning'
            impact = 'high' if severity == 'critical' else 'medium'
            quick_fix = (
                "Options: \n- Drop one (less predictive). \n- Group categories. \n- Use trees (robust to assoc.)."
                if severity == 'critical' else
                "Options: \n- Monitor redundancy. \n- Re-encode."
            )
            issues.append(Issue(
                category="feature_correlation",
                severity=severity,
                column=f"{col1},{col2}",
                description=f"Categorical columns '{col1}' and '{col2}' highly associated (Cramer's V: {cramers_v:.3f})",
                impact_score=impact,
                quick_fix=quick_fix,
            ))
    return issues


def _check_mixed_correlation(analyzer, numeric_cols: list, cat_cols: list, thresholds: dict):
    issues = []
    if not numeric_cols or not cat_cols:
        return issues

    discretizer = Discretizer(DiscretizationType.UNIFORM, n_bins=10)
    df_disc = discretizer.discretize_dataframe(analyzer.df[numeric_cols + cat_cols])

    for num_col, cat_col in [(n, c) for n in numeric_cols for c in cat_cols]:
        table = pd.crosstab(df_disc[cat_col], df_disc[num_col])
        cramers_v = _cramers_v_corrected(table)
        if cramers_v > thresholds['warning']:
            severity = 'critical' if cramers_v > thresholds['critical'] else 'warning'
            impact = 'high' if severity == 'critical' else 'medium'
            quick_fix = (
                "Options: \n- Drop one. \n- Discretize/encode differently. \n- Use robust models."
                if severity == 'critical' else
                "Options: \n- Monitor in modeling."
            )
            issues.append(Issue(
                category="feature_correlation",
                severity=severity,
                column=f"{cat_col},{num_col}",
                description=f"Mixed columns '{cat_col}' (cat) and '{num_col}' (num) associated (Discretized Cramer's V: {cramers_v:.3f})",
                impact_score=impact,
                quick_fix=quick_fix,
            ))

    return issues