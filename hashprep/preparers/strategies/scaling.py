from ..models import FixSuggestion, ScaleMethod
from .base import FixStrategy


class ScalingStrategy(FixStrategy):
    """Strategy for scaling numeric variables."""

    SKLEARN_IMPORTS = [
        "from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler",
    ]

    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        cols = self._format_column_list(suggestion.columns)
        method = suggestion.method

        if method == ScaleMethod.STANDARD.value:
            return f"df[{cols}] = (df[{cols}] - df[{cols}].mean()) / df[{cols}].std()"

        if method == ScaleMethod.MINMAX.value:
            return f"df[{cols}] = (df[{cols}] - df[{cols}].min()) / (df[{cols}].max() - df[{cols}].min())"

        if method == ScaleMethod.ROBUST.value:
            lines = []
            for col in suggestion.columns:
                lines.append(f"q1_{col} = df['{col}'].quantile(0.25)")
                lines.append(f"q3_{col} = df['{col}'].quantile(0.75)")
                lines.append(f"iqr_{col} = q3_{col} - q1_{col}")
                lines.append(f"df['{col}'] = (df['{col}'] - df['{col}'].median()) / iqr_{col}")
            return "\n".join(lines)

        if method == ScaleMethod.MAXABS.value:
            return f"df[{cols}] = df[{cols}] / df[{cols}].abs().max()"

        return f"df[{cols}] = (df[{cols}] - df[{cols}].mean()) / df[{cols}].std()"

    def get_sklearn_transformer(self, suggestion: FixSuggestion) -> tuple[str | None, list[str]]:
        method = suggestion.method
        cols = suggestion.columns

        scaler_map = {
            ScaleMethod.STANDARD.value: "StandardScaler()",
            ScaleMethod.MINMAX.value: "MinMaxScaler()",
            ScaleMethod.ROBUST.value: "RobustScaler()",
            ScaleMethod.MAXABS.value: "MaxAbsScaler()",
        }

        return scaler_map.get(method, "StandardScaler()"), cols
