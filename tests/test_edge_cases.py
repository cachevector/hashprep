"""Tests for edge cases, failure paths, and boundary conditions."""

import numpy as np
import pandas as pd

from hashprep import DatasetAnalyzer
from hashprep.checks.drift import check_drift


class TestEmptyDataframes:
    """Test behavior with empty or minimal DataFrames."""

    def test_empty_dataframe_analysis(self):
        df = pd.DataFrame()
        analyzer = DatasetAnalyzer(df, selected_checks=["empty_dataset"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_single_row_dataframe(self):
        df = pd.DataFrame({"a": [1], "b": ["x"]})
        analyzer = DatasetAnalyzer(df)
        summary = analyzer.analyze()
        assert summary is not None
        assert "issues" in summary

    def test_single_column_dataframe(self):
        df = pd.DataFrame({"only_col": range(100)})
        analyzer = DatasetAnalyzer(df)
        summary = analyzer.analyze()
        assert summary is not None

    def test_all_nan_dataframe(self):
        df = pd.DataFrame({"a": [np.nan] * 10, "b": [np.nan] * 10})
        analyzer = DatasetAnalyzer(df, selected_checks=["empty_dataset", "high_missing_values"])
        summary = analyzer.analyze()
        assert summary["total_issues"] > 0

    def test_all_nan_numeric_column_outliers(self):
        df = pd.DataFrame({"a": [np.nan] * 10, "b": range(10)})
        analyzer = DatasetAnalyzer(df, selected_checks=["outliers"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_empty_drift_check(self):
        issues = check_drift(pd.DataFrame(), pd.DataFrame())
        assert issues == []

    def test_drift_with_all_nan_columns(self):
        train = pd.DataFrame({"col": [np.nan] * 10})
        test = pd.DataFrame({"col": [np.nan] * 10})
        issues = check_drift(train, test)
        assert isinstance(issues, list)


class TestConstantAndDegenerateColumns:
    """Test with constant, zero-variance, and degenerate data."""

    def test_all_zeros_column(self):
        df = pd.DataFrame({"zeros": [0] * 100, "normal": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["outliers", "high_zero_counts"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_constant_numeric_column_outliers(self):
        df = pd.DataFrame({"const": [42] * 100, "var": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["outliers", "single_value_columns"])
        summary = analyzer.analyze()
        single_val_issues = [i for i in summary["issues"] if i["category"] == "single_value"]
        assert len(single_val_issues) >= 1

    def test_constant_string_column(self):
        df = pd.DataFrame({"const": ["same"] * 100})
        analyzer = DatasetAnalyzer(df, selected_checks=["single_value_columns", "high_cardinality"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_single_category(self):
        df = pd.DataFrame({"cat": ["A"] * 100, "num": range(100)})
        analyzer = DatasetAnalyzer(df, target_col="cat", selected_checks=["class_imbalance"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_infinite_values(self):
        df = pd.DataFrame({"a": [1, 2, np.inf, -np.inf, 5], "b": range(5)})
        analyzer = DatasetAnalyzer(df, selected_checks=["infinite_values"])
        summary = analyzer.analyze()
        inf_issues = [i for i in summary["issues"] if i["category"] == "infinite_values"]
        assert len(inf_issues) >= 1


class TestMixedAndEdgeCaseTypes:
    """Test with mixed types, unusual dtypes, and edge cases."""

    def test_mixed_types_column(self):
        # Use object-typed column with numeric strings mixed with text
        df = pd.DataFrame({"mixed": ["1", "two", "3.0", "four", "5"] * 20})
        analyzer = DatasetAnalyzer(df, selected_checks=["mixed_data_types"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_boolean_column(self):
        df = pd.DataFrame({"flag": [True, False] * 50, "num": range(100)})
        analyzer = DatasetAnalyzer(df)
        summary = analyzer.analyze()
        assert summary is not None

    def test_datetime_column(self):
        dates = pd.date_range("2020-01-01", periods=100, freq="D")
        df = pd.DataFrame({"date": dates, "val": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["datetime_skew"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_very_long_strings(self):
        df = pd.DataFrame({"text": ["x" * 10000] * 10 + ["short"] * 90})
        analyzer = DatasetAnalyzer(df, selected_checks=["extreme_text_lengths"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_empty_strings(self):
        df = pd.DataFrame({"text": [""] * 50 + ["hello"] * 50})
        analyzer = DatasetAnalyzer(df, selected_checks=["extreme_text_lengths"])
        summary = analyzer.analyze()
        assert summary is not None


class TestCorrelationEdgeCases:
    """Test correlation checks with edge case data."""

    def test_single_numeric_column_correlation(self):
        df = pd.DataFrame({"x": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["feature_correlation"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_all_constant_columns_correlation(self):
        df = pd.DataFrame({"a": [1] * 100, "b": [2] * 100})
        analyzer = DatasetAnalyzer(df, selected_checks=["feature_correlation"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_categorical_correlation_single_category(self):
        df = pd.DataFrame({"cat1": ["A"] * 100, "cat2": ["X"] * 100})
        analyzer = DatasetAnalyzer(df, selected_checks=["categorical_correlation"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_mixed_correlation_no_variance(self):
        df = pd.DataFrame({"cat": ["A", "B"] * 50, "num": [42] * 100})
        analyzer = DatasetAnalyzer(df, selected_checks=["mixed_correlation"])
        summary = analyzer.analyze()
        assert summary is not None


class TestLeakageEdgeCases:
    """Test leakage checks with edge case data."""

    def test_leakage_target_identical_column(self):
        df = pd.DataFrame({"target": [0, 1] * 50, "clone": [0, 1] * 50})
        analyzer = DatasetAnalyzer(df, target_col="target", selected_checks=["data_leakage"])
        summary = analyzer.analyze()
        leakage = [i for i in summary["issues"] if i["category"] == "data_leakage"]
        assert len(leakage) >= 1

    def test_leakage_no_target(self):
        df = pd.DataFrame({"a": range(100), "b": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["data_leakage"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_target_leakage_constant_feature(self):
        df = pd.DataFrame(
            {
                "target": [0, 1] * 50,
                "const": [42] * 100,
            }
        )
        analyzer = DatasetAnalyzer(
            df,
            target_col="target",
            selected_checks=["target_leakage_patterns"],
        )
        summary = analyzer.analyze()
        assert summary is not None

    def test_categorical_target_leakage(self):
        df = pd.DataFrame(
            {
                "target": ["yes", "no"] * 50,
                "predictor": ["y", "n"] * 50,
                "num": range(100),
            }
        )
        analyzer = DatasetAnalyzer(
            df,
            target_col="target",
            selected_checks=["target_leakage_patterns"],
        )
        summary = analyzer.analyze()
        assert summary is not None


class TestSelectedChecksFiltering:
    """Test that selected_checks properly filters checks."""

    def test_unknown_checks_ignored(self):
        df = pd.DataFrame({"a": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["nonexistent_check", "also_fake"])
        summary = analyzer.analyze()
        assert summary["total_issues"] == 0

    def test_empty_selected_checks(self):
        df = pd.DataFrame({"a": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=[])
        summary = analyzer.analyze()
        assert summary["total_issues"] == 0

    def test_single_check_selected(self):
        df = pd.DataFrame({"a": [0] * 95 + [999] * 5})
        analyzer = DatasetAnalyzer(df, selected_checks=["outliers"])
        summary = analyzer.analyze()
        for issue in summary["issues"]:
            assert issue["category"] == "outliers"


class TestDistributionEdgeCases:
    """Test distribution checks with edge case data."""

    def test_uniform_with_few_samples(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        analyzer = DatasetAnalyzer(df, selected_checks=["uniform_distribution"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_unique_values_few_rows(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        analyzer = DatasetAnalyzer(df, selected_checks=["unique_values"])
        summary = analyzer.analyze()
        assert summary is not None

    def test_skewness_constant_column(self):
        df = pd.DataFrame({"a": [5] * 100})
        analyzer = DatasetAnalyzer(df, selected_checks=["skewness"])
        summary = analyzer.analyze()
        assert summary is not None


class TestMissingPatternsEdgeCases:
    """Test missing value checks with edge case data."""

    def test_no_missing_values(self):
        df = pd.DataFrame({"a": range(100), "b": range(100)})
        analyzer = DatasetAnalyzer(
            df, selected_checks=["high_missing_values", "dataset_missingness", "missing_patterns"]
        )
        summary = analyzer.analyze()
        missing_issues = [i for i in summary["issues"] if "missing" in i["category"].lower()]
        assert len(missing_issues) == 0

    def test_completely_missing_column(self):
        df = pd.DataFrame({"empty": [None] * 100, "full": range(100)})
        analyzer = DatasetAnalyzer(df, selected_checks=["high_missing_values", "empty_columns"])
        summary = analyzer.analyze()
        assert summary["total_issues"] > 0


class TestDriftEdgeCases:
    """Test drift detection edge cases beyond basic validation."""

    def test_drift_disjoint_columns(self):
        train = pd.DataFrame({"a": [1, 2, 3]})
        test = pd.DataFrame({"b": [4, 5, 6]})
        issues = check_drift(train, test)
        assert issues == []

    def test_drift_single_value_columns(self):
        train = pd.DataFrame({"x": [1.0] * 100})
        test = pd.DataFrame({"x": [1.0] * 100})
        issues = check_drift(train, test)
        assert isinstance(issues, list)

    def test_drift_mixed_column_types(self):
        train = pd.DataFrame({"num": [1, 2, 3] * 100, "cat": ["a", "b", "c"] * 100})
        test = pd.DataFrame({"num": [10, 20, 30] * 100, "cat": ["a", "a", "a"] * 100})
        issues = check_drift(train, test)
        assert len(issues) > 0

    def test_drift_many_categories_skipped(self):
        """Chi-square should be skipped for high-cardinality categoricals."""
        train = pd.DataFrame({"cat": [f"v{i}" for i in range(200)]})
        test = pd.DataFrame({"cat": [f"v{i}" for i in range(200)]})
        issues = check_drift(train, test)
        chi2 = [i for i in issues if "Chi-square" in i.description]
        assert len(chi2) == 0
