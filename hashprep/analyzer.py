from dataclasses import dataclass
from typing import Dict
import pandas as pd


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
        self.issues = []
        self.summaries = {}

    def analyze(self) -> Dict:
        """Run all checks and return summary"""

        self._get_dataset_preview()
        return self._generate_summary()

    def _get_dataset_preview(self):
        head = self.df.head()
        tail = self.df.tail()
        sample = self.df.sample(10)
        dataset_preview = {
            "head": head,
            "tail": tail,
            "sample": sample
        }
        self.summaries.update(dataset_preview)

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
                    "quick_fix": issue.quick_fix
                }
                for issue in self.issues
            ],
            "dataset_info": {
                "rows": len(self.df),
                "columns": len(self.df.columns),
                "memory_mb": round(self.df.memory_usage(deep=True).sum() / 1024**2, 1),
                "missing_percentage": round((self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100, 1)
            },
            "summaries": self.summaries
        }
