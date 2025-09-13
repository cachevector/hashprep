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
        self._summarize_variables()

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
            "top_values": series.value_counts().head(10).to_dict(), # top 10 only
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
            "common_lengths": lengths.value_counts().head(5).to_dict(), # top 5
            "char_freq": (
                pd.Series(list("".join(series))).value_counts().head(10).to_dict() # top 10
                if not series.empty
                else None
            ), # top 10 only
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
