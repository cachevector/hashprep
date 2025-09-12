from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd
import hashlib


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

        return self._generate_summary()

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
