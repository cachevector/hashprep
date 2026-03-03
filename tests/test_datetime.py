"""Tests for DateTime support: type inference, checks, and summaries."""

import numpy as np
import pandas as pd

from hashprep import DatasetAnalyzer
from hashprep.checks.datetime_checks import (
    _check_datetime_future_dates,
    _check_datetime_gaps,
    _check_datetime_monotonicity,
)
from hashprep.summaries.variables import _summarize_datetime
from hashprep.utils.type_inference import infer_types

# ---------------------------------------------------------------------------
# Type inference
# ---------------------------------------------------------------------------


class TestDateTimeTypeInference:
    def test_native_datetime64_col(self):
        df = pd.DataFrame({"ts": pd.date_range("2020-01-01", periods=50, freq="D")})
        types = infer_types(df)
        assert types["ts"] == "DateTime"

    def test_string_iso_dates_inferred_as_datetime(self):
        dates = [f"2021-{m:02d}-01" for m in range(1, 13)] * 5
        df = pd.DataFrame({"date": dates})
        types = infer_types(df)
        assert types["date"] == "DateTime"

    def test_string_datetime_with_time(self):
        timestamps = ["2022-03-15 08:30:00", "2022-03-16 12:00:00"] * 30
        df = pd.DataFrame({"created_at": timestamps})
        types = infer_types(df)
        assert types["created_at"] == "DateTime"

    def test_non_date_strings_not_datetime(self):
        df = pd.DataFrame({"name": ["Alice", "Bob", "Carol", "Dave"] * 20})
        types = infer_types(df)
        assert types["name"] != "DateTime"

    def test_low_cardinality_numeric_still_categorical(self):
        df = pd.DataFrame({"flag": [0, 1, 0, 1] * 25})
        types = infer_types(df)
        assert types["flag"] == "Categorical"

    def test_mostly_unparseable_object_column(self):
        # Only 20% parseable → should NOT be DateTime
        values = ["2021-01-01"] * 2 + ["foo bar baz"] * 8
        df = pd.DataFrame({"mixed": values * 10})
        types = infer_types(df)
        assert types["mixed"] != "DateTime"

    def test_empty_col_is_unsupported(self):
        df = pd.DataFrame({"empty": [None, None, None]})
        types = infer_types(df)
        assert types["empty"] == "Unsupported"


# ---------------------------------------------------------------------------
# _check_datetime_future_dates
# ---------------------------------------------------------------------------


class _FakeAnalyzer:
    """Minimal stand-in for DatasetAnalyzer used in unit tests."""

    def __init__(self, df, column_types):
        from hashprep.config import DEFAULT_CONFIG

        self.df = df
        self.column_types = column_types
        self.config = DEFAULT_CONFIG


class TestFutureDatesCheck:
    def _make(self, dates, col="date"):
        df = pd.DataFrame({col: pd.to_datetime(dates)})
        return _FakeAnalyzer(df, {col: "DateTime"})

    def test_no_future_dates(self):
        analyzer = self._make(["2020-01-01", "2021-06-15", "2019-12-31"])
        issues = _check_datetime_future_dates(analyzer)
        assert issues == []

    def test_small_future_ratio_is_warning(self):
        past = pd.date_range("2020-01-01", periods=98, freq="D").tolist()
        future = [pd.Timestamp.now() + pd.Timedelta(days=365)] * 2  # 2% future
        analyzer = self._make(past + future)
        issues = _check_datetime_future_dates(analyzer)
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert issues[0].category == "datetime_future_dates"

    def test_large_future_ratio_is_critical(self):
        past = pd.date_range("2020-01-01", periods=90, freq="D").tolist()
        future = [pd.Timestamp.now() + pd.Timedelta(days=365)] * 10  # 10% future
        analyzer = self._make(past + future)
        issues = _check_datetime_future_dates(analyzer)
        assert len(issues) == 1
        assert issues[0].severity == "critical"

    def test_non_datetime_col_ignored(self):
        df = pd.DataFrame({"score": [1.0, 2.0, 3.0]})
        analyzer = _FakeAnalyzer(df, {"score": "Numeric"})
        issues = _check_datetime_future_dates(analyzer)
        assert issues == []


# ---------------------------------------------------------------------------
# _check_datetime_gaps
# ---------------------------------------------------------------------------


class TestDatetimeGapsCheck:
    def _make(self, dates, col="ts"):
        df = pd.DataFrame({col: pd.to_datetime(dates)})
        return _FakeAnalyzer(df, {col: "DateTime"})

    def test_regular_series_no_gap_issue(self):
        dates = pd.date_range("2020-01-01", periods=30, freq="D")
        analyzer = self._make(dates)
        issues = _check_datetime_gaps(analyzer)
        assert issues == []

    def test_large_gap_raises_warning(self):
        # 29 days regular, then jump 6 months
        regular = pd.date_range("2020-01-01", periods=20, freq="D").tolist()
        after_gap = pd.date_range("2020-09-01", periods=20, freq="D").tolist()
        analyzer = self._make(regular + after_gap)
        issues = _check_datetime_gaps(analyzer)
        assert len(issues) == 1
        assert issues[0].category == "datetime_gaps"

    def test_too_few_rows_skipped(self):
        dates = pd.date_range("2020-01-01", periods=5, freq="D")
        analyzer = self._make(dates)
        issues = _check_datetime_gaps(analyzer)
        assert issues == []


# ---------------------------------------------------------------------------
# _check_datetime_monotonicity
# ---------------------------------------------------------------------------


class TestDatetimeMonotonicityCheck:
    def _make(self, dates, col="ts"):
        df = pd.DataFrame({col: pd.to_datetime(dates)})
        return _FakeAnalyzer(df, {col: "DateTime"})

    def test_monotonic_increasing_no_issue(self):
        dates = pd.date_range("2020-01-01", periods=50, freq="D")
        analyzer = self._make(dates)
        issues = _check_datetime_monotonicity(analyzer)
        assert issues == []

    def test_non_monotonic_raises_warning(self):
        dates = pd.date_range("2020-01-01", periods=50, freq="D").tolist()
        # Shuffle to break monotonicity
        dates[10], dates[20] = dates[20], dates[10]
        dates[30], dates[40] = dates[40], dates[30]
        analyzer = self._make(dates)
        issues = _check_datetime_monotonicity(analyzer)
        assert len(issues) == 1
        assert issues[0].category == "datetime_monotonicity"
        assert issues[0].severity == "warning"

    def test_low_unique_ratio_skipped(self):
        # Many duplicate timestamps → not treated as a time-series index
        dates = ["2020-01-01"] * 50
        analyzer = self._make(dates)
        issues = _check_datetime_monotonicity(analyzer)
        assert issues == []


# ---------------------------------------------------------------------------
# _summarize_datetime
# ---------------------------------------------------------------------------


class TestSummarizeDatetime:
    def _df(self, col, values):
        return pd.DataFrame({col: values})

    def test_basic_fields_present(self):
        df = self._df("dt", pd.date_range("2020-01-01", periods=30, freq="D"))
        result = _summarize_datetime(df, "dt")
        for key in ("minimum", "maximum", "range_days", "counts", "gap_stats", "monotonicity", "future_count"):
            assert key in result, f"Missing key: {key}"

    def test_monotonicity_increasing(self):
        df = self._df("dt", pd.date_range("2021-01-01", periods=20, freq="D"))
        result = _summarize_datetime(df, "dt")
        assert result["monotonicity"] == "increasing"

    def test_counts_contain_weekdays(self):
        df = self._df("dt", pd.date_range("2020-01-01", periods=30, freq="D"))
        result = _summarize_datetime(df, "dt")
        assert "weekdays" in result["counts"]

    def test_string_dates_parsed(self):
        df = self._df("date", ["2021-01-01", "2021-06-15", "2022-03-20"])
        result = _summarize_datetime(df, "date")
        assert result["minimum"] is not None
        assert result["range_days"] > 0

    def test_all_missing_returns_none_fields(self):
        df = self._df("dt", [None, None, None])
        result = _summarize_datetime(df, "dt")
        assert result["minimum"] is None
        assert result["counts"] is None

    def test_gap_stats_present_for_regular_series(self):
        df = self._df("dt", pd.date_range("2020-01-01", periods=20, freq="D"))
        result = _summarize_datetime(df, "dt")
        assert result["gap_stats"] is not None
        assert result["gap_stats"]["median_gap_seconds"] > 0

    def test_has_time_component_false_for_date_only(self):
        df = self._df("dt", pd.date_range("2020-01-01", periods=10, freq="D"))
        result = _summarize_datetime(df, "dt")
        assert result["has_time_component"] is False

    def test_has_time_component_true_for_timestamps(self):
        timestamps = pd.date_range("2020-01-01 08:00", periods=10, freq="h")
        df = self._df("ts", timestamps)
        result = _summarize_datetime(df, "ts")
        assert result["has_time_component"] is True
        assert result["counts"]["hours"] is not None


# ---------------------------------------------------------------------------
# Integration: DatasetAnalyzer picks up DateTime columns end-to-end
# ---------------------------------------------------------------------------


class TestDateTimeIntegration:
    def test_datetime_column_typed_correctly(self):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=50, freq="D"),
                "value": np.random.default_rng(0).standard_normal(50),
            }
        )
        analyzer = DatasetAnalyzer(df, auto_sample=False)
        summary = analyzer.analyze()
        assert summary["column_types"]["date"] == "DateTime"

    def test_string_date_column_typed_correctly(self):
        df = pd.DataFrame(
            {
                "created": [f"2021-{m:02d}-15" for m in range(1, 13)] * 5,
                "amount": np.random.default_rng(1).standard_normal(60),
            }
        )
        analyzer = DatasetAnalyzer(df, auto_sample=False)
        summary = analyzer.analyze()
        assert summary["column_types"]["created"] == "DateTime"

    def test_datetime_summary_in_variables(self):
        df = pd.DataFrame({"ts": pd.date_range("2022-01-01", periods=30, freq="D")})
        analyzer = DatasetAnalyzer(df, auto_sample=False)
        summary = analyzer.analyze()
        var = summary["summaries"]["variables"]["ts"]
        assert var["category"] == "DateTime"
        assert var["minimum"] is not None
        assert var["counts"]["weekdays"] is not None

    def test_future_dates_issue_detected(self):
        past = pd.date_range("2020-01-01", periods=90, freq="D").tolist()
        future = [pd.Timestamp.now() + pd.Timedelta(days=400)] * 10
        df = pd.DataFrame({"date": past + future})
        analyzer = DatasetAnalyzer(df, selected_checks=["datetime_future_dates"], auto_sample=False)
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "datetime_future_dates" in categories

    def test_gap_issue_detected(self):
        regular = pd.date_range("2020-01-01", periods=20, freq="D").tolist()
        after = pd.date_range("2021-06-01", periods=20, freq="D").tolist()
        df = pd.DataFrame({"ts": regular + after, "val": range(40)})
        analyzer = DatasetAnalyzer(df, selected_checks=["datetime_gaps"], auto_sample=False)
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "datetime_gaps" in categories

    def test_new_checks_in_all_checks(self):
        for check in ("datetime_future_dates", "datetime_gaps", "datetime_monotonicity"):
            assert check in DatasetAnalyzer.ALL_CHECKS
