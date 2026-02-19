from ..models import EncodeMethod, FixSuggestion
from .base import FixStrategy


class EncodingStrategy(FixStrategy):
    """Strategy for encoding categorical variables."""

    SKLEARN_IMPORTS = [
        "from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder",
    ]

    def generate_pandas_code(self, suggestion: FixSuggestion) -> str:
        method = suggestion.method
        cols = suggestion.columns

        if method == EncodeMethod.ONEHOT.value:
            cols_str = self._format_column_list(cols)
            return f"df = pd.get_dummies(df, columns={cols_str}, drop_first=True)"

        if method == EncodeMethod.LABEL.value:
            lines = []
            for col in cols:
                lines.append(f"df['{col}'] = df['{col}'].astype('category').cat.codes")
            return "\n".join(lines)

        if method == EncodeMethod.ORDINAL.value:
            lines = []
            for col in cols:
                lines.append(f"df['{col}'] = df['{col}'].astype('category').cat.codes")
            return "\n".join(lines)

        if method == EncodeMethod.FREQUENCY.value:
            lines = []
            for col in cols:
                lines.append(f"freq_{col} = df['{col}'].value_counts(normalize=True)")
                lines.append(f"df['{col}_encoded'] = df['{col}'].map(freq_{col})")
            return "\n".join(lines)

        return f"df = pd.get_dummies(df, columns={self._format_column_list(cols)})"

    def get_sklearn_transformer(self, suggestion: FixSuggestion) -> tuple[str | None, list[str]]:
        method = suggestion.method
        cols = suggestion.columns

        if method == EncodeMethod.ONEHOT.value:
            return "OneHotEncoder(handle_unknown='ignore', sparse_output=False)", cols

        if method in (EncodeMethod.ORDINAL.value, EncodeMethod.LABEL.value):
            return (
                "OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)",
                cols,
            )

        if method == EncodeMethod.FREQUENCY.value:
            return None, cols

        return "OneHotEncoder(handle_unknown='ignore', sparse_output=False)", cols
