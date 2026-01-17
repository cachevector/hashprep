from typing import List, Dict
from ..checks.core import Issue

class SuggestionProvider:
    def __init__(self, issues: List[Issue]):
        self.issues = issues

    def get_suggestions(self) -> List[Dict]:
        suggestions_by_col = {}
        for issue in self.issues:
            code = self._generate_code(issue)
            if code:
                # Prioritize critical issues for the same column
                if issue.column not in suggestions_by_col or issue.severity == "critical":
                    suggestions_by_col[issue.column] = {
                        "issue": issue,
                        "code": code
                    }
        return list(suggestions_by_col.values())

    def _generate_code(self, issue: Issue) -> str:
        if issue.category == "missing_values" or issue.category == "empty_column":
            return f"df.drop(columns=['{issue.column}'], inplace=True)"
        
        if issue.category == "duplicates":
            return "df.drop_duplicates(inplace=True)"
        
        if issue.category == "single_value":
            return f"df.drop(columns=['{issue.column}'], inplace=True)"
        
        if issue.category == "high_cardinality":
            return f"# Consider target encoding or grouping rare categories for '{issue.column}'\n# from sklearn.preprocessing import TargetEncoder"

        if issue.category == "outliers":
             return f"# Consider capping or removing outliers in '{issue.column}'\n# q_low = df['{issue.column}'].quantile(0.01)\n# q_hi  = df['{issue.column}'].quantile(0.99)\n# df = df[(df['{issue.column}'] < q_hi) & (df['{issue.column}'] > q_low)]"

        return ""
