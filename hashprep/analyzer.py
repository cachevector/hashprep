from typing import Dict, List, Optional
import pandas as pd

from .checks import run_checks
from .summaries import (
    get_dataset_preview,
    summarize_dataset_info,
    summarize_variable_types,
    add_reproduction_info,
    summarize_variables,
    summarize_interactions,
    summarize_missing_values,
)

class DatasetAnalyzer:
    def __init__(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = None,
        selected_checks: Optional[List[str]] = None,
    ):
        self.df = df
        self.target_col = target_col
        self.selected_checks = selected_checks
        self.issues = []
        self.summaries = {}
        self.all_checks = [
            "data_leakage", "high_missing_values", "empty_columns", "single_value_columns",
            "target_leakage_patterns", "class_imbalance", "high_cardinality", "duplicates",
            "mixed_data_types", "outliers", "feature_correlation", "categorical_correlation",
            "mixed_correlation", "dataset_missingness", "high_zero_counts",
            "extreme_text_lengths", "datetime_skew", "missing_patterns",
        ]

    def analyze(self) -> Dict:
        """Run all summaries and checks, return summary"""
        self.summaries.update(get_dataset_preview(self.df))
        self.summaries.update(summarize_dataset_info(self.df))
        self.summaries["variable_types"] = summarize_variable_types(self.df)
        self.summaries["reproduction_info"] = add_reproduction_info(self.df)
        self.summaries["variables"] = summarize_variables(self.df)
        self.summaries.update(summarize_interactions(self.df))
        self.summaries.update(summarize_missing_values(self.df))

        checks_to_run = self.all_checks if self.selected_checks is None else [
            check for check in self.selected_checks if check in self.all_checks
        ]
        self.issues = run_checks(self, checks_to_run)

        return self._generate_summary()

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