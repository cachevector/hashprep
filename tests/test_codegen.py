"""Tests for code generation module."""

from hashprep.preparers.codegen import CodeGenerator
from hashprep.preparers.models import (
    EncodeMethod,
    FixSuggestion,
    FixType,
    ImputeMethod,
    ScaleMethod,
    TransformMethod,
)


class TestCodeGenerator:
    def test_generate_drop_column_code(self):
        suggestion = FixSuggestion(
            fix_type=FixType.DROP_COLUMN,
            columns=["empty_col"],
            reason="Empty column",
        )
        gen = CodeGenerator([suggestion])
        code = gen.generate_pandas_script()

        assert "def apply_fixes(df)" in code
        assert "drop(columns=" in code
        assert "empty_col" in code
        assert "import pandas as pd" in code

    def test_generate_imputation_code(self):
        suggestion = FixSuggestion(
            fix_type=FixType.IMPUTE,
            columns=["age"],
            method=ImputeMethod.MEDIAN.value,
            reason="Impute missing values",
        )
        gen = CodeGenerator([suggestion])
        code = gen.generate_pandas_script()

        assert "def apply_fixes(df)" in code
        assert "fillna" in code or "median" in code
        assert "age" in code

    def test_generate_encoding_code(self):
        suggestion = FixSuggestion(
            fix_type=FixType.ENCODE,
            columns=["category"],
            method=EncodeMethod.ONEHOT.value,
            reason="Encode categorical column",
        )
        gen = CodeGenerator([suggestion])
        code = gen.generate_pandas_script()

        assert "get_dummies" in code
        assert "category" in code

    def test_generate_scaling_code(self):
        suggestion = FixSuggestion(
            fix_type=FixType.SCALE,
            columns=["price"],
            method=ScaleMethod.STANDARD.value,
            reason="Scale numeric column",
        )
        gen = CodeGenerator([suggestion])
        code = gen.generate_pandas_script()

        assert "mean()" in code
        assert "std()" in code
        assert "price" in code

    def test_generate_transform_code(self):
        suggestion = FixSuggestion(
            fix_type=FixType.TRANSFORM,
            columns=["revenue"],
            method=TransformMethod.LOG1P.value,
            reason="Transform skewed column",
        )
        gen = CodeGenerator([suggestion])
        code = gen.generate_pandas_script()

        assert "log1p" in code
        assert "revenue" in code

    def test_generate_outlier_clipping_code(self):
        suggestion = FixSuggestion(
            fix_type=FixType.CLIP_OUTLIERS,
            columns=["value"],
            parameters={"clip_method": "iqr"},
            reason="Clip outliers",
        )
        gen = CodeGenerator([suggestion])
        code = gen.generate_pandas_script()

        assert "quantile" in code
        assert "clip" in code
        assert "value" in code

    def test_generated_code_is_valid_python(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.DROP_COLUMN,
                columns=["empty_col"],
                reason="Empty",
            ),
            FixSuggestion(
                fix_type=FixType.IMPUTE,
                columns=["age"],
                method=ImputeMethod.MEAN.value,
                reason="Missing",
            ),
        ]
        gen = CodeGenerator(suggestions)
        code = gen.generate_pandas_script()

        compile(code, "<string>", "exec")

    def test_multiple_suggestions(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.DROP_COLUMN,
                columns=["col1"],
                reason="Drop col1",
            ),
            FixSuggestion(
                fix_type=FixType.IMPUTE,
                columns=["col2"],
                method=ImputeMethod.MEDIAN.value,
                reason="Impute col2",
            ),
            FixSuggestion(
                fix_type=FixType.SCALE,
                columns=["col3"],
                method=ScaleMethod.MINMAX.value,
                reason="Scale col3",
            ),
        ]
        gen = CodeGenerator(suggestions)
        code = gen.generate_pandas_script()

        assert "col1" in code
        assert "col2" in code
        assert "col3" in code
        assert code.count("# ") >= 3

    def test_empty_suggestions(self):
        gen = CodeGenerator([])
        code = gen.generate_pandas_script()

        assert "def apply_fixes(df)" in code
        assert "return df" in code
