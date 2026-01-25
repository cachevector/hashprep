from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..models import FixSuggestion


class FixStrategy(ABC):
    """Base class for all fix strategies."""

    SKLEARN_IMPORTS: List[str] = []

    @abstractmethod
    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        """Generate pandas-based Python code for the fix."""
        pass

    @abstractmethod
    def get_sklearn_transformer(
        self, suggestion: FixSuggestion
    ) -> Tuple[Optional[str], List[str]]:
        """
        Return (transformer_instance_code, column_list) for sklearn pipeline.
        Returns (None, []) if not applicable to sklearn pipelines.
        """
        pass

    def get_sklearn_imports(self) -> List[str]:
        """Return required sklearn import statements."""
        return self.SKLEARN_IMPORTS

    def _format_column_list(self, columns: List[str]) -> str:
        """Format column list as Python literal."""
        if len(columns) == 1:
            return f"['{columns[0]}']"
        return str(columns)
