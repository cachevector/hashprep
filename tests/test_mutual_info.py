"""Tests for mutual information, entropy, and the low_mutual_information check."""

import numpy as np
import pandas as pd
import pytest

from hashprep import DatasetAnalyzer
from hashprep.checks.mutual_info import _check_low_mutual_information
from hashprep.summaries.mutual_info import summarize_mutual_information
from hashprep.summaries.variables import _summarize_categorical, _summarize_numeric
from hashprep.utils.type_inference import infer_types

rng = np.random.default_rng(0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeAnalyzer:
    def __init__(self, df, target_col=None):
        self.df = df
        self.target_col = target_col
        self.column_types = infer_types(df)


# ---------------------------------------------------------------------------
# Shannon entropy in variable summaries
# ---------------------------------------------------------------------------


class TestEntropyInSummaries:
    def test_categorical_has_entropy(self):
        df = pd.DataFrame({"cat": ["A", "B", "C", "D"] * 25})
        result = _summarize_categorical(df, "cat")
        assert "entropy" in result
        assert result["entropy"] is not None

    def test_uniform_categorical_max_entropy(self):
        # 4 equally likely classes → entropy = log2(4) = 2 bits
        df = pd.DataFrame({"cat": ["A", "B", "C", "D"] * 50})
        ent = _summarize_categorical(df, "cat")["entropy"]
        assert abs(ent["entropy_bits"] - 2.0) < 0.01
        assert abs(ent["normalized_entropy"] - 1.0) < 0.01

    def test_constant_categorical_entropy_none(self):
        df = pd.DataFrame({"cat": ["A"] * 50})
        ent = _summarize_categorical(df, "cat")["entropy"]
        assert ent is None

    def test_skewed_categorical_lower_entropy(self):
        # 90% A, 10% B → lower entropy than uniform
        df = pd.DataFrame({"cat": ["A"] * 90 + ["B"] * 10})
        ent_skewed = _summarize_categorical(df, "cat")["entropy"]["entropy_bits"]
        df_uniform = pd.DataFrame({"cat": ["A"] * 50 + ["B"] * 50})
        ent_uniform = _summarize_categorical(df_uniform, "cat")["entropy"]["entropy_bits"]
        assert ent_skewed < ent_uniform

    def test_numeric_has_entropy(self):
        df = pd.DataFrame({"x": rng.standard_normal(200)})
        result = _summarize_numeric(df, "x")
        assert "entropy" in result
        assert result["entropy"] is not None

    def test_numeric_entropy_fields(self):
        df = pd.DataFrame({"x": rng.uniform(0, 1, 200)})
        ent = _summarize_numeric(df, "x")["entropy"]
        assert "entropy_bits" in ent
        assert "normalized_entropy" in ent
        assert 0.0 <= ent["normalized_entropy"] <= 1.0

    def test_numeric_constant_entropy_none(self):
        df = pd.DataFrame({"x": [5.0] * 50})
        result = _summarize_numeric(df, "x")
        # constant column: normality is None; entropy is also None (only 1 bin)
        assert result["entropy"] is None


# ---------------------------------------------------------------------------
# summarize_mutual_information
# ---------------------------------------------------------------------------


class TestSummarizeMutualInformation:
    def _classification_df(self, n=200):
        x_signal = rng.standard_normal(n)
        x_noise = rng.standard_normal(n)
        y = (x_signal > 0).astype(int)
        return pd.DataFrame({"signal": x_signal, "noise": x_noise, "target": y})

    def _regression_df(self, n=200):
        x_signal = rng.standard_normal(n)
        x_noise = rng.standard_normal(n)
        y = x_signal * 3 + rng.standard_normal(n) * 0.1
        return pd.DataFrame({"signal": x_signal, "noise": x_noise, "target": y})

    def test_returns_dict_with_scores(self):
        df = self._classification_df()
        types = infer_types(df)
        result = summarize_mutual_information(df, "target", types)
        assert "scores" in result
        assert "signal" in result["scores"]
        assert "noise" in result["scores"]

    def test_classification_task_detected(self):
        df = self._classification_df()
        types = infer_types(df)
        result = summarize_mutual_information(df, "target", types)
        assert result["task"] == "classification"

    def test_regression_task_detected(self):
        df = self._regression_df()
        types = infer_types(df)
        result = summarize_mutual_information(df, "target", types)
        assert result["task"] == "regression"

    def test_signal_higher_mi_than_noise(self):
        df = self._classification_df()
        types = infer_types(df)
        scores = summarize_mutual_information(df, "target", types)["scores"]
        assert scores["signal"] > scores["noise"]

    def test_scores_sorted_descending(self):
        df = self._classification_df()
        types = infer_types(df)
        scores = summarize_mutual_information(df, "target", types)["scores"]
        vals = list(scores.values())
        assert vals == sorted(vals, reverse=True)

    def test_scores_non_negative(self):
        df = self._classification_df()
        types = infer_types(df)
        scores = summarize_mutual_information(df, "target", types)["scores"]
        assert all(v >= 0 for v in scores.values())

    def test_missing_target_col_returns_empty(self):
        df = pd.DataFrame({"x": rng.standard_normal(100)})
        types = infer_types(df)
        assert summarize_mutual_information(df, "nonexistent", types) == {}

    def test_too_few_samples_returns_empty(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0], "target": [0, 1, 0]})
        types = infer_types(df)
        assert summarize_mutual_information(df, "target", types) == {}

    def test_categorical_features_included(self):
        df = pd.DataFrame(
            {
                "cat": ["A", "B"] * 100,
                "num": rng.standard_normal(200),
                "target": rng.integers(0, 2, 200),
            }
        )
        types = infer_types(df)
        result = summarize_mutual_information(df, "target", types)
        assert "cat" in result.get("scores", {})

    def test_high_cardinality_cat_excluded(self):
        # 300 unique categories → should be excluded from MI
        df = pd.DataFrame(
            {
                "high_card": [f"cat_{i}" for i in range(300)],
                "num": rng.standard_normal(300),
                "target": rng.integers(0, 2, 300),
            }
        )
        types = infer_types(df)
        result = summarize_mutual_information(df, "target", types)
        assert "high_card" not in result.get("scores", {})


# ---------------------------------------------------------------------------
# low_mutual_information check
# ---------------------------------------------------------------------------


class TestLowMutualInformationCheck:
    def test_no_target_returns_empty(self):
        df = pd.DataFrame({"x": rng.standard_normal(100)})
        issues = _check_low_mutual_information(_FakeAnalyzer(df, target_col=None))
        assert issues == []

    def test_noise_feature_flagged(self):
        # Independent seed + n=2000 so the KNN estimator reliably gives noise ≈ 0
        _rng = np.random.default_rng(123)
        n = 2000
        x_signal = _rng.standard_normal(n)
        noise = _rng.standard_normal(n)
        target = (x_signal > 0).astype(int)
        df = pd.DataFrame({"signal": x_signal, "noise": noise, "target": target})
        issues = _check_low_mutual_information(_FakeAnalyzer(df, target_col="target"))
        flagged = [i.column for i in issues]
        assert "noise" in flagged

    def test_strong_signal_not_flagged(self):
        x = rng.standard_normal(300)
        target = (x > 0).astype(int)
        df = pd.DataFrame({"signal": x, "target": target})
        issues = _check_low_mutual_information(_FakeAnalyzer(df, target_col="target"))
        flagged = [i.column for i in issues]
        assert "signal" not in flagged

    def test_issue_fields_correct(self):
        noise = rng.standard_normal(300)
        target = rng.integers(0, 2, 300)
        df = pd.DataFrame({"noise": noise, "target": target})
        issues = _check_low_mutual_information(_FakeAnalyzer(df, target_col="target"))
        if issues:
            issue = issues[0]
            assert issue.category == "low_mutual_information"
            assert issue.severity == "warning"
            assert "MI=" in issue.description

    def test_target_col_not_flagged_against_itself(self):
        df = pd.DataFrame({"x": rng.standard_normal(100), "target": rng.integers(0, 2, 100)})
        issues = _check_low_mutual_information(_FakeAnalyzer(df, target_col="target"))
        assert all(i.column != "target" for i in issues)


# ---------------------------------------------------------------------------
# Integration: DatasetAnalyzer end-to-end
# ---------------------------------------------------------------------------


class TestMutualInfoIntegration:
    def test_mi_summary_present_when_target_set(self):
        x = rng.standard_normal(200)
        df = pd.DataFrame({"x": x, "target": (x > 0).astype(int)})
        analyzer = DatasetAnalyzer(df, target_col="target", auto_sample=False)
        summary = analyzer.analyze()
        assert "mutual_information" in summary["summaries"]
        mi = summary["summaries"]["mutual_information"]
        assert "scores" in mi
        assert "x" in mi["scores"]

    def test_mi_summary_absent_when_no_target(self):
        df = pd.DataFrame({"x": rng.standard_normal(100)})
        analyzer = DatasetAnalyzer(df, auto_sample=False)
        summary = analyzer.analyze()
        assert "mutual_information" not in summary["summaries"]

    def test_low_mi_check_runs_in_full_analysis(self):
        # Independent seed so this test is not sensitive to rng state from prior tests
        _rng = np.random.default_rng(999)
        n = 2000
        signal = _rng.standard_normal(n)
        noise = _rng.standard_normal(n)
        target = (signal > 0).astype(int)
        df = pd.DataFrame({"signal": signal, "noise": noise, "target": target})
        analyzer = DatasetAnalyzer(
            df, target_col="target", selected_checks=["low_mutual_information"], auto_sample=False
        )
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "low_mutual_information" in categories

    def test_entropy_in_variable_summary(self):
        df = pd.DataFrame({"cat": ["A", "B", "C"] * 50, "num": rng.standard_normal(150)})
        analyzer = DatasetAnalyzer(df, auto_sample=False)
        summary = analyzer.analyze()
        cat_var = summary["summaries"]["variables"]["cat"]
        num_var = summary["summaries"]["variables"]["num"]
        assert "entropy" in cat_var
        assert "entropy" in num_var

    def test_low_mi_in_all_checks(self):
        assert "low_mutual_information" in DatasetAnalyzer.ALL_CHECKS

    @pytest.mark.parametrize("check", ["low_mutual_information"])
    def test_check_selectable(self, check):
        df = pd.DataFrame({"x": rng.standard_normal(100), "target": rng.integers(0, 2, 100)})
        analyzer = DatasetAnalyzer(df, target_col="target", selected_checks=[check], auto_sample=False)
        summary = analyzer.analyze()
        assert "issues" in summary
