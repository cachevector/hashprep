from ..models import FixSuggestion
from .base import FixStrategy


class OutlierStrategy(FixStrategy):
    """Strategy for handling outliers through clipping or removal."""

    SKLEARN_IMPORTS = [
        "from sklearn.preprocessing import RobustScaler",
    ]

    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        cols = suggestion.columns
        clip_method = suggestion.parameters.get("clip_method", "iqr")

        if clip_method == "iqr":
            lines = []
            for col in cols:
                lines.append(f"q1_{col}, q3_{col} = df['{col}'].quantile([0.25, 0.75])")
                lines.append(f"iqr_{col} = q3_{col} - q1_{col}")
                lines.append(f"lower_{col}, upper_{col} = q1_{col} - 1.5 * iqr_{col}, q3_{col} + 1.5 * iqr_{col}")
                lines.append(f"df['{col}'] = df['{col}'].clip(lower=lower_{col}, upper=upper_{col})")
            return "\n".join(lines)

        if clip_method == "percentile":
            lower_pct = suggestion.parameters.get("lower_pct", 0.01)
            upper_pct = suggestion.parameters.get("upper_pct", 0.99)
            lines = []
            for col in cols:
                lines.append(f"low_{col}, high_{col} = df['{col}'].quantile([{lower_pct}, {upper_pct}])")
                lines.append(f"df['{col}'] = df['{col}'].clip(lower=low_{col}, upper=high_{col})")
            return "\n".join(lines)

        if clip_method == "zscore":
            z_threshold = suggestion.parameters.get("z_threshold", 3.0)
            lines = []
            for col in cols:
                lines.append(f"mean_{col} = df['{col}'].mean()")
                lines.append(f"std_{col} = df['{col}'].std()")
                lines.append(f"lower_{col} = mean_{col} - {z_threshold} * std_{col}")
                lines.append(f"upper_{col} = mean_{col} + {z_threshold} * std_{col}")
                lines.append(f"df['{col}'] = df['{col}'].clip(lower=lower_{col}, upper=upper_{col})")
            return "\n".join(lines)

        return self._generate_iqr_code(cols)

    def _generate_iqr_code(self, cols: list[str]) -> str:
        lines = []
        for col in cols:
            lines.append(f"q1_{col}, q3_{col} = df['{col}'].quantile([0.25, 0.75])")
            lines.append(f"iqr_{col} = q3_{col} - q1_{col}")
            lines.append(
                f"df['{col}'] = df['{col}'].clip(lower=q1_{col} - 1.5 * iqr_{col}, upper=q3_{col} + 1.5 * iqr_{col})"
            )
        return "\n".join(lines)

    def get_sklearn_transformer(self, suggestion: FixSuggestion) -> tuple[str | None, list[str]]:
        return None, suggestion.columns
