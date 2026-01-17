from typing import Dict, List, Optional
import pandas as pd
from ..utils.type_inference import infer_types

from ..checks import run_checks
from ..summaries import (
    get_dataset_preview,
    summarize_dataset_info,
    summarize_variable_types,
    add_reproduction_info,
    summarize_variables,
    summarize_interactions,
    summarize_missing_values,
)
from .visualizations import (
    plot_histogram,
    plot_bar,
    plot_heatmap,
    plot_scatter,
    plot_missing_bar,
    plot_missing_heatmap,
)

class DatasetAnalyzer:
    ALL_CHECKS = [
        "data_leakage", "high_missing_values", "empty_columns", "single_value_columns",
        "target_leakage_patterns", "class_imbalance", "high_cardinality", "duplicates",
        "mixed_data_types", "outliers", "feature_correlation", "categorical_correlation",
        "mixed_correlation", "dataset_missingness", "high_zero_counts",
        "extreme_text_lengths", "datetime_skew", "missing_patterns", "skewness",
    ]

    def __init__(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = None,
        selected_checks: Optional[List[str]] = None,
        include_plots: bool = False,
    ):
        self.df = df
        self.target_col = target_col
        self.selected_checks = selected_checks
        self.include_plots = include_plots
        self.issues = []
        self.summaries = {}
        self.column_types = infer_types(df)


    def analyze(self) -> Dict:
        # """analyze columns first for better results"""
        """Run all summaries and checks, return summary"""
        self.summaries.update(get_dataset_preview(self.df))
        self.summaries.update(summarize_dataset_info(self.df))
        self.summaries["variable_types"] = summarize_variable_types(self.df, column_types=self.column_types) # Todo: Implement this arg
        self.summaries["reproduction_info"] = add_reproduction_info(self.df)
        self.summaries["variables"] = summarize_variables(self.df)
        self.summaries.update(summarize_interactions(self.df))
        self.summaries.update(summarize_missing_values(self.df))

        if self.include_plots:
            self._generate_plots()

        checks_to_run = self.ALL_CHECKS if self.selected_checks is None else [
            check for check in self.selected_checks if check in self.ALL_CHECKS
        ]
        self.issues = run_checks(self, checks_to_run)

        return self._generate_summary()

    def _generate_plots(self):
        # Variable plots
        for col, stats in self.summaries["variables"].items():
            plots = {}
            if stats["category"] == "Numeric":
                if stats["histogram"]["counts"]:
                    plots["histogram"] = plot_histogram(self.df[col].dropna(), f"Histogram of {col}")
            elif stats["category"] in ["Categorical", "Boolean"]:
                if stats["categories"].get("common_values"):
                    series = self.df[col].dropna().astype(str).value_counts().head(10)
                    plots["common_values_bar"] = plot_bar(series, f"Top Values of {col}", col, "Count")
            elif stats["category"] == "Text":
                 if stats["words"]:
                     word_counts = {w: d['count'] for w, d in stats['words'].items()}
                     series = pd.Series(word_counts).head(10)
                     plots["word_bar"] = plot_bar(series, f"Top Words in {col}", "Words", "Count")
            
            stats["plots"] = plots

        # Interaction plots
        # Numeric correlations
        if "pearson" in self.summaries.get("numeric_correlations", {}):
            numeric_df = self.df.select_dtypes(include="number")
            if not numeric_df.empty:
                if "plots" not in self.summaries["numeric_correlations"]:
                    self.summaries["numeric_correlations"]["plots"] = {}
                
                for method in ["pearson", "spearman", "kendall"]:
                     corr = numeric_df.corr(method=method)
                     self.summaries["numeric_correlations"]["plots"][method] = plot_heatmap(corr, f"{method.capitalize()} Correlation")

        # Scatter plots (limit to first 5 pairs to avoid bloat)
        pairs = self.summaries.get("scatter_pairs", [])
        scatter_plots = {}
        for c1, c2 in pairs[:5]:
             scatter_plots[f"{c1}__{c2}"] = plot_scatter(self.df, c1, c2)
        self.summaries["scatter_plots"] = scatter_plots

        # Missing value plots
        missing_counts = self.summaries["missing_values"]["count"]
        missing_series = pd.Series(missing_counts)
        self.summaries["plots"] = {
            "missing_bar": plot_missing_bar(missing_series),
            "missing_heatmap": plot_missing_heatmap(self.df)
        }

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
            "column_types": self.column_types,
        }