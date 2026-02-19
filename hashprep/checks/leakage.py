from .core import Issue
import pandas as pd
from scipy.stats import chi2_contingency, f_oneway
import numpy as np
from ..config import DEFAULT_CONFIG

_LEAK = DEFAULT_CONFIG.leakage

def _check_data_leakage(analyzer):
    issues = []
    if analyzer.target_col and analyzer.target_col in analyzer.df.columns:
        target = analyzer.df[analyzer.target_col]
        for col in analyzer.df.columns:
            if col == analyzer.target_col:
                continue
            if analyzer.df[col].equals(target):
                issues.append(
                    Issue(
                        category="data_leakage",
                        severity="critical",
                        column=col,
                        description=f"Column '{col}' is identical to target '{analyzer.target_col}'",
                        impact_score="high",
                        quick_fix="Options: \n- Drop column: Prevents data leakage (Pros: Ensures model integrity; Cons: Loses potential feature info).\n- Verify data collection: Ensure column isn't target-derived (Pros: Validates data; Cons: Time-consuming).",
                    )
                )
    return issues

def _check_target_leakage_patterns(analyzer):
    issues = []
    if analyzer.target_col and analyzer.target_col in analyzer.df.columns:
        target = analyzer.df[analyzer.target_col]
        # Numeric target
        if pd.api.types.is_numeric_dtype(target):
            numeric_cols = analyzer.df.select_dtypes(include="number").drop(
                columns=[analyzer.target_col], errors="ignore"
            )
            if not numeric_cols.empty:
                corrs = numeric_cols.corrwith(target).abs()
                for col, corr in corrs.items():
                    severity = (
                        "critical" if corr > _LEAK.numeric_critical else "warning" if corr > _LEAK.numeric_warning else None
                    )
                    if severity:
                        impact = "high" if severity == "critical" else "medium"
                        quick_fix = (
                            "Options: \n- Drop column: Prevents target leakage (Pros: Ensures model integrity; Cons: Loses feature info).\n- Verify feature: Check if correlation is valid or data-derived (Pros: Validates data; Cons: Time-consuming)."
                            if severity == "critical"
                            else "Options: \n- Drop column: Reduces leakage risk (Pros: Safer model; Cons: May lose predictive info).\n- Retain and test: Use robust models (e.g., trees) and evaluate (Pros: Keeps potential signal; Cons: Risk of overfitting).\n- Engineer feature: Transform to reduce correlation (Pros: Retains info; Cons: Adds complexity)."
                        )
                        issues.append(
                            Issue(
                                category="target_leakage",
                                severity=severity,
                                column=col,
                                description=f"Column '{col}' highly correlated with target ({float(corr):.2f})",
                                impact_score=impact,
                                quick_fix=quick_fix,
                            )
                        )
        # Categorical target
        else:
            cat_cols = analyzer.df.select_dtypes(include="object").drop(
                columns=[analyzer.target_col], errors="ignore"
            )
            for col in cat_cols.columns:
                try:
                    table = pd.crosstab(target, analyzer.df[col])
                    chi2, _, _, _ = chi2_contingency(table)
                    n = table.sum().sum()
                    phi2 = chi2 / n
                    r, k = table.shape
                    cramers_v = np.sqrt(phi2 / min(k - 1, r - 1))
                    severity = (
                        "critical" if cramers_v > _LEAK.categorical_critical else "warning" if cramers_v > _LEAK.categorical_warning else None
                    )
                    if severity:
                        impact = "high" if severity == "critical" else "medium"
                        quick_fix = (
                            "Options: \n- Drop column: Prevents target leakage (Pros: Ensures model integrity; Cons: Loses feature info).\n- Verify feature: Check if correlation is valid or data-derived (Pros: Validates data; Cons: Time-consuming)."
                            if severity == "critical"
                            else "Options: \n- Drop column: Reduces leakage risk (Pros: Safer model; Cons: May lose predictive info).\n- Retain and test: Use robust models (e.g., trees) and evaluate (Pros: Keeps potential signal; Cons: Risk of overfitting).\n- Engineer feature: Transform to reduce correlation (Pros: Retains info; Cons: Adds complexity)."
                        )
                        issues.append(
                            Issue(
                                category="target_leakage",
                                severity=severity,
                                column=col,
                                description=f"Column '{col}' highly associated with target (Cramer's V: {float(cramers_v):.2f})",
                                impact_score=impact,
                                quick_fix=quick_fix,
                            )
                        )
                except Exception:
                    continue
            numeric_cols = analyzer.df.select_dtypes(include="number").drop(
                columns=[analyzer.target_col], errors="ignore"
            )
            for col in numeric_cols.columns:
                groups = [
                    analyzer.df.loc[target == level, col].dropna().to_numpy()
                    for level in target.dropna().unique()
                    if len(analyzer.df.loc[target == level, col].dropna()) > 1
                ]
                if len(groups) < 2 or all(np.var(g, ddof=1) == 0 for g in groups):
                    continue
                try:
                    f_stat, p_val = f_oneway(*groups)
                    severity = (
                        "critical" if f_stat > _LEAK.f_stat_critical and p_val < _LEAK.f_stat_p_value
                        else "warning" if f_stat > _LEAK.f_stat_warning and p_val < _LEAK.f_stat_p_value else None
                    )
                    if severity:
                        impact = "high" if severity == "critical" else "medium"
                        quick_fix = (
                            "Options: \n- Drop column: Prevents target leakage (Pros: Ensures model integrity; Cons: Loses feature info).\n- Verify feature: Check if correlation is valid or data-derived (Pros: Validates data; Cons: Time-consuming)."
                            if severity == "critical"
                            else "Options: \n- Drop column: Reduces leakage risk (Pros: Safer model; Cons: May lose predictive info).\n- Retain and test: Use robust models (e.g., trees) and evaluate (Pros: Keeps potential signal; Cons: Risk of overfitting).\n- Engineer feature: Transform to reduce correlation (Pros: Retains info; Cons: Adds complexity)."
                        )
                        issues.append(
                            Issue(
                                category="target_leakage",
                                severity=severity,
                                column=col,
                                description=f"Column '{col}' strongly associated with target (F: {float(f_stat):.2f}, p: {float(p_val):.4f})",
                                impact_score=impact,
                                quick_fix=quick_fix,
                            )
                        )
                except Exception:
                    continue
    return issues