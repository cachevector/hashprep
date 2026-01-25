from typing import Dict, List, Optional

from ..checks.core import Issue
from .fix_registry import FixRegistry
from .models import FixSuggestion


class SuggestionProvider:
    """
    Analyzes issues and generates structured fix suggestions.
    Uses column metadata for context-aware recommendations.
    """

    def __init__(
        self,
        issues: List[Issue],
        column_types: Optional[Dict[str, str]] = None,
        target_col: Optional[str] = None,
        column_stats: Optional[Dict[str, Dict]] = None,
    ):
        self.issues = issues
        self.column_types = column_types or {}
        self.target_col = target_col
        self.column_stats = column_stats or {}
        self.registry = FixRegistry(self.column_types, target_col, column_stats)

    def get_suggestions(self) -> List[FixSuggestion]:
        """Generate all fix suggestions, deduplicated and prioritized."""
        suggestions: List[FixSuggestion] = []
        seen_columns: set = set()

        sorted_issues = sorted(
            self.issues,
            key=lambda i: (0 if i.severity == "critical" else 1, i.column),
        )

        for issue in sorted_issues:
            issue_suggestions = self.registry.get_suggestions(issue)
            for suggestion in issue_suggestions:
                col_key = tuple(sorted(suggestion.columns))
                if col_key not in seen_columns:
                    suggestions.append(suggestion)
                    seen_columns.add(col_key)

        return sorted(suggestions, key=lambda s: s.priority)

    def get_suggestions_by_type(self) -> Dict[str, List[FixSuggestion]]:
        """Group suggestions by fix type for organized output."""
        grouped: Dict[str, List[FixSuggestion]] = {}
        for suggestion in self.get_suggestions():
            key = suggestion.fix_type.value
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(suggestion)
        return grouped

    def get_legacy_suggestions(self) -> List[Dict]:
        """
        Return suggestions in legacy format for backward compatibility.
        Maps to the old {issue, code} dict format.
        """
        from .codegen import CodeGenerator

        suggestions = self.get_suggestions()
        codegen = CodeGenerator(suggestions)

        legacy = []
        for suggestion in suggestions:
            code = codegen._generate_code_for_suggestion(suggestion)
            legacy.append(
                {
                    "issue": Issue(
                        category=suggestion.source_issue_category,
                        severity="warning",
                        column=suggestion.columns[0] if suggestion.columns else "",
                        description=suggestion.reason,
                        impact_score="medium",
                        quick_fix=code,
                    ),
                    "code": code,
                }
            )
        return legacy
