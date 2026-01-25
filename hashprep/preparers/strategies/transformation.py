from typing import List, Optional, Tuple

from ..models import FixSuggestion, TransformMethod
from .base import FixStrategy


class TransformationStrategy(FixStrategy):
    """Strategy for transforming skewed distributions."""

    SKLEARN_IMPORTS = [
        "from sklearn.preprocessing import PowerTransformer, FunctionTransformer",
        "import numpy as np",
    ]

    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        cols = self._format_column_list(suggestion.columns)
        method = suggestion.method

        if method == TransformMethod.LOG.value:
            return f"df[{cols}] = np.log(df[{cols}].clip(lower=1e-10))"

        if method == TransformMethod.LOG1P.value:
            return f"df[{cols}] = np.log1p(df[{cols}].clip(lower=0))"

        if method == TransformMethod.SQRT.value:
            return f"df[{cols}] = np.sqrt(df[{cols}].clip(lower=0))"

        if method == TransformMethod.BOXCOX.value:
            lines = [
                "from scipy.stats import boxcox",
            ]
            for col in suggestion.columns:
                lines.append(
                    f"df['{col}'], _ = boxcox(df['{col}'].clip(lower=1e-10).values)"
                )
            return "\n".join(lines)

        if method == TransformMethod.YEOJOHNSON.value:
            lines = [
                "from sklearn.preprocessing import PowerTransformer",
                "pt = PowerTransformer(method='yeo-johnson')",
            ]
            for col in suggestion.columns:
                lines.append(
                    f"df[['{col}']] = pt.fit_transform(df[['{col}']])"
                )
            return "\n".join(lines)

        return f"df[{cols}] = np.log1p(df[{cols}].clip(lower=0))"

    def get_sklearn_transformer(
        self, suggestion: FixSuggestion
    ) -> Tuple[Optional[str], List[str]]:
        method = suggestion.method
        cols = suggestion.columns

        if method == TransformMethod.BOXCOX.value:
            return "PowerTransformer(method='box-cox')", cols

        if method == TransformMethod.YEOJOHNSON.value:
            return "PowerTransformer(method='yeo-johnson')", cols

        if method == TransformMethod.LOG1P.value:
            return "FunctionTransformer(np.log1p, validate=True)", cols

        if method == TransformMethod.LOG.value:
            return (
                "FunctionTransformer(lambda x: np.log(np.clip(x, 1e-10, None)), validate=True)",
                cols,
            )

        if method == TransformMethod.SQRT.value:
            return (
                "FunctionTransformer(lambda x: np.sqrt(np.clip(x, 0, None)), validate=True)",
                cols,
            )

        return "PowerTransformer(method='yeo-johnson')", cols
