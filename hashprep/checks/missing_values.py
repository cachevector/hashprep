from scipy.stats import chi2_contingency, mannwhitneyu
from .core import Issue
import pandas as pd
from collections import defaultdict
import numpy as np

def _check_high_missing_values(analyzer, threshold: float = 0.4, critical_threshold: float = 0.7):
    issues = []
    for col in analyzer.df.columns:
        missing_pct = float(analyzer.df[col].isna().mean())
        if missing_pct > threshold:
            severity = "critical" if missing_pct > critical_threshold else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Drop column: Reduces bias from missing data (Pros: Simplifies model; Cons: Loses potential info).\n- Impute values: Use domain-informed methods (e.g., median, mode, or predictive model) (Pros: Retains feature; Cons: May introduce bias).\n- Create missingness indicator: Flag missing values as a new feature (Pros: Captures missingness pattern; Cons: Adds complexity)."
                if severity == "critical"
                else "Options: \n- Impute values: Use simple methods (e.g., mean, mode) or domain knowledge (Pros: Retains feature; Cons: Risk of bias if not careful).\n- Drop column: If feature is less critical (Pros: Simplifies model; Cons: Loses info).\n- Test model impact: Evaluate feature importance (Pros: Data-driven decision; Cons: Requires computation)."
            )
            issues.append(
                Issue(
                    category="missing_values",
                    severity=severity,
                    column=col,
                    description=f"{missing_pct:.1%} missing values in '{col}'",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )
    return issues

def _check_empty_columns(analyzer):
    issues = []
    for col in analyzer.df.columns:
        if int(analyzer.df[col].notna().sum()) == 0:
            issues.append(
                Issue(
                    category="empty_column",
                    severity="critical",
                    column=col,
                    description=f"Column '{col}' has no non-missing values",
                    impact_score="high",
                    quick_fix="Options: \n- Drop column: No useful data present (Pros: Simplifies model; Cons: None).\n- Verify data collection: Check for errors in data (Pros: Ensures data quality; Cons: Time-consuming).",
                )
            )
    return issues

def _check_dataset_missingness(analyzer, threshold: float = 20.0, critical_threshold: float = 50.0):
    issues = []
    missing_pct = float(
        (analyzer.df.isnull().sum().sum() / (analyzer.df.shape[0] * analyzer.df.shape[1])) * 100
    )
    if missing_pct > threshold:
        severity = "critical" if missing_pct > critical_threshold else "warning"
        impact = "high" if severity == "critical" else "medium"
        quick_fix = (
            "Options: \n- Drop sparse columns: Reduces bias from missingness (Pros: Simplifies model; Cons: Loses info).\n- Impute globally: Use advanced methods (e.g., predictive models) (Pros: Retains features; Cons: Risk of bias).\n- Investigate source: Check data collection issues (Pros: Improves quality; Cons: Time-consuming)."
            if severity == "critical"
            else "Options: \n- Impute missing values: Use simple or domain-informed methods (Pros: Retains features; Cons: Risk of bias).\n- Drop sparse columns: If less critical (Pros: Simplifies model; Cons: Loses info).\n- Test impact: Evaluate model with/without missing data (Pros: Data-driven; Cons: Requires computation)."
        )
        issues.append(
            Issue(
                category="dataset_missingness",
                severity=severity,
                column="__all__",
                description=f"Dataset has {missing_pct:.1f}% missing values",
                impact_score=impact,
                quick_fix=quick_fix,
            )
        )
    return issues


def _check_missing_patterns(analyzer, threshold: float = 0.01,
                            critical_p_threshold: float = 0.001):
    issues = []
    missing_cols = [
        col for col in analyzer.df.columns if int(analyzer.df[col].isna().sum()) >= 10
    ]

    # grouping logic
    cat_patterns = defaultdict(list)  # (missing_col, correlated_col, p_val, cramers_v)
    num_patterns = defaultdict(list)  # (missing_col, correlated_col, p_val, cohens_d)

    for col in missing_cols:
        for other_col in analyzer.df.select_dtypes(
                include=["object", "category"]
        ).columns:
            if col == other_col:
                continue
            try:
                value_counts = analyzer.df[other_col].value_counts()
                rare_cats = value_counts[value_counts < 5].index
                temp_col = analyzer.df[other_col].copy()
                if not rare_cats.empty:
                    temp_col = temp_col.where(~temp_col.isin(rare_cats), "Other")
                is_missing = analyzer.df[col].isna().astype(int)
                table = pd.crosstab(is_missing, temp_col)
                if table.shape[0] < 2 or table.shape[1] < 2:
                    continue
                chi2, p_val, _, _ = chi2_contingency(table)

                # Cramér's V calculation and threshold
                def cramers_v(table):
                    chi2_val = chi2_contingency(table)[0]
                    n = table.sum().sum()
                    phi2 = chi2_val / n
                    r, k = table.shape
                    phi2corr = max(0, phi2 - (k - 1) * (r - 1) / (n - 1))
                    rkcorr = min((k - 1), (r - 1))
                    if rkcorr == 0:
                        return 0.0
                    return np.sqrt(phi2corr / rkcorr)

                cramers = cramers_v(table)
                if p_val < threshold and cramers > 0.1:
                    cat_patterns[col].append((other_col, p_val, cramers))
            except Exception:
                continue

        for other_col in analyzer.df.select_dtypes(
                include=["int64", "float64"]
        ).columns:
            if col == other_col:
                continue
            try:
                missing = analyzer.df[analyzer.df[col].isna()][other_col].dropna()
                non_missing = analyzer.df[analyzer.df[col].notna()][other_col].dropna()
                if len(missing) < 10 or len(non_missing) < 10:
                    continue

                # Replaced f_oneway with mannwhitneyu
                u_stat, p_val = mannwhitneyu(missing, non_missing, alternative='two-sided')

                # Cohen's d proxy as effect size
                pooled_std = np.sqrt((np.std(missing) ** 2 + np.std(non_missing) ** 2) / 2)
                cohens_d = abs(np.mean(missing) - np.mean(non_missing)) / pooled_std if pooled_std > 0 else 0

                if p_val < threshold and cohens_d > 0.2:
                    num_patterns[col].append((other_col, p_val, cohens_d))
            except Exception:
                continue

    # Generate grouped issues
    for col in missing_cols:
        all_patterns = []
        if col in cat_patterns:
            all_patterns.extend(cat_patterns[col])
        if col in num_patterns:
            all_patterns.extend(num_patterns[col])

        if all_patterns:
            # Sort by effect size (descending) and take top 3
            all_patterns.sort(key=lambda x: x[2], reverse=True)  # x[2] is effect size
            top_corrs = [pat[0] for pat in all_patterns[:3]]
            total_count = len(all_patterns)

            desc = f"Missingness in '{col}' correlates with {total_count} columns ({', '.join(top_corrs)})"

            # severity logic with effect size for critical
            max_effect = max([pat[2] for pat in all_patterns])
            is_target_correlated = any(pat[0] == analyzer.target_col for pat in all_patterns)
            severity = (
                "critical"
                if p_val < critical_p_threshold and is_target_correlated and max_effect > 0.3  # medium effect threshold
                else "warning"
            )
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Drop column: Avoids bias from non-random missingness (Pros: Simplifies model; Cons: Loses info).\n- Impute with target-aware method: Use predictive models or domain knowledge (Pros: Retains feature; Cons: Complex).\n- Create missingness indicator: Flag missing values (Pros: Captures pattern; Cons: Adds complexity)."
                if severity == "critical"
                else "Options: \n- Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias).\n- Drop column: If less critical (Pros: Simplifies model; Cons: Loses info).\n- Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation)."
            )

            issues.append(
                Issue(
                    category="missing_patterns",
                    severity=severity,
                    column=col,
                    description=desc,  # Use grouped description
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )

    return issues