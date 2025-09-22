from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import hashlib
from scipy.stats import chi2_contingency, f_oneway
import numpy as np


@dataclass
class Issues:
    category: str
    severity: str  # critical or warning
    column: str
    description: str
    impact_score: str  # high, medium, low
    quick_fix: str


class DatasetAnalyzer:
    """
    Improved HashPrep Dataset Analyzer with Scenario-Based Quick Fixes
    Detects critical issues and warnings with dynamic severity and impact, provides multiple resolution options
    """

    def __init__(self, df: pd.DataFrame, target_col: Optional[str] = None, selected_checks: Optional[List[str]] = None):
        self.df = df
        self.target_col = target_col
        self.selected_checks = selected_checks
        self.issues: List[Issues] = []
        self.summaries: Dict = {}
        self.all_checks = [
            "data_leakage", "high_missing_values", "empty_columns", "single_value_columns",
            "target_leakage_patterns", "class_imbalance", "high_cardinality", "duplicates",
            "mixed_data_types", "outliers", "feature_correlation", "categorical_correlation",
            "mixed_correlation", "dataset_missingness", "high_zero_counts",
            "extreme_text_lengths", "datetime_skew", "missing_patterns"
        ]

    def analyze(self) -> Dict:
        """ Run all checks and return summary """
        self._get_dataset_preview()
        self._summarize_dataset_info()
        self._summarize_variable_types()
        self._add_reproduction_info()
        self._summarize_variables()
        self._summarize_interactions()
        self._summarize_missing_values()

        checks_to_run = self.all_checks if self.selected_checks is None else [
            check for check in self.selected_checks if check in self.all_checks
        ]

        for check in checks_to_run:
            getattr(self, f"_check_{check}")()

        return self._generate_summary()

    # =========================================================================
    # Sample Section
    # =========================================================================
    def _get_dataset_preview(self):
        head = self.df.head()
        tail = self.df.tail()
        sample = self.df.sample(min(10, len(self.df)))
        dataset_preview = {
            "head": head.to_dict(orient="records"),
            "tail": tail.to_dict(orient="records"),
            "sample": sample.to_dict(orient="records"),
        }
        self.summaries.update(dataset_preview)

    # =========================================================================
    # Overview Section
    # =========================================================================
    def _summarize_dataset_info(self):
        self.summaries["dataset_info"] = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "memory_mb": round(float(self.df.memory_usage(deep=True).sum() / 1024**2), 1),
            "missing_cells": int(self.df.isnull().sum().sum()),
            "total_cells": int(len(self.df) * len(self.df.columns)),
            "missing_percentage": round(
                int(self.df.isnull().sum().sum()) / (len(self.df) * len(self.df.columns)) * 100, 2
            ),
        }

    def _summarize_variable_types(self):
        variable_types = {column: str(self.df[column].dtype) for column in self.df.columns}
        self.summaries["variable_types"] = variable_types

    def _add_reproduction_info(self):
        dataset_hash = hashlib.md5(pd.util.hash_pandas_object(self.df, index=True).values).hexdigest()
        timestamp = pd.Timestamp.now().isoformat()
        self.summaries["reproduction_info"] = {"dataset_hash": dataset_hash, "analysis_timestamp": timestamp}

    # =========================================================================
    # Variables Section
    # =========================================================================
    def _summarize_variables(self):
        for column in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[column]):
                self._summarize_numeric_column(column)
            elif pd.api.types.is_datetime64_any_dtype(self.df[column]):
                self._summarize_datetime_column(column)
            elif pd.api.types.is_string_dtype(self.df[column]):
                self._summarize_text_column(column)
            else:
                self._summarize_categorical_column(column)

    def _summarize_numeric_column(self, col: str):
        series = self.df[col].dropna()
        stats = {
            "count": int(series.count()),
            "mean": float(series.mean()) if not series.empty else None,
            "std": float(series.std()) if not series.empty else None,
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "quantiles": (
                {
                    "25%": float(series.quantile(0.25)),
                    "50%": float(series.quantile(0.50)),
                    "75%": float(series.quantile(0.75)),
                } if not series.empty else None
            ),
            "missing": int(self.df[col].isna().sum()),
            "zeros": int((series == 0).sum()),
        }
        if not series.empty:
            hist, bin_edges = pd.cut(series, bins=10, retbins=True, include_lowest=True, duplicates="drop")
            hist = hist.value_counts().sort_index().to_dict()
            bin_edges = bin_edges.tolist()
            stats["histogram"] = {"bin_edges": bin_edges, "counts": hist}
        else:
            stats["histogram"] = {"bin_edges": None, "counts": None}
        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    def _summarize_categorical_column(self, col: str):
        series = self.df[col].dropna().astype(str)
        stats = {
            "count": int(series.count()),
            "unique": int(series.nunique()),
            "top_values": series.value_counts().head(10).to_dict(),
            "most_frequent": series.mode().iloc[0] if not series.empty else None,
            "missing": int(self.df[col].isna().sum()),
        }
        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    def _summarize_text_column(self, col: str):
        series = self.df[col].dropna().astype(str)
        lengths = series.str.len()
        stats = {
            "count": int(series.count()),
            "missing": int(self.df[col].isna().sum()),
            "avg_length": float(lengths.mean()) if not lengths.empty else None,
            "min_length": float(lengths.min()) if not lengths.empty else None,
            "max_length": float(lengths.max()) if not lengths.empty else None,
            "common_lengths": lengths.value_counts().head(5).to_dict(),
            "char_freq": (
                pd.Series(list("".join(series))).value_counts().head(10).to_dict()
                if not series.empty else None
            ),
        }
        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    def _summarize_datetime_column(self, col: str):
        series = pd.to_datetime(self.df[col], errors="coerce").dropna()
        stats = {
            "count": int(series.count()),
            "missing": int(self.df[col].isna().sum()),
            "min": str(series.min()) if not series.empty else None,
            "max": str(series.max()) if not series.empty else None,
            "year_counts": series.dt.year.value_counts().to_dict() if not series.empty else None,
            "month_counts": series.dt.month.value_counts().to_dict() if not series.empty else None,
            "day_counts": series.dt.day.value_counts().to_dict() if not series.empty else None,
        }
        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    # =========================================================================
    # Interactions and Correlations Section
    # =========================================================================
    def _summarize_interactions(self):
        self._scatter_plots_numeric()
        self._compute_correlation_matrices()
        self._compute_categorical_correlations()
        self._compute_mixed_correlations()

    def _scatter_plots_numeric(self):
        numeric_columns = self.df.select_dtypes(include="number").columns
        pairs = [(c1, c2) for i, c1 in enumerate(numeric_columns) for c2 in numeric_columns[i + 1 :]]
        self.summaries["scatter_pairs"] = pairs

    def _compute_correlation_matrices(self):
        numeric_df = self.df.select_dtypes(include="number")
        corrs = {}
        if not numeric_df.empty:
            corrs["pearson"] = numeric_df.corr(method="pearson").to_dict()
            corrs["spearman"] = numeric_df.corr(method="spearman").to_dict()
            corrs["kendall"] = numeric_df.corr(method="kendall").to_dict()
        self.summaries["numeric_correlations"] = corrs

    def _compute_categorical_correlations(self):
        categorical = self.df.select_dtypes(include="object").columns
        results = {}
        for i, c1 in enumerate(categorical):
            for c2 in categorical[i + 1 :]:
                try:
                    table = pd.crosstab(self.df[c1], self.df[c2])
                    chi2, _, _, _ = chi2_contingency(table)
                    n = table.sum().sum()
                    phi2 = chi2 / n
                    r, k = table.shape
                    cramers_v = (phi2 / min(k - 1, r - 1)) ** 0.5
                    results[f"{c1}__{c2}"] = cramers_v
                except Exception:
                    continue
        self.summaries["categorical_correlations"] = results

    def _compute_mixed_correlations(self):
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns
        num_cols = self.df.select_dtypes(include=["int64", "float64"]).columns
        mixed_corr = {}
        for cat in cat_cols:
            for num in num_cols:
                groups = [self.df.loc[self.df[cat] == level, num].dropna().to_numpy()
                          for level in self.df[cat].dropna().unique() if len(self.df.loc[self.df[cat] == level, num].dropna()) > 1]
                if len(groups) < 2 or all(np.var(g, ddof=1) == 0 for g in groups):
                    continue
                try:
                    f_stat, p_val = f_oneway(*groups)
                    mixed_corr[f"{cat}__{num}"] = {"f_stat": f_stat, "p_value": p_val}
                except Exception as e:
                    mixed_corr[f"{cat}__{num}"] = {"error": str(e)}
        self.summaries["mixed_correlations"] = mixed_corr

    # =========================================================================
    # Missing Value Section
    # =========================================================================
    def _summarize_missing_values(self):
        missing_count = self.df.isnull().sum().to_dict()
        missing_percentage = (self.df.isnull().mean() * 100).round(2).to_dict()
        self.summaries["missing_values"] = {"count": missing_count, "percentage": missing_percentage}
        self.summaries["missing_patterns"] = {
            col: self.df[self.df[col].isna()].index.tolist() for col in self.df.columns if self.df[col].isna().any()
        }

    # =========================================================================
    # Critical Issues & Warning Checks
    # =========================================================================
    def _check_data_leakage(self, target_col: str = None):
        if target_col and target_col in self.df.columns:
            target = self.df[target_col]
            for col in self.df.columns:
                if col == target_col:
                    continue
                if self.df[col].equals(target):
                    self.issues.append(
                        Issues(
                            category="data_leakage",
                            severity="critical",
                            column=col,
                            description=f"Column '{col}' is identical to target '{target_col}'",
                            impact_score="high",
                            quick_fix="Options: \n- Drop column: Prevents data leakage (Pros: Ensures model integrity; Cons: Loses potential feature info).\n- Verify data collection: Ensure column isn't target-derived (Pros: Validates data; Cons: Time-consuming).",
                        )
                    )

    def _check_high_missing_values(self, threshold: float = 0.4, critical_threshold: float = 0.7):
        for col in self.df.columns:
            missing_pct = self.df[col].isna().mean()
            if missing_pct > threshold:
                severity = "critical" if missing_pct > critical_threshold else "warning"
                impact = "high" if severity == "critical" else "medium"
                quick_fix = (
                    "Options: \n- Drop column: Reduces bias from missing data (Pros: Simplifies model; Cons: Loses potential info).\n- Impute values: Use domain-informed methods (e.g., median, mode, or predictive model) (Pros: Retains feature; Cons: May introduce bias).\n- Create missingness indicator: Flag missing values as a new feature (Pros: Captures missingness pattern; Cons: Adds complexity)."
                    if severity == "critical"
                    else "Options: \n- Impute values: Use simple methods (e.g., mean, mode) or domain knowledge (Pros: Retains feature; Cons: Risk of bias if not careful).\n- Drop column: If feature is less critical (Pros: Simplifies model; Cons: Loses info).\n- Test model impact: Evaluate feature importance (Pros: Data-driven decision; Cons: Requires computation)."
                )
                self.issues.append(
                    Issues(
                        category="missing_values",
                        severity=severity,
                        column=col,
                        description=f"{missing_pct:.1%} missing values in '{col}'",
                        impact_score=impact,
                        quick_fix=quick_fix,
                    )
                )

    def _check_empty_columns(self):
        for col in self.df.columns:
            if self.df[col].notna().sum() == 0:
                self.issues.append(
                    Issues(
                        category="empty_column",
                        severity="critical",
                        column=col,
                        description=f"Column '{col}' has no non-missing values",
                        impact_score="high",
                        quick_fix="Options: \n- Drop column: No useful data present (Pros: Simplifies model; Cons: None).\n- Verify data collection: Check for errors in data (Pros: Ensures data quality; Cons: Time-consuming).",
                    )
                )

    def _check_single_value_columns(self):
        for col in self.df.columns:
            if self.df[col].nunique(dropna=True) == 1:
                impact = "low" if col != self.target_col else "high"
                severity = "warning" if col != self.target_col else "critical"
                quick_fix = (
                    "Options: \n- Drop column: Not informative for modeling (Pros: Simplifies model; Cons: None).\n- Verify data: Ensure single value isn't an error (Pros: Validates data; Cons: Time-consuming)."
                    if col != self.target_col
                    else "Options: \n- Redefine target: Replace with a more variable target (Pros: Enables modeling; Cons: Requires new data).\n- Stop analysis: Constant target prevents meaningful prediction (Pros: Avoids invalid model; Cons: Halts analysis)."
                )
                self.issues.append(
                    Issues(
                        category="single_value",
                        severity=severity,
                        column=col,
                        description=f"Column '{col}' contains only one unique value",
                        impact_score=impact,
                        quick_fix=quick_fix,
                    )
                )

    def _check_target_leakage_patterns(self, target_col: str = None):
        if target_col and target_col in self.df.columns:
            target = self.df[target_col]
            # Numeric target
            if pd.api.types.is_numeric_dtype(target):
                numeric_cols = self.df.select_dtypes(include="number").drop(columns=[target_col], errors="ignore")
                if not numeric_cols.empty:
                    corrs = numeric_cols.corrwith(target).abs()
                    for col, corr in corrs.items():
                        severity = "critical" if corr > 0.98 else "warning" if corr > 0.95 else None
                        if severity:
                            impact = "high" if severity == "critical" else "medium"
                            quick_fix = (
                                "Options: \n- Drop column: Prevents target leakage (Pros: Ensures model integrity; Cons: Loses feature info).\n- Verify feature: Check if correlation is valid or data-derived (Pros: Validates data; Cons: Time-consuming)."
                                if severity == "critical"
                                else "Options: \n- Drop column: Reduces leakage risk (Pros: Safer model; Cons: May lose predictive info).\n- Retain and test: Use robust models (e.g., trees) and evaluate (Pros: Keeps potential signal; Cons: Risk of overfitting).\n- Engineer feature: Transform to reduce correlation (Pros: Retains info; Cons: Adds complexity)."
                            )
                            self.issues.append(
                                Issues(
                                    category="target_leakage",
                                    severity=severity,
                                    column=col,
                                    description=f"Column '{col}' highly correlated with target ({corr:.2f})",
                                    impact_score=impact,
                                    quick_fix=quick_fix,
                                )
                            )
            # Categorical target
            else:
                cat_cols = self.df.select_dtypes(include="object").drop(columns=[target_col], errors="ignore")
                for col in cat_cols.columns:
                    try:
                        table = pd.crosstab(target, self.df[col])
                        chi2, _, _, _ = chi2_contingency(table)
                        n = table.sum().sum()
                        phi2 = chi2 / n
                        r, k = table.shape
                        cramers_v = np.sqrt(phi2 / min(k - 1, r - 1))
                        severity = "critical" if cramers_v > 0.95 else "warning" if cramers_v > 0.8 else None
                        if severity:
                            impact = "high" if severity == "critical" else "medium"
                            quick_fix = (
                                "Options: \n- Drop column: Prevents target leakage (Pros: Ensures model integrity; Cons: Loses feature info).\n- Verify feature: Check if correlation is valid or data-derived (Pros: Validates data; Cons: Time-consuming)."
                                if severity == "critical"
                                else "Options: \n- Drop column: Reduces leakage risk (Pros: Safer model; Cons: May lose predictive info).\n- Retain and test: Use robust models (e.g., trees) and evaluate (Pros: Keeps potential signal; Cons: Risk of overfitting).\n- Engineer feature: Transform to reduce correlation (Pros: Retains info; Cons: Adds complexity)."
                            )
                            self.issues.append(
                                Issues(
                                    category="target_leakage",
                                    severity=severity,
                                    column=col,
                                    description=f"Column '{col}' highly associated with target (Cramer's V: {cramers_v:.2f})",
                                    impact_score=impact,
                                    quick_fix=quick_fix,
                                )
                            )
                    except Exception:
                        continue
                numeric_cols = self.df.select_dtypes(include="number").drop(columns=[target_col], errors="ignore")
                for col in numeric_cols.columns:
                    groups = [self.df.loc[target == level, col].dropna().to_numpy()
                              for level in target.dropna().unique() if len(self.df.loc[target == level, col].dropna()) > 1]
                    if len(groups) < 2 or all(np.var(g, ddof=1) == 0 for g in groups):
                        continue
                    try:
                        f_stat, p_val = f_oneway(*groups)
                        severity = "critical" if f_stat > 20.0 and p_val < 0.001 else "warning" if f_stat > 10.0 and p_val < 0.001 else None
                        if severity:
                            impact = "high" if severity == "critical" else "medium"
                            quick_fix = (
                                "Options: \n- Drop column: Prevents target leakage (Pros: Ensures model integrity; Cons: Loses feature info).\n- Verify feature: Check if correlation is valid or data-derived (Pros: Validates data; Cons: Time-consuming)."
                                if severity == "critical"
                                else "Options: \n- Drop column: Reduces leakage risk (Pros: Safer model; Cons: May lose predictive info).\n- Retain and test: Use robust models (e.g., trees) and evaluate (Pros: Keeps potential signal; Cons: Risk of overfitting).\n- Engineer feature: Transform to reduce correlation (Pros: Retains info; Cons: Adds complexity)."
                            )
                            self.issues.append(
                                Issues(
                                    category="target_leakage",
                                    severity=severity,
                                    column=col,
                                    description=f"Column '{col}' strongly associated with target (F: {f_stat:.2f}, p: {p_val:.4f})",
                                    impact_score=impact,
                                    quick_fix=quick_fix,
                                )
                            )
                    except Exception:
                        continue

    def _check_class_imbalance(self, target_col: str = None, threshold: float = 0.9):
        if target_col and target_col in self.df.columns:
            counts = self.df[target_col].value_counts(normalize=True)
            if counts.max() > threshold:
                self.issues.append(
                    Issues(
                        category="class_imbalance",
                        severity="warning",
                        column=target_col,
                        description=f"Target '{target_col}' is imbalanced ({counts.max():.1%} in one class)",
                        impact_score="medium",
                        quick_fix="Options: \n- Resample data: Use oversampling (e.g., SMOTE) or undersampling (Pros: Balances classes; Cons: May introduce bias or lose data).\n- Use class weights: Adjust model weights for imbalance (Pros: Simple; Cons: Model-dependent).\n- Stratified sampling: Ensure balanced splits in training (Pros: Improves evaluation; Cons: Requires careful implementation).",
                    )
                )

    def _check_high_cardinality(self, threshold: int = 100, critical_threshold: float = 0.9):
        categorical_cols = self.df.select_dtypes(include="object").columns
        for col in categorical_cols:
            unique_count = self.df[col].nunique()
            unique_ratio = unique_count / len(self.df)
            if unique_count > threshold:
                severity = "critical" if unique_ratio > critical_threshold else "warning"
                impact = "high" if severity == "critical" else "medium"
                quick_fix = (
                    "Options: \n- Drop column: Avoids overfitting from unique identifiers (Pros: Simplifies model; Cons: Loses potential info).\n- Engineer feature: Extract patterns (e.g., titles from names) (Pros: Retains useful info; Cons: Requires domain knowledge).\n- Use hashing: Reduce dimensionality (Pros: Scalable; Cons: May lose interpretability)."
                    if severity == "critical"
                    else "Options: \n- Group rare categories: Reduce cardinality (Pros: Simplifies feature; Cons: May lose nuance).\n- Use feature hashing: Map to lower dimensions (Pros: Scalable; Cons: Less interpretable).\n- Retain and test: Evaluate feature importance (Pros: Data-driven; Cons: Risk of overfitting)."
                )
                self.issues.append(
                    Issues(
                        category="high_cardinality",
                        severity=severity,
                        column=col,
                        description=f"Column '{col}' has {unique_count} unique values ({unique_ratio:.1%} of rows)",
                        impact_score=impact,
                        quick_fix=quick_fix,
                    )
                )

    def _check_duplicates(self):
        duplicate_rows = self.df.duplicated().sum()
        if duplicate_rows > 0:
            duplicate_ratio = duplicate_rows / len(self.df)
            severity = "critical" if duplicate_ratio > 0.1 else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Drop duplicates: Ensures data integrity (Pros: Cleaner data; Cons: May lose valid repeats).\n- Verify duplicates: Check if intentional (e.g., time-series) (Pros: Validates data; Cons: Time-consuming)."
                if severity == "critical"
                else "Options: \n- Drop duplicates: Simplifies dataset (Pros: Cleaner data; Cons: May lose valid repeats).\n- Keep duplicates: If meaningful (e.g., repeated events) (Pros: Retains info; Cons: May bias model).\n- Test impact: Evaluate model performance with/without duplicates (Pros: Data-driven; Cons: Requires computation)."
            )
            self.issues.append(
                Issues(
                    category="duplicates",
                    severity=severity,
                    column="__all__",
                    description=f"Dataset contains {duplicate_rows} duplicate rows ({duplicate_ratio:.1%} of rows)",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )

    def _check_mixed_data_types(self):
        for col in self.df.columns:
            types = self.df[col].dropna().map(type).nunique()
            if types > 1:
                self.issues.append(
                    Issues(
                        category="mixed_types",
                        severity="warning",
                        column=col,
                        description=f"Column '{col}' contains mixed data types",
                        impact_score="low",
                        quick_fix="Options: \n- Cast to single type: Ensure consistency (Pros: Simplifies processing; Cons: May lose nuance).\n- Split column: Separate types into new features (Pros: Preserves info; Cons: Adds complexity).\n- Investigate source: Check data collection errors (Pros: Improves quality; Cons: Time-consuming).",
                    )
                )

    def _check_outliers(self, z_threshold: float = 4.0):
        for col in self.df.select_dtypes(include="number").columns:
            series = self.df[col].dropna()
            if len(series) == 0:
                continue
            z_scores = (series - series.mean()) / series.std(ddof=0)
            outlier_count = (abs(z_scores) > z_threshold).sum()
            if outlier_count > 0:
                outlier_ratio = outlier_count / len(series)
                severity = "critical" if outlier_ratio > 0.1 else "warning"
                impact = "high" if severity == "critical" else "medium"
                quick_fix = (
                    "Options: \n- Remove outliers: Improves model stability (Pros: Reduces noise; Cons: Loses data).\n- Winsorize: Cap extreme values (Pros: Retains data; Cons: Alters distribution).\n- Transform: Apply log/sqrt to reduce impact (Pros: Preserves info; Cons: Changes interpretation)."
                    if severity == "critical"
                    else "Options: \n- Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming).\n- Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation).\n- Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models)."
                )
                self.issues.append(
                    Issues(
                        category="outliers",
                        severity=severity,
                        column=col,
                        description=f"Column '{col}' has {outlier_count} potential outliers ({outlier_ratio:.1%} of non-missing values)",
                        impact_score=impact,
                        quick_fix=quick_fix,
                    )
                )

    def _check_feature_correlation(self, threshold: float = 0.95, critical_threshold: float = 0.98):
        numeric_df = self.df.select_dtypes(include="number")
        if numeric_df.empty:
            return
        corr_matrix = numeric_df.corr().abs()
        upper = corr_matrix.where(np.tril(np.ones(corr_matrix.shape)).astype(bool))
        correlated_pairs = [
            (col, row, val) for row in upper.index for col, val in upper[row].dropna().items()
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
            self.issues.append(
                Issues(
                    category="feature_correlation",
                    severity=severity,
                    column=f"{col1},{col2}",
                    description=f"Columns '{col1}' and '{col2}' are highly correlated ({corr:.2f})",
                    impact_score=impact,
                    quick_fix=quick_fix,
                    )
                )

    def _check_categorical_correlation(self, threshold: float = 0.8, critical_threshold: float = 0.95):
        categorical = self.df.select_dtypes(include="object").columns
        for i, c1 in enumerate(categorical):
            for c2 in categorical[i + 1 :]:
                try:
                    table = pd.crosstab(self.df[c1], self.df[c2])
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
                        self.issues.append(
                            Issues(
                                category="feature_correlation",
                                severity=severity,
                                column=f"{c1},{c2}",
                                description=f"Columns '{c1}' and '{c2}' are highly associated (Cramer's V: {cramers_v:.2f})",
                                impact_score=impact,
                                quick_fix=quick_fix,
                            )
                        )
                except Exception:
                    continue

    def _check_mixed_correlation(self, p_threshold: float = 0.05, critical_p_threshold: float = 0.001):
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns
        num_cols = self.df.select_dtypes(include=["int64", "float64"]).columns
        for cat in cat_cols:
            for num in num_cols:
                groups = [self.df.loc[self.df[cat] == level, num].dropna().to_numpy()
                          for level in self.df[cat].dropna().unique() if len(self.df.loc[self.df[cat] == level, num].dropna()) > 1]
                if len(groups) < 2 or all(np.var(g, ddof=1) == 0 for g in groups):
                    continue
                try:
                    f_stat, p_val = f_oneway(*groups)
                    if p_val < p_threshold:
                        severity = "critical" if p_val < critical_p_threshold and f_stat > 20.0 else "warning"
                        impact = "high" if severity == "critical" else "medium"
                        quick_fix = (
                            "Options: \n- Drop one feature: Avoids redundancy (Pros: Simplifies model; Cons: Loses info).\n- Engineer feature: Transform categorical or numeric feature (Pros: Retains info; Cons: Adds complexity).\n- Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models)."
                            if severity == "critical"
                            else "Options: \n- Drop one feature: If less predictive (Pros: Simplifies model; Cons: Loses info).\n- Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: Risk of redundancy).\n- Engineer feature: Transform or encode differently (Pros: Reduces redundancy; Cons: Adds complexity)."
                        )
                        self.issues.append(
                            Issues(
                                category="feature_correlation",
                                severity=severity,
                                column=f"{cat},{num}",
                                description=f"Columns '{cat}' and '{num}' show strong association (F: {f_stat:.2f}, p: {p_val:.4f})",
                                impact_score=impact,
                                quick_fix=quick_fix,
                            )
                        )
                except Exception:
                    continue

    def _check_dataset_missingness(self, threshold: float = 20.0, critical_threshold: float = 50.0):
        missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        if missing_pct > threshold:
            severity = "critical" if missing_pct > critical_threshold else "warning"
            impact = "high" if severity == "critical" else "medium"
            quick_fix = (
                "Options: \n- Drop sparse columns: Reduces bias from missingness (Pros: Simplifies model; Cons: Loses info).\n- Impute globally: Use advanced methods (e.g., predictive models) (Pros: Retains features; Cons: Risk of bias).\n- Investigate source: Check data collection issues (Pros: Improves quality; Cons: Time-consuming)."
                if severity == "critical"
                else "Options: \n- Impute missing values: Use simple or domain-informed methods (Pros: Retains features; Cons: Risk of bias).\n- Drop sparse columns: If less critical (Pros: Simplifies model; Cons: Loses info).\n- Test impact: Evaluate model with/without missing data (Pros: Data-driven; Cons: Requires computation)."
            )
            self.issues.append(
                Issues(
                    category="dataset_missingness",
                    severity=severity,
                    column="__all__",
                    description=f"Dataset has {missing_pct:.1f}% missing values",
                    impact_score=impact,
                    quick_fix=quick_fix,
                )
            )

    def _check_high_zero_counts(self, threshold: float = 0.5, critical_threshold: float = 0.8):
        for col in self.df.select_dtypes(include="number").columns:
            series = self.df[col].dropna()
            if len(series) == 0:
                continue
            zero_pct = (series == 0).mean()
            if zero_pct > threshold:
                severity = "critical" if zero_pct > critical_threshold else "warning"
                impact = "high" if severity == "critical" else "medium"
                quick_fix = (
                    "Options: \n- Drop column: If zeros are not meaningful (Pros: Simplifies model; Cons: Loses info).\n- Transform: Use binary indicator or log transform (Pros: Retains info; Cons: Changes interpretation).\n- Verify zeros: Check if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming)."
                    if severity == "critical"
                    else "Options: \n- Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity).\n- Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results).\n- Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming)."
                )
                self.issues.append(
                    Issues(
                        category="high_zero_counts",
                        severity=severity,
                        column=col,
                        description=f"Column '{col}' has {zero_pct:.1%} zero values",
                        impact_score=impact,
                        quick_fix=quick_fix,
                    )
                )

    def _check_extreme_text_lengths(self, max_threshold: int = 1000, min_threshold: int = 1):
        for col in self.df.select_dtypes(include="object").columns:
            series = self.df[col].dropna().astype(str)
            if series.empty:
                continue
            lengths = series.str.len()
            if lengths.max() > max_threshold or lengths.min() < min_threshold:
                extreme_ratio = ((lengths > max_threshold) | (lengths < min_threshold)).mean()
                severity = "critical" if extreme_ratio > 0.1 else "warning"
                impact = "high" if severity == "critical" else "medium"
                quick_fix = (
                    "Options: \n- Truncate values: Cap extreme lengths (Pros: Stabilizes model; Cons: Loses info).\n- Filter outliers: Remove extreme entries (Pros: Reduces noise; Cons: Loses data).\n- Transform: Normalize lengths (e.g., log) (Pros: Retains info; Cons: Changes interpretation)."
                    if severity == "critical"
                    else "Options: \n- Investigate extremes: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming).\n- Transform: Truncate or normalize lengths (Pros: Retains info; Cons: Changes interpretation).\n- Retain and test: Use robust models (Pros: Keeps info; Cons: May affect sensitive models)."
                )
                self.issues.append(
                    Issues(
                        category="extreme_text_lengths",
                        severity=severity,
                        column=col,
                        description=f"Column '{col}' has extreme lengths (min: {lengths.min()}, max: {lengths.max()}; {extreme_ratio:.1%} extreme)",
                        impact_score=impact,
                        quick_fix=quick_fix,
                    )
                )

    def _check_datetime_skew(self, threshold: float = 0.8):
        for col in self.df.select_dtypes(include="datetime64").columns:
            series = pd.to_datetime(self.df[col], errors="coerce").dropna()
            if series.empty:
                continue
            year_counts = series.dt.year.value_counts(normalize=True)
            if year_counts.max() > threshold:
                self.issues.append(
                    Issues(
                        category="datetime_skew",
                        severity="warning",
                        column=col,
                        description=f"Column '{col}' has {year_counts.max():.1%} in one year",
                        impact_score="medium",
                        quick_fix="Options: \n- Subsample data: Balance temporal distribution (Pros: Reduces bias; Cons: Loses data).\n- Engineer features: Extract year/month (Pros: Retains info; Cons: Adds complexity).\n- Retain and test: Use robust models (Pros: Keeps info; Cons: May skew results).",
                    )
                )

    def _check_missing_patterns(self, threshold: float = 0.05, critical_p_threshold: float = 0.001):
        missing_cols = [col for col in self.df.columns if self.df[col].isna().sum() >= 5]
        for col in missing_cols:
            for other_col in self.df.select_dtypes(include=["object", "category"]).columns:
                if col == other_col:
                    continue
                try:
                    value_counts = self.df[other_col].value_counts()
                    rare_cats = value_counts[value_counts < 5].index
                    temp_col = self.df[other_col].copy()
                    if not rare_cats.empty:
                        temp_col = temp_col.where(~temp_col.isin(rare_cats), "Other")
                    is_missing = self.df[col].isna().astype(int)
                    table = pd.crosstab(is_missing, temp_col)
                    if table.shape[0] < 2 or table.shape[1] < 2:
                        continue
                    chi2, p_val, _, _ = chi2_contingency(table)
                    severity = "critical" if p_val < critical_p_threshold and other_col == self.target_col else "warning"
                    impact = "high" if severity == "critical" else "medium"
                    quick_fix = (
                        "Options: \n- Drop column: Avoids bias from non-random missingness (Pros: Simplifies model; Cons: Loses info).\n- Impute with target-aware method: Use predictive models or domain knowledge (Pros: Retains feature; Cons: Complex).\n- Create missingness indicator: Flag missing values (Pros: Captures pattern; Cons: Adds complexity)."
                        if severity == "critical"
                        else "Options: \n- Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias).\n- Drop column: If less critical (Pros: Simplifies model; Cons: Loses info).\n- Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation)."
                    )
                    if p_val < threshold:
                        self.issues.append(
                            Issues(
                                category="missing_patterns",
                                severity=severity,
                                column=col,
                                description=f"Missingness in '{col}' correlates with '{other_col}' (p: {p_val:.4f})",
                                impact_score=impact,
                                quick_fix=quick_fix,
                            )
                        )
                except Exception:
                    continue
            for other_col in self.df.select_dtypes(include=["int64", "float64"]).columns:
                if col == other_col:
                    continue
                try:
                    missing = self.df[self.df[col].isna()][other_col].dropna()
                    non_missing = self.df[self.df[col].notna()][other_col].dropna()
                    if len(missing) < 5 or len(non_missing) < 5:
                        continue
                    f_stat, p_val = f_oneway(missing, non_missing)
                    severity = "critical" if p_val < critical_p_threshold and f_stat > 20.0 and other_col == self.target_col else "warning"
                    impact = "high" if severity == "critical" else "medium"
                    quick_fix = (
                        "Options: \n- Drop column: Avoids bias from non-random missingness (Pros: Simplifies model; Cons: Loses info).\n- Impute with target-aware method: Use predictive models or domain knowledge (Pros: Retains feature; Cons: Complex).\n- Create missingness indicator: Flag missing values (Pros: Captures pattern; Cons: Adds complexity)."
                        if severity == "critical"
                        else "Options: \n- Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias).\n- Drop column: If less critical (Pros: Simplifies model; Cons: Loses info).\n- Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation)."
                    )
                    if p_val < threshold:
                        self.issues.append(
                            Issues(
                                category="missing_patterns",
                                severity=severity,
                                column=col,
                                description=f"Missingness in '{col}' correlates with numeric '{other_col}' (F: {f_stat:.2f}, p: {p_val:.4f})",
                                impact_score=impact,
                                quick_fix=quick_fix,
                            )
                        )
                except Exception:
                    continue

    # =========================================================================
    # Generate Summary
    # =========================================================================
    def _generate_summary(self):
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        warning_issues = [i for i in self.issues if i.severity == "warning"]
        return {
            "critical_count": len(critical_issues),
            "warning_count": len(warning_issues),
            "total_issues": len(self.issues),
            "issues": [
                {
                    "category": issue.category,
                    "severity": issue.severity,
                    "column": issue.column,
                    "description": issue.description,
                    "impact_score": issue.impact_score,
                    "quick_fix": issue.quick_fix,
                } for issue in self.issues
            ],
            "summaries": self.summaries,
        }