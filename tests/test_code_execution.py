import numpy as np
import pandas as pd
import pytest

from hashprep.preparers.codegen import CodeGenerator
from hashprep.preparers.models import (
    EncodeMethod,
    FixSuggestion,
    FixType,
    ImputeMethod,
    ScaleMethod,
)
from hashprep.preparers.pipeline_builder import PipelineBuilder


def test_execute_pandas_fixes():
    suggestions = [
        FixSuggestion(
            fix_type=FixType.DROP_COLUMN,
            columns=["col_to_drop"],
            reason="Empty",
        ),
        FixSuggestion(
            fix_type=FixType.IMPUTE,
            columns=["col_to_impute"],
            method=ImputeMethod.MEAN.value,
            reason="Missing",
        ),
        FixSuggestion(
            fix_type=FixType.ENCODE,
            columns=["col_to_encode"],
            method=EncodeMethod.ONEHOT.value,
            reason="Categorical",
        ),
    ]

    df = pd.DataFrame(
        {
            "col_to_drop": [np.nan, np.nan, np.nan],
            "col_to_impute": [1.0, np.nan, 3.0],
            "col_to_encode": ["A", "B", "A"],
            "other_col": [10, 20, 30],
        }
    )

    gen = CodeGenerator(suggestions)
    code = gen.generate_pandas_script()

    # Define a namespace to execute the code
    namespace = {}
    exec(code, namespace)

    # Call apply_fixes
    apply_fixes = namespace["apply_fixes"]
    result_df = apply_fixes(df.copy())

    assert "col_to_drop" not in result_df.columns
    assert result_df["col_to_impute"].isnull().sum() == 0
    assert result_df["col_to_impute"].iloc[1] == 2.0  # Mean of 1.0 and 3.0
    # One-hot encoding should create new columns
    assert any("col_to_encode" in col for col in result_df.columns)


@pytest.mark.skipif(
    not pytest.importorskip("sklearn", reason="sklearn not installed"),
    reason="sklearn not installed",
)
def test_execute_sklearn_pipeline():
    suggestions = [
        FixSuggestion(
            fix_type=FixType.IMPUTE,
            columns=["col_to_impute"],
            method=ImputeMethod.MEDIAN.value,
            reason="Missing",
        ),
        FixSuggestion(
            fix_type=FixType.SCALE,
            columns=["col_to_scale"],
            method=ScaleMethod.STANDARD.value,
            reason="Scale",
        ),
    ]

    df = pd.DataFrame(
        {
            "col_to_impute": [10.0, np.nan, 30.0],
            "col_to_scale": [1.0, 2.0, 3.0],
        }
    )

    builder = PipelineBuilder(suggestions)
    code = builder.generate_pipeline_code()

    namespace = {}
    exec(code, namespace)

    build_pipeline = namespace["build_preprocessing_pipeline"]
    pipeline = build_pipeline()

    result = pipeline.fit_transform(df)

    assert result.shape == (3, 2)
    assert not np.any(np.isnan(result))
    # Check scaling (mean should be approx 0)
    assert np.abs(np.mean(result[:, 1])) < 1e-7
