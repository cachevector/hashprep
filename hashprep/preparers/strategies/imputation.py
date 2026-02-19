from ..models import FixSuggestion, ImputeMethod
from .base import FixStrategy


class ImputationStrategy(FixStrategy):
    """Strategy for handling missing values through imputation."""

    SKLEARN_IMPORTS = [
        "from sklearn.impute import SimpleImputer, KNNImputer",
    ]

    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        cols = self._format_column_list(suggestion.columns)
        method = suggestion.method

        if method == ImputeMethod.MEAN.value:
            return f"df[{cols}] = df[{cols}].fillna(df[{cols}].mean())"

        if method == ImputeMethod.MEDIAN.value:
            return f"df[{cols}] = df[{cols}].fillna(df[{cols}].median())"

        if method == ImputeMethod.MODE.value:
            lines = []
            for col in suggestion.columns:
                lines.append(f"df['{col}'] = df['{col}'].fillna(df['{col}'].mode().iloc[0])")
            return "\n".join(lines)

        if method == ImputeMethod.CONSTANT.value:
            fill_value = suggestion.parameters.get("fill_value", 0)
            return f"df[{cols}] = df[{cols}].fillna({repr(fill_value)})"

        if method == ImputeMethod.KNN.value:
            n_neighbors = suggestion.parameters.get("n_neighbors", 5)
            lines = [
                "from sklearn.impute import KNNImputer",
                f"imputer = KNNImputer(n_neighbors={n_neighbors})",
                f"df[{cols}] = imputer.fit_transform(df[{cols}])",
            ]
            return "\n".join(lines)

        return f"df[{cols}] = df[{cols}].fillna(df[{cols}].median())"

    def get_sklearn_transformer(self, suggestion: FixSuggestion) -> tuple[str | None, list[str]]:
        method = suggestion.method
        cols = suggestion.columns

        if method == ImputeMethod.KNN.value:
            n_neighbors = suggestion.parameters.get("n_neighbors", 5)
            return f"KNNImputer(n_neighbors={n_neighbors})", cols

        strategy_map = {
            ImputeMethod.MEAN.value: "mean",
            ImputeMethod.MEDIAN.value: "median",
            ImputeMethod.MODE.value: "most_frequent",
            ImputeMethod.CONSTANT.value: "constant",
        }
        strategy = strategy_map.get(method, "median")

        if method == ImputeMethod.CONSTANT.value:
            fill_value = suggestion.parameters.get("fill_value", 0)
            return f"SimpleImputer(strategy='constant', fill_value={repr(fill_value)})", cols

        return f"SimpleImputer(strategy='{strategy}')", cols
