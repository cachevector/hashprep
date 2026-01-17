import pandas as pd
from scipy.stats import chi2_contingency, f_oneway
import numpy as np


def summarize_interactions(df):
    interactions = {}
    interactions["scatter_pairs"] = _scatter_plots_numeric(df)
    interactions["numeric_correlations"] = _compute_correlation_matrices(df)
    interactions["categorical_correlations"] = _compute_categorical_correlations(df)
    interactions["mixed_correlations"] = _compute_mixed_correlations(df)
    return interactions


def _scatter_plots_numeric(df):
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    pairs = [
        (c1, c2)
        for i, c1 in enumerate(numeric_columns)
        for c2 in numeric_columns[i + 1 :]
    ]
    return pairs


def _compute_correlation_matrices(df):
    numeric_df = df.select_dtypes(include="number")
    corrs = {}
    if not numeric_df.empty:
        corrs["pearson"] = numeric_df.corr(method="pearson").to_dict()
        corrs["spearman"] = numeric_df.corr(method="spearman").to_dict()
        corrs["kendall"] = numeric_df.corr(method="kendall").to_dict()
    return corrs


def _compute_categorical_correlations(df):
    categorical = df.select_dtypes(include="object").columns.tolist()
    results = {}
    for i, c1 in enumerate(categorical):
        for c2 in categorical[i + 1 :]:
            try:
                table = pd.crosstab(df[c1], df[c2])
                chi2, _, _, _ = chi2_contingency(table)
                n = table.sum().sum()
                phi2 = chi2 / n
                r, k = table.shape
                cramers_v = (phi2 / min(k - 1, r - 1)) ** 0.5
                results[f"{c1}__{c2}"] = float(cramers_v)
            except Exception:
                continue
    return results


def _compute_mixed_correlations(df):
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    mixed_corr = {}
    for cat in cat_cols:
        for num in num_cols:
            groups = [
                df.loc[df[cat] == level, num].dropna().to_numpy()
                for level in df[cat].dropna().unique()
                if len(df.loc[df[cat] == level, num].dropna()) > 1
            ]
            if len(groups) < 2 or all(np.var(g, ddof=1) == 0 for g in groups):
                continue
            try:
                f_stat, p_val = f_oneway(*groups)
                mixed_corr[f"{cat}__{num}"] = {
                    "f_stat": float(f_stat),
                    "p_value": float(p_val),
                }
            except Exception as e:
                mixed_corr[f"{cat}__{num}"] = {"error": str(e)}
    return mixed_corr
