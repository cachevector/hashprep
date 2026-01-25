"""Tests for pipeline builder module."""

import numpy as np
import pandas as pd
import pytest

from hashprep.preparers.models import (
    FixSuggestion,
    FixType,
    ImputeMethod,
    ScaleMethod,
)
from hashprep.preparers.pipeline_builder import PipelineBuilder


class TestPipelineBuilder:
    def test_generate_pipeline_code(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.IMPUTE,
                columns=["age"],
                method=ImputeMethod.MEAN.value,
                reason="Impute missing",
            ),
            FixSuggestion(
                fix_type=FixType.SCALE,
                columns=["fare"],
                method=ScaleMethod.STANDARD.value,
                reason="Scale",
            ),
        ]
        builder = PipelineBuilder(suggestions)
        code = builder.generate_pipeline_code()

        assert "def build_preprocessing_pipeline()" in code
        assert "ColumnTransformer" in code
        assert "Pipeline" in code
        assert "SimpleImputer" in code
        assert "StandardScaler" in code

    def test_generated_pipeline_code_is_valid_python(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.IMPUTE,
                columns=["col1"],
                method=ImputeMethod.MEDIAN.value,
                reason="Test",
            ),
        ]
        builder = PipelineBuilder(suggestions)
        code = builder.generate_pipeline_code()

        compile(code, "<string>", "exec")

    def test_empty_suggestions_returns_none_pipeline(self):
        builder = PipelineBuilder([])
        code = builder.generate_pipeline_code()

        assert "No transformations needed" in code
        assert "return None" in code

    def test_pre_pipeline_steps_for_duplicates(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.DROP_DUPLICATES,
                columns=["__dataset__"],
                reason="Remove duplicates",
            ),
        ]
        builder = PipelineBuilder(suggestions)
        code = builder.generate_pipeline_code()

        assert "get_pre_pipeline_steps" in code

    def test_drop_column_transformer(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.DROP_COLUMN,
                columns=["bad_col"],
                reason="Drop column",
            ),
        ]
        builder = PipelineBuilder(suggestions)
        code = builder.generate_pipeline_code()

        assert "'drop'" in code
        assert "bad_col" in code


@pytest.mark.skipif(
    not pytest.importorskip("sklearn", reason="sklearn not installed"),
    reason="sklearn not installed",
)
class TestPipelineBuilderIntegration:
    def test_build_pipeline_object(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.IMPUTE,
                columns=["age"],
                method=ImputeMethod.MEAN.value,
                reason="Missing",
            ),
            FixSuggestion(
                fix_type=FixType.SCALE,
                columns=["fare"],
                method=ScaleMethod.STANDARD.value,
                reason="Scale",
            ),
        ]
        builder = PipelineBuilder(suggestions)
        pipeline = builder.build_pipeline_object()

        df = pd.DataFrame(
            {
                "age": [25, np.nan, 35, 40],
                "fare": [100, 200, 150, 300],
            }
        )

        result = pipeline.fit_transform(df)
        assert result.shape[0] == 4
        assert not np.any(np.isnan(result))

    def test_pipeline_with_drop(self):
        suggestions = [
            FixSuggestion(
                fix_type=FixType.DROP_COLUMN,
                columns=["bad_col"],
                reason="Drop",
            ),
        ]
        builder = PipelineBuilder(suggestions)
        pipeline = builder.build_pipeline_object()

        df = pd.DataFrame(
            {
                "good_col": [1, 2, 3],
                "bad_col": [4, 5, 6],
            }
        )

        result = pipeline.fit_transform(df)
        assert result.shape[1] == 1
