from .core import Issues
import pandas as pd
from scipy.stats import chi2_contingency, f_oneway
import numpy as np

def _check_feature_correlation(analyzer, threshold: float = 0.95, critical_threshold: float = 0.98):
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
            Issues(
                category="feature_correlation",
                severity=severity,
                column=f"{col1},{col2}",
                description=f"Columns '{col1}' and '{col2}' are highly correlated ({corr:.2f})",
                impact_score=impact,
                quick_fix=quick_fix,
            )
        )
    return issues

def _check_categorical_correlation(analyzer, threshold: float = 0.8, critical_threshold: float = 0.95):
    issues = []
    categorical = analyzer.df.select_dtypes(include="object").columns.tolist()
    for i, c1 in enumerate(categorical):
        for c2 in categorical[i + 1 :]:
            try:
                table = pd.crosstab(analyzer.df[c1], analyzer.df[c2])
                chi2, _, _, _ = chi2_contingency(table)
                n = table.sum().sum()
                phi2 = chi2 / n
                r, k = table.shape
                cramers_v = np.sqrt(phi2 / min(k - 1, r - 1))
                if cramers_v > threshold:
                    severity = "critical" if cramers_v > critical_threshold else "warning"
                    impact = "high" if severity == "critical" else "medium"
                    quick_fix = (
                        "Options: \n- Drop one feature: Avoids overfitting from high redundancy (Pros: Simplifies model; Cons: Loses info).\n- Engineer feature: Extract common patterns (e.g., group categories) (Pros: Retains info; Cons: Requires domain knowledge).\n- Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models)."
                        if severity == "critical"
                        else "Options: \n- Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info).\n- Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy).\n- Engineer feature: Group categories or encode differently (Pros: Reduces redundancy; Cons: Adds complexity)."
                    )
                    issues.append(
                        Issues(
                            category="feature_correlation",
                            severity=severity,
                            column=f"{c1},{c2}",
                            description=f"Columns '{c1}' and '{c2}' are highly associated (Cramer's V: {float(cramers_v):.2f})",
                            impact_score=impact,
                            quick_fix=quick_fix,
                        )
                    )
            except Exception:
                continue
    return issues

def _check_mixed_correlation(analyzer, p_threshold: float = 0.05, critical_p_threshold: float = 0.001):
    issues = []
    cat_cols = analyzer.df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()
    num_cols = analyzer.df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    for cat in cat_cols:
        for num in num_cols:
            groups = [
                analyzer.df.loc[analyzer.df[cat] == level, num].dropna().to_numpy()
                for level in analyzer.df[cat].dropna().unique()
                if len(analyzer.df.loc[analyzer.df[cat] == level, num].dropna()) > 1
            ]
            if len(groups) < 2 or all(np.var(g, ddof=1) == 0 for g in groups):
                continue
            try:
                f_stat, p_val = f_oneway(*groups)
                if p_val < p_threshold:
                    severity = (
                        "critical"
                        if p_val < critical_p_threshold and f_stat > 20.0
                        else "warning"
                    )
                    impact = "high" if severity == "critical" else "medium"
                    quick_fix = (
                        "Options: \n- Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info).\n- Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity).\n- Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models)."
                        if severity == "critical"
                        else "Options: \n- Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info).\n- Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy).\n- Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity)."
                    )
                    issues.append(
                        Issues(
                            category="feature_correlation",
                            severity=severity,
                            column=f"{cat},{num}",
                            description=f"Columns '{cat}' and '{num}' show strong association (F: {float(f_stat):.2f}, p: {float(p_val):.4f})",
                            impact_score=impact,
                            quick_fix=quick_fix,
                        )
                    )
            except Exception:
                continue
    return issues