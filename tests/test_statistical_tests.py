"""Tests for statistical checks: normality and variance homogeneity."""

import numpy as np
import pandas as pd
import pytest

from hashprep import DatasetAnalyzer
from hashprep.checks.statistical_tests import _check_normality, _check_variance_homogeneity
from hashprep.summaries.variables import _summarize_numeric

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeAnalyzer:
    def __init__(self, df, target_col=None):
        self.df = df
        self.target_col = target_col
        from hashprep.utils.type_inference import infer_types

        self.column_types = infer_types(df)


rng = np.random.default_rng(42)


# ---------------------------------------------------------------------------
# Normality check
# ---------------------------------------------------------------------------


class TestNormalityCheck:
    def test_normal_data_no_issue(self):
        df = pd.DataFrame({"x": rng.standard_normal(200)})
        issues = _check_normality(_FakeAnalyzer(df))
        # Normal data should not trigger a flag
        assert all(i.column != "x" for i in issues) or len(issues) == 0

    def test_heavily_skewed_data_flagged(self):
        # Exponential distribution is very non-normal
        df = pd.DataFrame({"x": rng.exponential(scale=1.0, size=300)})
        issues = _check_normality(_FakeAnalyzer(df))
        assert any(i.category == "normality" and i.column == "x" for i in issues)

    def test_uniform_data_flagged(self):
        df = pd.DataFrame({"x": rng.uniform(0, 1, size=200)})
        issues = _check_normality(_FakeAnalyzer(df))
        assert any(i.category == "normality" for i in issues)

    def test_too_few_rows_skipped(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        issues = _check_normality(_FakeAnalyzer(df))
        assert issues == []

    def test_constant_column_skipped(self):
        df = pd.DataFrame({"x": [5.0] * 50})
        issues = _check_normality(_FakeAnalyzer(df))
        assert issues == []

    def test_all_nan_column_skipped(self):
        df = pd.DataFrame({"x": [np.nan] * 50, "y": rng.standard_normal(50)})
        categories = [i.column for i in _check_normality(_FakeAnalyzer(df))]
        assert "x" not in categories

    def test_large_normal_data_uses_dagostino(self):
        # n > 5000 → should switch to D'Agostino-Pearson
        df = pd.DataFrame({"big": rng.standard_normal(6000)})
        issues = _check_normality(_FakeAnalyzer(df))
        # Large normal data should not be flagged
        assert all(i.column != "big" for i in issues)

    def test_large_non_normal_data_flagged(self):
        df = pd.DataFrame({"big": rng.exponential(scale=1.0, size=6000)})
        issues = _check_normality(_FakeAnalyzer(df))
        assert any(i.category == "normality" and i.column == "big" for i in issues)

    def test_issue_fields_populated(self):
        df = pd.DataFrame({"x": rng.exponential(1.0, size=200)})
        issues = _check_normality(_FakeAnalyzer(df))
        issue = next(i for i in issues if i.column == "x")
        assert issue.category == "normality"
        assert issue.severity in ("warning", "critical")
        assert "stat=" in issue.description
        assert "p=" in issue.description

    def test_new_checks_in_all_checks(self):
        assert "normality" in DatasetAnalyzer.ALL_CHECKS
        assert "variance_homogeneity" in DatasetAnalyzer.ALL_CHECKS


# ---------------------------------------------------------------------------
# Variance homogeneity check (Levene's)
# ---------------------------------------------------------------------------


class TestVarianceHomogeneityCheck:
    def test_no_target_col_returns_empty(self):
        df = pd.DataFrame({"x": rng.standard_normal(100), "y": rng.standard_normal(100)})
        issues = _check_variance_homogeneity(_FakeAnalyzer(df, target_col=None))
        assert issues == []

    def test_equal_variance_across_groups_no_issue(self):
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 100), rng.normal(5, 1, 100)]),
                "target": ["A"] * 100 + ["B"] * 100,
            }
        )
        issues = _check_variance_homogeneity(_FakeAnalyzer(df, target_col="target"))
        assert all(i.category != "variance_homogeneity" for i in issues)

    def test_unequal_variance_flagged(self):
        # Group A: std=1, Group B: std=20 → Levene should fire
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 100), rng.normal(0, 20, 100)]),
                "target": ["A"] * 100 + ["B"] * 100,
            }
        )
        issues = _check_variance_homogeneity(_FakeAnalyzer(df, target_col="target"))
        assert any(i.category == "variance_homogeneity" and i.column == "x" for i in issues)

    def test_issue_contains_levene_info(self):
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 100), rng.normal(0, 15, 100)]),
                "target": ["A"] * 100 + ["B"] * 100,
            }
        )
        issues = _check_variance_homogeneity(_FakeAnalyzer(df, target_col="target"))
        issue = next(i for i in issues if i.category == "variance_homogeneity")
        assert "Levene" in issue.description
        assert "stat=" in issue.description
        assert "p=" in issue.description
        assert "std ratio" in issue.description

    def test_target_col_excluded_from_check(self):
        df = pd.DataFrame(
            {
                "target": [0] * 100 + [1] * 100,
                "x": rng.standard_normal(200),
            }
        )
        issues = _check_variance_homogeneity(_FakeAnalyzer(df, target_col="target"))
        assert all(i.column != "target" for i in issues)

    def test_too_few_per_group_skipped(self):
        # Only 3 samples per group — below min_group_size (8)
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0], "target": ["A", "A", "A", "B", "B", "B"]})
        issues = _check_variance_homogeneity(_FakeAnalyzer(df, target_col="target"))
        assert issues == []

    def test_only_one_valid_group_skipped(self):
        # Group B has < min_group_size samples
        x = np.concatenate([rng.normal(0, 1, 100), rng.normal(0, 5, 3)])
        target = ["A"] * 100 + ["B"] * 3
        df = pd.DataFrame({"x": x, "target": target})
        issues = _check_variance_homogeneity(_FakeAnalyzer(df, target_col="target"))
        assert issues == []


# ---------------------------------------------------------------------------
# Normality in numeric summaries
# ---------------------------------------------------------------------------


class TestNormalitySummary:
    def test_normality_key_present(self):
        series = rng.standard_normal(100)
        df = pd.DataFrame({"x": series})
        result = _summarize_numeric(df, "x")
        assert "normality" in result

    def test_normality_fields(self):
        df = pd.DataFrame({"x": rng.standard_normal(100)})
        norm = _summarize_numeric(df, "x")["normality"]
        assert norm is not None
        assert "test" in norm
        assert "statistic" in norm
        assert "p_value" in norm
        assert "is_normal" in norm
        assert isinstance(norm["is_normal"], bool)
        assert norm["test"] == "shapiro_wilk"  # n=100 < 5000

    def test_large_sample_uses_dagostino(self):
        df = pd.DataFrame({"x": rng.standard_normal(6000)})
        norm = _summarize_numeric(df, "x")["normality"]
        assert norm["test"] == "dagostino_pearson"

    def test_normality_none_for_too_few_rows(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        result = _summarize_numeric(df, "x")
        assert result["normality"] is None

    def test_normality_none_for_constant_col(self):
        df = pd.DataFrame({"x": [5.0] * 50})
        result = _summarize_numeric(df, "x")
        assert result["normality"] is None

    def test_non_normal_data_is_normal_false(self):
        # Very heavy exponential tail — p should be well below 0.05
        df = pd.DataFrame({"x": rng.exponential(1.0, size=500)})
        norm = _summarize_numeric(df, "x")["normality"]
        assert norm["is_normal"] is False

    def test_normality_handles_inf_values(self):
        # Infinite values should be excluded before the test
        values = list(rng.standard_normal(100)) + [np.inf, -np.inf]
        df = pd.DataFrame({"x": values})
        result = _summarize_numeric(df, "x")
        # Should not raise; normality may be None or a valid result
        assert "normality" in result


# ---------------------------------------------------------------------------
# Integration: DatasetAnalyzer end-to-end
# ---------------------------------------------------------------------------


class TestStatisticalTestsIntegration:
    def test_normality_check_runs_in_full_analysis(self):
        df = pd.DataFrame(
            {
                "normal_col": rng.standard_normal(200),
                "skewed_col": rng.exponential(1.0, size=200),
            }
        )
        analyzer = DatasetAnalyzer(df, selected_checks=["normality"], auto_sample=False)
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "normality" in categories

    def test_variance_homogeneity_runs_with_target(self):
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 100), rng.normal(0, 15, 100)]),
                "target": ["A"] * 100 + ["B"] * 100,
            }
        )
        analyzer = DatasetAnalyzer(df, target_col="target", selected_checks=["variance_homogeneity"], auto_sample=False)
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "variance_homogeneity" in categories

    def test_normality_summary_present_in_full_analysis(self):
        df = pd.DataFrame({"val": rng.standard_normal(100), "cat": ["A", "B"] * 50})
        analyzer = DatasetAnalyzer(df, auto_sample=False)
        summary = analyzer.analyze()
        var = summary["summaries"]["variables"]["val"]
        assert "normality" in var
        assert var["normality"] is not None

    def test_no_crash_without_target(self):
        df = pd.DataFrame({"a": rng.standard_normal(100), "b": rng.exponential(1, 100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["variance_homogeneity"], auto_sample=False)
        summary = analyzer.analyze()
        assert summary["total_issues"] == 0

    @pytest.mark.parametrize("check", ["normality", "variance_homogeneity"])
    def test_check_selectable_via_selected_checks(self, check):
        df = pd.DataFrame(
            {
                "x": rng.exponential(1.0, size=100),
                "target": ["A"] * 50 + ["B"] * 50,
            }
        )
        analyzer = DatasetAnalyzer(df, target_col="target", selected_checks=[check], auto_sample=False)
        summary = analyzer.analyze()
        # Should run without error and return a dict
        assert "issues" in summary
