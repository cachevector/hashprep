import pandas as pd
from scipy.stats import chi2_contingency, f_oneway
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def summarize_interactions(df, include_plots=False):
    interactions = {}
    interactions["scatter_pairs"] = _scatter_plots_numeric(df, include_plots)
    interactions["numeric_correlations"] = _compute_correlation_matrices(
        df, include_plots
    )
    interactions["categorical_correlations"] = _compute_categorical_correlations(df)
    interactions["mixed_correlations"] = _compute_mixed_correlations(df)
    return interactions


def _scatter_plots_numeric(df, include_plots):
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    pairs = [
        (c1, c2)
        for i, c1 in enumerate(numeric_columns)
        for c2 in numeric_columns[i + 1 :]
    ]
    if not include_plots:
        return pairs

    plots = {}
    for c1, c2 in pairs:
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.scatterplot(data=df, x=c1, y=c2, ax=ax)
        ax.set_title(f"{c1} vs {c2}")
        ax.set_xlabel(c1)
        ax.set_ylabel(c2)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)
        plots[f"{c1}__{c2}"] = img_str

    return {"pairs": pairs, "plots": plots}


def _compute_correlation_matrices(df, include_plots):
    numeric_df = df.select_dtypes(include="number")
    corrs = {}
    if not numeric_df.empty:
        corrs["pearson"] = numeric_df.corr(method="pearson").to_dict()
        corrs["spearman"] = numeric_df.corr(method="spearman").to_dict()
        corrs["kendall"] = numeric_df.corr(method="kendall").to_dict()
        if include_plots:
            corrs["plots"] = {}
            for method in ["pearson", "spearman", "kendall"]:
                corr_matrix = numeric_df.corr(method=method)
                fig, ax = plt.subplots(figsize=(5, 4))
                sns.heatmap(
                    corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, ax=ax
                )
                ax.set_title(f"{method.capitalize()} Correlation")
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                buf.seek(0)
                img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
                plt.close(fig)
                corrs["plots"][method] = img_str
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
