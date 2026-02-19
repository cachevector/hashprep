from ..models import FixSuggestion
from .base import FixStrategy


class ColumnDropStrategy(FixStrategy):
    """Strategy for dropping columns."""

    SKLEARN_IMPORTS: list[str] = []

    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        cols = self._format_column_list(suggestion.columns)
        return f"df = df.drop(columns={cols})"

    def get_sklearn_transformer(self, suggestion: FixSuggestion) -> tuple[str | None, list[str]]:
        return "'drop'", suggestion.columns


class DuplicateRemovalStrategy(FixStrategy):
    """Strategy for removing duplicate rows."""

    SKLEARN_IMPORTS: list[str] = []

    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        keep = suggestion.parameters.get("keep", "first")
        return f"df = df.drop_duplicates(keep='{keep}')"

    def get_sklearn_transformer(self, suggestion: FixSuggestion) -> tuple[str | None, list[str]]:
        return None, []
