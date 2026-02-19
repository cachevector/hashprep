"""Tests for drift detection module."""

import numpy as np
import pandas as pd

from hashprep.checks.drift import check_drift


class TestNumericDrift:
    def test_no_drift_identical_distributions(self):
        np.random.seed(42)
        train = pd.DataFrame({"col": np.random.normal(0, 1, 1000)})
        test = pd.DataFrame({"col": np.random.normal(0, 1, 1000)})

        issues = check_drift(train, test)

        drift_issues = [i for i in issues if "Drift" in i.description]
        assert len(drift_issues) == 0

    def test_drift_detected_different_distributions(self):
        np.random.seed(42)
        train = pd.DataFrame({"col": np.random.normal(0, 1, 1000)})
        test = pd.DataFrame({"col": np.random.normal(5, 1, 1000)})

        issues = check_drift(train, test)

        drift_issues = [i for i in issues if "Drift" in i.description]
        assert len(drift_issues) >= 1
        assert drift_issues[0].category == "dataset_drift"

    def test_critical_severity_for_extreme_drift(self):
        np.random.seed(42)
        train = pd.DataFrame({"col": np.random.normal(0, 1, 1000)})
        test = pd.DataFrame({"col": np.random.normal(100, 1, 1000)})

        issues = check_drift(train, test)

        drift_issues = [i for i in issues if "Drift" in i.description]
        assert len(drift_issues) >= 1
        assert drift_issues[0].severity == "critical"

    def test_handles_missing_columns_gracefully(self):
        train = pd.DataFrame({"col_a": [1, 2, 3], "col_b": [4, 5, 6]})
        test = pd.DataFrame({"col_a": [1, 2, 3]})

        issues = check_drift(train, test)
        assert isinstance(issues, list)

    def test_handles_empty_columns(self):
        train = pd.DataFrame({"col": [1.0, 2.0, np.nan, np.nan]})
        test = pd.DataFrame({"col": [np.nan, np.nan, np.nan, np.nan]})

        issues = check_drift(train, test)
        assert isinstance(issues, list)


class TestCategoricalDrift:
    def test_no_drift_same_categories(self):
        train = pd.DataFrame({"cat": ["A", "B", "C"] * 100})
        test = pd.DataFrame({"cat": ["A", "B", "C"] * 100})

        issues = check_drift(train, test)

        drift_issues = [i for i in issues if "Drift" in i.description and "cat" in i.column]
        assert len(drift_issues) == 0

    def test_drift_different_category_distribution(self):
        train = pd.DataFrame({"cat": ["A"] * 90 + ["B"] * 10})
        test = pd.DataFrame({"cat": ["A"] * 10 + ["B"] * 90})

        issues = check_drift(train, test)

        drift_issues = [i for i in issues if "Drift" in i.description and "cat" in i.column]
        assert len(drift_issues) >= 1

    def test_new_categories_detected(self):
        train = pd.DataFrame({"cat": ["A", "B"] * 50})
        test = pd.DataFrame({"cat": ["A", "B", "C"] * 33})

        issues = check_drift(train, test)

        new_cat_issues = [i for i in issues if "New categories" in i.description]
        assert len(new_cat_issues) >= 1
        assert "C" in new_cat_issues[0].description

    def test_skips_high_cardinality(self):
        train = pd.DataFrame({"cat": [f"cat_{i}" for i in range(100)]})
        test = pd.DataFrame({"cat": [f"cat_{i}" for i in range(100)]})

        issues = check_drift(train, test)

        chi2_issues = [i for i in issues if "Chi-square" in i.description and i.column == "cat"]
        assert len(chi2_issues) == 0
