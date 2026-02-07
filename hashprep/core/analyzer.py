import time
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from ..checks import run_checks
from ..summaries import (
    add_reproduction_info,
    get_dataset_preview,
    get_duplicate_info,
    summarize_dataset_info,
    summarize_interactions,
    summarize_missing_values,
    summarize_variable_type_counts,
    summarize_variable_types,
    summarize_variables,
)
from ..utils.sampling import DatasetSampler, SamplingConfig
from ..utils.type_inference import infer_types
from .visualizations import (
    plot_bar,
    plot_heatmap,
    plot_histogram,
    plot_missing_bar,
    plot_missing_heatmap,
    plot_scatter,
)


class DatasetAnalyzer:
    ALL_CHECKS = [
        "empty_dataset",
        "data_leakage",
        "high_missing_values",
        "empty_columns",
        "single_value_columns",
        "target_leakage_patterns",
        "class_imbalance",
        "high_cardinality",
        "duplicates",
        "mixed_data_types",
        "outliers",
        "feature_correlation",
        "categorical_correlation",
        "mixed_correlation",
        "dataset_missingness",
        "high_zero_counts",
        "extreme_text_lengths",
        "datetime_skew",
        "missing_patterns",
        "skewness",
        "dataset_drift",
        "uniform_distribution",
        "unique_values",
        "infinite_values",
        "constant_length",
    ]

    def __init__(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = None,
        selected_checks: Optional[List[str]] = None,
        include_plots: bool = False,
        comparison_df: Optional[pd.DataFrame] = None,
        sampling_config: Optional[SamplingConfig] = None,
        auto_sample: bool = True,
    ):
        self.comparison_df = comparison_df
        self.target_col = target_col
        self.selected_checks = selected_checks
        self.include_plots = include_plots
        self.issues: List = []
        self.summaries: Dict = {}

        self.sampler: Optional[DatasetSampler] = None
        if auto_sample:
            self.sampler = DatasetSampler(sampling_config)
            if self.sampler.should_sample(df):
                self.df = self.sampler.sample(df)
                self.df_full = df
            else:
                self.df = df
                self.df_full = df
        else:
            self.df = df
            self.df_full = df

        self.column_types = infer_types(self.df)

    def analyze(self) -> Dict:
        """Run all summaries and checks, return summary."""
        analysis_start = datetime.now()
        start_time = time.time()

        self.summaries.update(get_dataset_preview(self.df))
        self.summaries.update(summarize_dataset_info(self.df))

        duplicate_info = get_duplicate_info(self.df)
        self.summaries["dataset_info"].update(duplicate_info)

        self.summaries["variable_types"] = summarize_variable_types(
            self.df, column_types=self.column_types
        )
        self.summaries["variable_type_counts"] = summarize_variable_type_counts(
            self.df, column_types=self.column_types
        )
        self.summaries["reproduction_info"] = add_reproduction_info(self.df)
        self.summaries["variables"] = summarize_variables(self.df)
        self.summaries.update(summarize_interactions(self.df))
        self.summaries.update(summarize_missing_values(self.df))

        if self.sampler:
            self.summaries["sampling_info"] = self.sampler.get_sampling_info()

        if self.include_plots:
            self._generate_plots()

        checks_to_run = (
            self.ALL_CHECKS
            if self.selected_checks is None
            else [check for check in self.selected_checks if check in self.ALL_CHECKS]
        )
        self.issues = run_checks(self, checks_to_run)

        analysis_end = datetime.now()
        duration_seconds = time.time() - start_time
        self.summaries["reproduction_info"]["analysis_started"] = analysis_start.isoformat()
        self.summaries["reproduction_info"]["analysis_finished"] = analysis_end.isoformat()
        self.summaries["reproduction_info"]["duration_seconds"] = round(duration_seconds, 2)

        return self._generate_summary()

    def _generate_plots(self):
        for col, stats in self.summaries["variables"].items():
            plots = {}
            if stats["category"] == "Numeric":
                if stats["histogram"]["counts"]:
                    plots["histogram"] = plot_histogram(
                        self.df[col].dropna(), f"Histogram of {col}"
                    )
            elif stats["category"] in ["Categorical", "Boolean"]:
                if stats["categories"].get("common_values"):
                    series = self.df[col].dropna().astype(str).value_counts().head(10)
                    plots["common_values_bar"] = plot_bar(
                        series, f"Top Values of {col}", col, "Count"
                    )
            elif stats["category"] == "Text":
                if stats["words"]:
                    word_counts = {w: d["count"] for w, d in stats["words"].items()}
                    series = pd.Series(word_counts).head(10)
                    plots["word_bar"] = plot_bar(
                        series, f"Top Words in {col}", "Words", "Count"
                    )

            stats["plots"] = plots

        if "pearson" in self.summaries.get("numeric_correlations", {}):
            numeric_df = self.df.select_dtypes(include="number")
            if not numeric_df.empty:
                if "plots" not in self.summaries["numeric_correlations"]:
                    self.summaries["numeric_correlations"]["plots"] = {}

                for method in ["pearson", "spearman", "kendall"]:
                    corr = numeric_df.corr(method=method)
                    self.summaries["numeric_correlations"]["plots"][method] = (
                        plot_heatmap(corr, f"{method.capitalize()} Correlation")
                    )

        pairs = self.summaries.get("scatter_pairs", [])
        scatter_plots = {}
        for c1, c2 in pairs[:5]:
            scatter_plots[f"{c1}__{c2}"] = plot_scatter(self.df, c1, c2)
        self.summaries["scatter_plots"] = scatter_plots

        missing_counts = self.summaries["missing_values"]["count"]
        missing_series = pd.Series(missing_counts)
        self.summaries["plots"] = {
            "missing_bar": plot_missing_bar(missing_series),
            "missing_heatmap": plot_missing_heatmap(self.df),
        }

    def _generate_summary(self):
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        warning_issues = [i for i in self.issues if i.severity == "warning"]

        summary = {
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
            "column_types": self.column_types,
        }

        if self.sampler:
            summary["sampling_info"] = self.sampler.get_sampling_info()

        return summary
