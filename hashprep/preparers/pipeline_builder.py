from typing import Any

from .models import FixSuggestion, FixType
from .strategies import (
    ColumnDropStrategy,
    EncodingStrategy,
    ImputationStrategy,
    ScalingStrategy,
    TransformationStrategy,
)


class PipelineBuilder:
    """
    Builds sklearn Pipeline/ColumnTransformer from fix suggestions.
    Generates both code and actual pipeline objects.
    """

    STRATEGY_MAP: dict[FixType, Any] = {
        FixType.DROP_COLUMN: ColumnDropStrategy(),
        FixType.IMPUTE: ImputationStrategy(),
        FixType.ENCODE: EncodingStrategy(),
        FixType.SCALE: ScalingStrategy(),
        FixType.TRANSFORM: TransformationStrategy(),
    }

    def __init__(self, suggestions: list[FixSuggestion]):
        self.suggestions = suggestions
        self._validate_suggestions()

    def _validate_suggestions(self) -> None:
        """Mark suggestions that cannot be done in sklearn pipeline."""
        for s in self.suggestions:
            if s.fix_type == FixType.DROP_DUPLICATES:
                s.parameters["pre_pipeline"] = True
            if s.fix_type == FixType.CLIP_OUTLIERS:
                s.parameters["pre_pipeline"] = True

    def generate_pipeline_code(self) -> str:
        """Generate sklearn pipeline code as a string."""
        code: list[str] = []

        code.append('"""')
        code.append("Auto-generated sklearn preprocessing pipeline by HashPrep.")
        code.append("Review and adapt before production use.")
        code.append('"""')
        code.append("")

        code.extend(self._collect_all_imports())
        code.append("")
        code.append("")

        code.append("def build_preprocessing_pipeline():")
        code.append('    """Build sklearn preprocessing pipeline."""')
        code.append("")

        transformers = self._build_transformer_list()

        if not transformers:
            code.append("    # No transformations needed")
            code.append("    return None")
        else:
            code.append("    transformers = [")
            for name, transformer_code, columns in transformers:
                cols_str = str(columns)
                code.append(f"        ('{name}', {transformer_code}, {cols_str}),")
            code.append("    ]")
            code.append("")
            code.append("    preprocessor = ColumnTransformer(")
            code.append("        transformers=transformers,")
            code.append("        remainder='passthrough',")
            code.append("        verbose_feature_names_out=False,")
            code.append("    )")
            code.append("")
            code.append("    pipeline = Pipeline([")
            code.append("        ('preprocessor', preprocessor),")
            code.append("    ])")
            code.append("")
            code.append("    return pipeline")

        code.append("")
        code.append("")
        code.append("def get_pre_pipeline_steps():")
        code.append('    """')
        code.append("    Return operations that must be done before the pipeline.")
        code.append("    These cannot be expressed as sklearn transformers.")
        code.append('    """')
        code.append("    steps = []")

        pre_pipeline = [s for s in self.suggestions if s.parameters.get("pre_pipeline")]
        for s in pre_pipeline:
            if s.fix_type == FixType.DROP_DUPLICATES:
                code.append("    steps.append(('drop_duplicates', lambda df: df.drop_duplicates()))")
            elif s.fix_type == FixType.CLIP_OUTLIERS:
                cols = s.columns
                code.append(f"    # Outlier clipping for {cols}")
                code.append(f"    steps.append(('clip_outliers_{cols[0]}', None))  # Implement manually")

        code.append("    return steps")
        code.append("")
        code.append("")
        code.append("if __name__ == '__main__':")
        code.append("    import joblib")
        code.append("")
        code.append("    pipeline = build_preprocessing_pipeline()")
        code.append("    if pipeline:")
        code.append("        print('Pipeline created successfully')")
        code.append("        print(pipeline)")
        code.append("        # Example: Save pipeline")
        code.append("        # joblib.dump(pipeline, 'preprocessing_pipeline.joblib')")

        return "\n".join(code)

    def _collect_all_imports(self) -> list[str]:
        """Collect all required imports for the pipeline."""
        imports: set[str] = {
            "from sklearn.pipeline import Pipeline",
            "from sklearn.compose import ColumnTransformer",
            "import numpy as np",
        }

        for suggestion in self.suggestions:
            if suggestion.parameters.get("pre_pipeline"):
                continue
            strategy = self.STRATEGY_MAP.get(suggestion.fix_type)
            if strategy:
                imports.update(strategy.get_sklearn_imports())

        return sorted(imports)

    def _build_transformer_list(self) -> list[tuple[str, str, list[str]]]:
        """Build list of (name, transformer_code, columns) tuples."""
        transformers: list[tuple[str, str, list[str]]] = []
        seen_names: set[str] = set()

        for suggestion in self.suggestions:
            if suggestion.parameters.get("pre_pipeline"):
                continue

            strategy = self.STRATEGY_MAP.get(suggestion.fix_type)
            if not strategy:
                continue

            transformer_code, columns = strategy.get_sklearn_transformer(suggestion)
            if transformer_code is None:
                continue

            base_name = f"{suggestion.fix_type.value}"
            if suggestion.columns:
                base_name = f"{suggestion.fix_type.value}_{suggestion.columns[0][:10]}"

            name = base_name
            counter = 1
            while name in seen_names:
                name = f"{base_name}_{counter}"
                counter += 1
            seen_names.add(name)

            transformers.append((name, transformer_code, columns))

        return transformers

    def build_pipeline_object(self) -> Any | None:
        """
        Return an actual sklearn Pipeline object.
        Can be serialized with joblib.
        """
        try:
            from sklearn.compose import ColumnTransformer
            from sklearn.pipeline import Pipeline
        except ImportError:
            return None

        transformers = []
        seen_names: set[str] = set()

        for suggestion in self.suggestions:
            if suggestion.parameters.get("pre_pipeline"):
                continue

            transformer = self._get_transformer_instance(suggestion)
            if transformer is None:
                continue

            columns = suggestion.columns
            base_name = f"{suggestion.fix_type.value}"
            if columns:
                base_name = f"{suggestion.fix_type.value}_{columns[0][:10]}"

            name = base_name
            counter = 1
            while name in seen_names:
                name = f"{base_name}_{counter}"
                counter += 1
            seen_names.add(name)

            transformers.append((name, transformer, columns))

        if not transformers:
            return None

        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="passthrough",
            verbose_feature_names_out=False,
        )

        return Pipeline([("preprocessor", preprocessor)])

    def _get_transformer_instance(self, suggestion: FixSuggestion) -> Any | None:
        """Return actual transformer instance for a suggestion."""
        try:
            from sklearn.impute import KNNImputer, SimpleImputer
            from sklearn.preprocessing import (
                FunctionTransformer,
                MaxAbsScaler,
                MinMaxScaler,
                OneHotEncoder,
                OrdinalEncoder,
                PowerTransformer,
                RobustScaler,
                StandardScaler,
            )
        except ImportError:
            return None

        import numpy as np

        fix_type = suggestion.fix_type
        method = suggestion.method

        if fix_type == FixType.DROP_COLUMN:
            return "drop"

        if fix_type == FixType.IMPUTE:
            if method == "knn":
                n = suggestion.parameters.get("n_neighbors", 5)
                return KNNImputer(n_neighbors=n)
            strategy_map = {
                "mean": "mean",
                "median": "median",
                "most_frequent": "most_frequent",
                "constant": "constant",
            }
            strategy = strategy_map.get(method or "median", "median")
            if method == "constant":
                fill_value = suggestion.parameters.get("fill_value", 0)
                return SimpleImputer(strategy="constant", fill_value=fill_value)
            return SimpleImputer(strategy=strategy)

        if fix_type == FixType.SCALE:
            scaler_map = {
                "standard": StandardScaler(),
                "minmax": MinMaxScaler(),
                "robust": RobustScaler(),
                "maxabs": MaxAbsScaler(),
            }
            return scaler_map.get(method or "standard", StandardScaler())

        if fix_type == FixType.ENCODE:
            if method == "onehot":
                return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
            if method in ("ordinal", "label"):
                return OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
            return None

        if fix_type == FixType.TRANSFORM:
            if method == "boxcox":
                return PowerTransformer(method="box-cox")
            if method == "yeojohnson":
                return PowerTransformer(method="yeo-johnson")
            if method == "log1p":
                return FunctionTransformer(np.log1p, validate=True)
            if method == "sqrt":
                return FunctionTransformer(lambda x: np.sqrt(np.clip(x, 0, None)), validate=True)

        return None
