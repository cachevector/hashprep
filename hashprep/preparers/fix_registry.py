from collections.abc import Callable

from ..checks.core import Issue
from .models import (
    EncodeMethod,
    FixSuggestion,
    FixType,
    ImputeMethod,
    TransformMethod,
)


class FixRegistry:
    """Maps issue categories to fix suggestion generators."""

    def __init__(
        self,
        column_types: dict[str, str],
        target_col: str | None = None,
        column_stats: dict[str, dict] | None = None,
    ):
        self.column_types = column_types
        self.target_col = target_col
        self.column_stats = column_stats or {}

        self._handlers: dict[str, Callable[[Issue], list[FixSuggestion]]] = {
            "missing_values": self._suggest_missing_fix,
            "high_missing_values": self._suggest_missing_fix,
            "empty_column": self._suggest_drop,
            "single_value": self._suggest_drop,
            "single_value_columns": self._suggest_drop,
            "high_cardinality": self._suggest_encoding,
            "duplicates": self._suggest_dedupe,
            "outliers": self._suggest_outlier_fix,
            "skewness": self._suggest_transform,
            "mixed_types": self._suggest_drop,
            "mixed_data_types": self._suggest_drop,
            "data_leakage": self._suggest_drop,
            "target_leakage": self._suggest_drop_with_warning,
            "target_leakage_patterns": self._suggest_drop_with_warning,
            "feature_correlation": self._suggest_drop_correlated,
        }

    def get_suggestions(self, issue: Issue) -> list[FixSuggestion]:
        """Get fix suggestions for an issue."""
        handler = self._handlers.get(issue.category)
        if handler:
            return handler(issue)
        return []

    def _get_column_type(self, col: str) -> str:
        return self.column_types.get(col, "Unknown")

    def _get_missing_pct(self, issue: Issue) -> float:
        """Extract missing percentage from issue description."""
        desc = issue.description.lower()
        if "%" in desc:
            try:
                for part in desc.split():
                    if "%" in part:
                        return float(part.replace("%", "").replace(",", ""))
            except ValueError:
                pass
        return 50.0

    def _suggest_missing_fix(self, issue: Issue) -> list[FixSuggestion]:
        col = issue.column
        col_type = self._get_column_type(col)
        missing_pct = self._get_missing_pct(issue)

        if missing_pct > 70 or issue.severity == "critical":
            return [
                FixSuggestion(
                    fix_type=FixType.DROP_COLUMN,
                    columns=[col],
                    priority=0,
                    reason=f"Column '{col}' has {missing_pct:.0f}% missing values",
                    source_issue_category=issue.category,
                )
            ]

        if col_type == "Numeric":
            return [
                FixSuggestion(
                    fix_type=FixType.IMPUTE,
                    columns=[col],
                    method=ImputeMethod.MEDIAN.value,
                    priority=1,
                    reason=f"Impute missing values in numeric column '{col}'",
                    source_issue_category=issue.category,
                )
            ]

        if col_type in ("Categorical", "Text"):
            return [
                FixSuggestion(
                    fix_type=FixType.IMPUTE,
                    columns=[col],
                    method=ImputeMethod.MODE.value,
                    priority=1,
                    reason=f"Impute missing values in categorical column '{col}'",
                    source_issue_category=issue.category,
                )
            ]

        return [
            FixSuggestion(
                fix_type=FixType.IMPUTE,
                columns=[col],
                method=ImputeMethod.MEDIAN.value,
                priority=1,
                reason=f"Impute missing values in '{col}'",
                source_issue_category=issue.category,
            )
        ]

    def _suggest_drop(self, issue: Issue) -> list[FixSuggestion]:
        return [
            FixSuggestion(
                fix_type=FixType.DROP_COLUMN,
                columns=[issue.column],
                priority=0,
                reason=f"Drop column '{issue.column}' ({issue.category})",
                source_issue_category=issue.category,
            )
        ]

    def _suggest_drop_with_warning(self, issue: Issue) -> list[FixSuggestion]:
        return [
            FixSuggestion(
                fix_type=FixType.DROP_COLUMN,
                columns=[issue.column],
                priority=0,
                reason=f"Drop column '{issue.column}' (potential data leakage - verify manually)",
                source_issue_category=issue.category,
            )
        ]

    def _suggest_encoding(self, issue: Issue) -> list[FixSuggestion]:
        col = issue.column
        desc = issue.description.lower()

        unique_count = 100
        try:
            for part in desc.split():
                if part.isdigit():
                    unique_count = int(part)
                    break
        except ValueError:
            pass

        if unique_count > 50:
            return [
                FixSuggestion(
                    fix_type=FixType.ENCODE,
                    columns=[col],
                    method=EncodeMethod.FREQUENCY.value,
                    priority=2,
                    reason=f"Frequency encode high-cardinality column '{col}'",
                    source_issue_category=issue.category,
                )
            ]

        if unique_count <= 10:
            return [
                FixSuggestion(
                    fix_type=FixType.ENCODE,
                    columns=[col],
                    method=EncodeMethod.ONEHOT.value,
                    priority=2,
                    reason=f"One-hot encode categorical column '{col}'",
                    source_issue_category=issue.category,
                )
            ]

        return [
            FixSuggestion(
                fix_type=FixType.ENCODE,
                columns=[col],
                method=EncodeMethod.FREQUENCY.value,
                priority=2,
                reason=f"Frequency encode categorical column '{col}'",
                source_issue_category=issue.category,
            )
        ]

    def _suggest_dedupe(self, issue: Issue) -> list[FixSuggestion]:
        return [
            FixSuggestion(
                fix_type=FixType.DROP_DUPLICATES,
                columns=["__dataset__"],
                parameters={"keep": "first"},
                priority=0,
                reason="Remove duplicate rows",
                source_issue_category=issue.category,
            )
        ]

    def _suggest_outlier_fix(self, issue: Issue) -> list[FixSuggestion]:
        return [
            FixSuggestion(
                fix_type=FixType.CLIP_OUTLIERS,
                columns=[issue.column],
                parameters={"clip_method": "iqr"},
                priority=3,
                reason=f"Clip outliers in '{issue.column}' using IQR method",
                source_issue_category=issue.category,
            )
        ]

    def _suggest_transform(self, issue: Issue) -> list[FixSuggestion]:
        col = issue.column
        desc = issue.description.lower()

        skewness = 5.0
        try:
            if "skewness" in desc:
                parts = desc.split("skewness")
                if len(parts) > 1:
                    for part in parts[1].split():
                        try:
                            skewness = abs(float(part.replace(",", "").replace(":", "")))
                            break
                        except ValueError:
                            continue
        except (ValueError, IndexError):
            pass

        if skewness > 10:
            return [
                FixSuggestion(
                    fix_type=FixType.TRANSFORM,
                    columns=[col],
                    method=TransformMethod.YEOJOHNSON.value,
                    priority=4,
                    reason=f"Apply Yeo-Johnson transform to highly skewed column '{col}'",
                    source_issue_category=issue.category,
                )
            ]

        return [
            FixSuggestion(
                fix_type=FixType.TRANSFORM,
                columns=[col],
                method=TransformMethod.LOG1P.value,
                priority=4,
                reason=f"Apply log1p transform to skewed column '{col}'",
                source_issue_category=issue.category,
            )
        ]

    def _suggest_drop_correlated(self, issue: Issue) -> list[FixSuggestion]:
        col = issue.column
        return [
            FixSuggestion(
                fix_type=FixType.DROP_COLUMN,
                columns=[col],
                priority=5,
                reason=f"Drop highly correlated column '{col}'",
                source_issue_category=issue.category,
            )
        ]
