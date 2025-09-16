from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd
import hashlib
from scipy.stats import chi2_contingency
import numpy as np


@dataclass
class Issues:
    category: str
    severity: str  # critical or warning
    column: str
    description: str
    impact_score: str  # TODO: check afterwards if it's needed
    quick_fix: str


class DatasetAnalyzer:
    """
    HashPrep Dataset Analyzer
    Detects critical issues and warnings, generates report
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.issues: Optional[str] = []
        self.summaries: Dict = {}

    def analyze(self) -> Dict:
        """Run all checks and return summary"""

        # ---- Dataset Preview ----
        self._get_dataset_preview()

        # ---- Summaries ----
        self._summarize_dataset_info()
        self._summarize_variable_types()
        self._add_reproduction_info()
        self._summarize_variables()
        self._summarize_interactions()
        self._summarize_missing_values()

        # ---- Warnings and Critical Issues ----
        self._check_data_leakage()
        self._check_high_missing_values()
        self._check_empty_columns()
        self._check_single_value_columns()
        self._check_target_leakage_patterns()
        self._check_class_imbalance()
        self._check_high_cardinality()
        self._check_duplicates()
        self._check_mixed_data_types()
        self._check_outliers()
        self._check_feature_correlation()

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
        """
        Total rows, columns, missing cells, memory usage
        """
        self.summaries["dataset_info"] = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "memory_mb": round(
                float(self.df.memory_usage(deep=True).sum() / 1024**2), 1
            ),
            "missing_cells": int(self.df.isnull().sum().sum()),
            "total_cells": int(len(self.df) * len(self.df.columns)),
            "missing_percentage": round(
                int(self.df.isnull().sum().sum())
                / (len(self.df) * len(self.df.columns))
                * 100,
                2,
            ),
        }

    def _summarize_variable_types(self):
        """
        Breakdown of variable types: numerical, categorical, boolean, datetime
        """
        variable_types = {}
        for column in self.df.columns:
            variable_types[column] = str(self.df[column].dtype)

        self.summaries["variable_types"] = variable_types

    def _add_reproduction_info(self):
        """Dataset hash + analysis timestamp for reproducibility"""
        dataset_hash = hashlib.md5(
            pd.util.hash_pandas_object(self.df, index=True).values
        ).hexdigest()
        timestamp = pd.Timestamp.now().isoformat()
        self.summaries["reproduction_info"] = {
            "dataset_hash": dataset_hash,
            "analysis_timestamp": timestamp,
        }

    # =========================================================================
    # Variables Section
    # =========================================================================
    def _summarize_variables(self):
        """Iterate over all columns and delegate to type-specific summarizers"""
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
        """Numeric stats: mean, std, min, max, quantiles, zeros, histogram"""
        series = self.df[col].dropna()  # we dont need NANs for stats

        stats = {
            "count": int(series.count()),
            "mean": float(series.mean()) if not series.empty else None,
            "std": float(series.std()) if not series.empty else None,
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "quantiles": (
                {
                    "25%": float(series.quantile(0.25)),
                    "50%": float(series.quantile(0.50)),  # median
                    "75%": float(series.quantile(0.75)),
                }
                if not series.empty
                else None
            ),
            "missing": int(self.df[col].isna().sum()),
            "zeros": int((series == 0).sum()),
        }

        # Histogram
        hist, bin_edges = None, None
        if not series.empty:
            hist, bin_edges = pd.cut(
                series, bins=10, retbins=True, include_lowest=True, duplicates="drop"
            )
            hist = hist.value_counts().sort_index().to_dict()
            bin_edges = bin_edges.tolist()

        stats["histogram"] = {"bin_edges": bin_edges, "counts": hist}

        # Add to summaries
        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    def _summarize_categorical_column(self, col: str):
        """Categorical stats: value counts, most frequent, length distribution"""
        series = self.df[col].dropna().astype(str)
        stats = {
            "count": int(series.count()),
            "unique": int(series.nunique()),
            "top_values": series.value_counts().head(10).to_dict(),  # top 10 only
            "most_frequent": series.mode().iloc[0] if not series.empty else None,
            "missing": int(self.df[col].isna().sum()),
        }

        # Add to summaries
        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    def _summarize_text_column(self, col: str):
        """Text stats: char frequency, length distribution"""
        series = self.df[col].dropna().astype(str)

        lengths = series.str.len()
        stats = {
            "count": int(series.count()),
            "missing": int(self.df[col].isna().sum()),
            "avg_length": float(lengths.mean()) if not lengths.empty else None,
            "min_length": float(lengths.min()) if not lengths.empty else None,
            "max_length": float(lengths.max()) if not lengths.empty else None,
            "common_lengths": lengths.value_counts().head(5).to_dict(),  # top 5
            "char_freq": (
                pd.Series(list("".join(series)))
                .value_counts()
                .head(10)
                .to_dict()  # top 10
                if not series.empty
                else None
            ),  # top 10 only
        }

        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    def _summarize_datetime_column(self, col: str):
        """Datetime stats: min/max date, temporal distribution patterns"""
        series = pd.to_datetime(self.df[col], error="coerce").dropna()

        stats = {
            "count": int(series.count()),
            "missing": int(self.df[col].isna().sum()),
            "min": str(series.min()) if not series.empty() else None,
            "max": str(series.max()) if not series.empty() else None,
            "year_counts": (
                series.dt.year.value_counts().to_dict() if not series.empty else None
            ),
            "month_counts": (
                series.dt.month.value_counts().to_dict() if not series.empty else None
            ),
            "day_counts": (
                series.dt.day.value_counts().to_dict() if not series.empty else None
            ),
        }

        if "variables" not in self.summaries:
            self.summaries["variables"] = {}
        self.summaries["variables"][col] = stats

    # =========================================================================
    # Interactions and Correlations Section
    # =========================================================================
    def _summarize_interactions(self):
        """Run interactions between variables"""
        self._scatter_plots_numeric()
        self._compute_correlation_matrices()
        self._compute_categorical_correlations()
        self._compute_mixed_correlations()

    def _scatter_plots_numeric(self):
        """
        Generate scatter plots between numeric variables
        for CLI: just the pairs
        for Web/Report: Plot them
        """
        numeric_columns = self.df.select_dtypes(include="number").columns
        pairs = [
            (c1, c2)
            for i, c1 in enumerate(numeric_columns)
            for c2 in numeric_columns[i + 1 :]
        ]
        self.summaries["scatter_pairs"] = pairs  # TODO: Plot these

    def _compute_correlation_matrices(self):
        """Compute Pearson/Spearman/Kendall correlations"""
        numeric_df = self.df.select_dtypes(include="number")
        corrs = {}
        if not numeric_df.empty:
            corrs["pearson"] = numeric_df.corr(method="pearson").to_dict()
            corrs["spearman"] = numeric_df.corr(method="spearman").to_dict()
            corrs["kendall"] = numeric_df.corr(method="kendall").to_dict()
        self.summaries["numeric_correlations"] = corrs

    def _compute_categorical_correlations(self):
        """Compute Cramer's V for categorical pairs"""
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
        """
        Compute correlation between categorical and numeric using ANOVA F-test as proxy
        """
        from scipy.stats import f_oneway
        import numpy as np

        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns
        num_cols = self.df.select_dtypes(include=["int64", "float64"]).columns
        mixed_corr = {}

        for cat in cat_cols:
            for num in num_cols:
                # Build groups for each level of categorical variable
                groups = []
                for level in self.df[cat].dropna().unique():
                    vals = self.df.loc[self.df[cat] == level, num].dropna().to_numpy()
                    if len(vals) > 1:  # Only include groups with more than 1 value
                        groups.append(vals)

                if len(groups) < 2:
                    continue  # Need at least 2 valid groups for ANOVA

                # Skip if all groups have zero variance
                if all(np.var(g, ddof=1) == 0 for g in groups):
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
        """Summarize missing value patterns"""
        missing_count = self.df.isnull().sum().to_dict()
        missing_percentage = (self.df.isnull().mean() * 100).round(2).to_dict()

        self.summaries["missing_values"] = {
            "count": missing_count,
            "percentage": missing_percentage,
        }

        # Simple missingness heatmap structure (list of missing row indexes)
        self.summaries["missing_patterns"] = {
            col: self.df[self.df[col].isna()].index.tolist()
            for col in self.df.columns
            if self.df[col].isna().any()
        }

    # =========================================================================
    # Critical Issues & Warning Checks
    # =========================================================================

    def _check_data_leakage(self, target_col: str = None):
        """Check if any feature is a perfect duplicate of the target"""
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
                            quick_fix="Drop the column before training.",
                        )
                    )

    def _check_high_missing_values(self, threshold: float = 0.4):
        """Flag columns with > threshold missing values"""
        for col in self.df.columns:
            missing_pct = self.df[col].isna().mean()
            if missing_pct > threshold:
                self.issues.append(
                    Issues(
                        category="missing_values",
                        severity="warning",
                        column=col,
                        description=f"{missing_pct:.1%} missing values in '{col}'",
                        impact_score="medium",
                        quick_fix="Consider imputing or dropping this column.",
                    )
                )

    def _check_empty_columns(self):
        """Detect columns that are entirely empty"""
        for col in self.df.columns:
            if self.df[col].notna().sum() == 0:
                self.issues.append(
                    Issues(
                        category="empty_column",
                        severity="critical",
                        column=col,
                        description=f"Column '{col}' has no non-missing values",
                        impact_score="high",
                        quick_fix="Drop the column.",
                    )
                )

    def _check_single_value_columns(self):
        """Detect columns with only one unique value"""
        for col in self.df.columns:
            if self.df[col].nunique(dropna=True) == 1:
                self.issues.append(
                    Issues(
                        category="single_value",
                        severity="warning",
                        column=col,
                        description=f"Column '{col}' contains only one unique value",
                        impact_score="low",
                        quick_fix="Drop this column (not informative).",
                    )
                )

    def _check_target_leakage_patterns(self, target_col: str = None):
        """
        Detect columns that strongly correlate with target (possible leakage).
        Works only if target_col is provided.
        """
        if target_col and target_col in self.df.columns:
            target = self.df[target_col]
            numeric_cols = self.df.select_dtypes(include="number").drop(
                columns=[target_col], errors="ignore"
            )
            if not numeric_cols.empty and pd.api.types.is_numeric_dtype(target):
                corrs = numeric_cols.corrwith(target).abs()
                for col, corr in corrs.items():
                    if corr > 0.95:
                        self.issues.append(
                            Issues(
                                category="target_leakage",
                                severity="critical",
                                column=col,
                                description=f"Column '{col}' highly correlated with target ({corr:.2f})",
                                impact_score="high",
                                quick_fix="Remove this column before training.",
                            )
                        )

    def _check_class_imbalance(self, target_col: str = None, threshold: float = 0.9):
        """Check if target variable is highly imbalanced"""
        if target_col and target_col in self.df.columns:
            counts = self.df[target_col].value_counts(normalize=True)
            if counts.iloc[0] > threshold:
                self.issues.append(
                    Issues(
                        category="class_imbalance",
                        severity="warning",
                        column=target_col,
                        description=f"Target '{target_col}' is imbalanced ({counts.iloc[0]:.1%} in one class)",
                        impact_score="medium",
                        quick_fix="Consider stratified sampling, resampling, or class-weighted models.",
                    )
                )

    def _check_high_cardinality(self, threshold: int = 100):
        """Detect categorical columns with too many unique values"""
        categorical_cols = self.df.select_dtypes(include="object").columns
        for col in categorical_cols:
            unique_count = self.df[col].nunique()
            if unique_count > threshold:
                self.issues.append(
                    Issues(
                        category="high_cardinality",
                        severity="warning",
                        column=col,
                        description=f"Column '{col}' has {unique_count} unique values",
                        impact_score="medium",
                        quick_fix="Consider feature hashing or grouping rare categories.",
                    )
                )

    def _check_duplicates(self):
        """Check for duplicate rows"""
        duplicate_rows = self.df.duplicated().sum()
        if duplicate_rows > 0:
            self.issues.append(
                Issues(
                    category="duplicates",
                    severity="warning",
                    column="__all__",
                    description=f"Dataset contains {duplicate_rows} duplicate rows",
                    impact_score="medium",
                    quick_fix="Drop duplicates if not meaningful.",
                )
            )

    def _check_mixed_data_types(self):
        """Detect columns with mixed dtypes (e.g., numbers + strings)"""
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
                        quick_fix="Clean or cast to a single type.",
                    )
                )

    def _check_outliers(self, z_threshold: float = 4.0):
        """Flag numeric columns with extreme outliers based on Z-score"""
        from scipy.stats import zscore

        numeric_df = self.df.select_dtypes(include="number").dropna()
        if numeric_df.empty:
            return

        z_scores = (numeric_df - numeric_df.mean()) / numeric_df.std(ddof=0)
        for col in numeric_df.columns:
            outlier_count = (abs(z_scores[col]) > z_threshold).sum()
            if outlier_count > 0:
                self.issues.append(
                    Issues(
                        category="outliers",
                        severity="warning",
                        column=col,
                        description=f"Column '{col}' has {outlier_count} potential outliers",
                        impact_score="medium",
                        quick_fix="Investigate values; consider winsorization or transformations.",
                    )
                )

    def _check_feature_correlation(self, threshold: float = 0.95):
        """Detect highly correlated numeric features"""
        numeric_df = self.df.select_dtypes(include="number")
        if numeric_df.empty:
            return

        corr_matrix = numeric_df.corr().abs()
        upper = corr_matrix.where(np.tril(np.ones(corr_matrix.shape)).astype(bool))
        correlated_pairs = [
            (col, row, val)
            for row in upper.index
            for col, val in upper[row].dropna().items()
            if val > threshold
        ]

        for col1, col2, corr in correlated_pairs:
            self.issues.append(
                Issues(
                    category="feature_correlation",
                    severity="warning",
                    column=f"{col1},{col2}",
                    description=f"Columns '{col1}' and '{col2}' are highly correlated ({corr:.2f})",
                    impact_score="medium",
                    quick_fix="Consider dropping one of the correlated features.",
                )
            )

    # =========================================================================
    # Generate Summary
    # =========================================================================
    def _generate_summary(self):
        """Generate final summary report"""

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
                }
                for issue in self.issues
            ],
            "summaries": self.summaries,
        }
