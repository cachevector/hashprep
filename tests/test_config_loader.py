"""Tests for config file loading and config_from_dict."""

import json
import textwrap

import numpy as np
import pandas as pd
import pytest

from hashprep import DatasetAnalyzer, HashPrepConfig, load_config
from hashprep.config import DEFAULT_CONFIG, config_from_dict

# ---------------------------------------------------------------------------
# config_from_dict
# ---------------------------------------------------------------------------


class TestConfigFromDict:
    def test_empty_dict_returns_defaults(self):
        cfg = config_from_dict({})
        assert cfg == DEFAULT_CONFIG

    def test_partial_override_missing_values(self):
        cfg = config_from_dict({"missing_values": {"warning": 0.1}})
        assert cfg.missing_values.warning == 0.1
        # Other fields stay at default
        assert cfg.missing_values.critical == DEFAULT_CONFIG.missing_values.critical

    def test_partial_override_outliers(self):
        cfg = config_from_dict({"outliers": {"z_score": 3.0}})
        assert cfg.outliers.z_score == 3.0
        assert cfg.outliers.outlier_ratio_critical == DEFAULT_CONFIG.outliers.outlier_ratio_critical

    def test_multiple_section_override(self):
        cfg = config_from_dict(
            {
                "missing_values": {"warning": 0.2},
                "outliers": {"z_score": 2.5},
            }
        )
        assert cfg.missing_values.warning == 0.2
        assert cfg.outliers.z_score == 2.5
        # Unmodified sections stay at default
        assert cfg.correlations == DEFAULT_CONFIG.correlations

    def test_unknown_keys_are_ignored(self):
        # Should not raise
        cfg = config_from_dict({"nonexistent_section": {"foo": 1}})
        assert cfg == DEFAULT_CONFIG

    def test_unknown_nested_keys_are_ignored(self):
        cfg = config_from_dict({"outliers": {"z_score": 3.0, "nonexistent": 99}})
        assert cfg.outliers.z_score == 3.0

    def test_returns_hashprepconfig_instance(self):
        cfg = config_from_dict({})
        assert isinstance(cfg, HashPrepConfig)

    def test_result_is_frozen(self):
        cfg = config_from_dict({"outliers": {"z_score": 2.0}})
        with pytest.raises((AttributeError, TypeError)):
            cfg.outliers = None  # type: ignore[assignment]

    def test_int_override(self):
        cfg = config_from_dict({"statistical_tests": {"shapiro_max_n": 1000}})
        assert cfg.statistical_tests.shapiro_max_n == 1000

    def test_float_override(self):
        cfg = config_from_dict({"correlations": {"spearman_warning": 0.8}})
        assert cfg.correlations.spearman_warning == 0.8


# ---------------------------------------------------------------------------
# load_config — YAML
# ---------------------------------------------------------------------------


class TestLoadConfigYaml:
    def test_load_minimal_yaml(self, tmp_path):
        yaml_content = textwrap.dedent("""\
            missing_values:
              warning: 0.3
        """)
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(yaml_content)

        cfg = load_config(cfg_file)
        assert cfg.missing_values.warning == 0.3

    def test_load_yml_extension(self, tmp_path):
        cfg_file = tmp_path / "config.yml"
        cfg_file.write_text("outliers:\n  z_score: 3.5\n")
        cfg = load_config(cfg_file)
        assert cfg.outliers.z_score == 3.5

    def test_empty_yaml_returns_defaults(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("")
        cfg = load_config(cfg_file)
        assert cfg == DEFAULT_CONFIG

    def test_load_multi_section_yaml(self, tmp_path):
        yaml_content = textwrap.dedent("""\
            outliers:
              z_score: 3.0
              skewness_warning: 2.0
            correlations:
              spearman_warning: 0.8
        """)
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(yaml_content)
        cfg = load_config(cfg_file)
        assert cfg.outliers.z_score == 3.0
        assert cfg.outliers.skewness_warning == 2.0
        assert cfg.correlations.spearman_warning == 0.8


# ---------------------------------------------------------------------------
# load_config — JSON
# ---------------------------------------------------------------------------


class TestLoadConfigJson:
    def test_load_json(self, tmp_path):
        data = {"missing_values": {"warning": 0.25, "critical": 0.6}}
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(data))
        cfg = load_config(cfg_file)
        assert cfg.missing_values.warning == 0.25
        assert cfg.missing_values.critical == 0.6

    def test_empty_json_object_returns_defaults(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text("{}")
        cfg = load_config(cfg_file)
        assert cfg == DEFAULT_CONFIG


# ---------------------------------------------------------------------------
# load_config — error cases
# ---------------------------------------------------------------------------


class TestLoadConfigErrors:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_unsupported_extension(self, tmp_path):
        cfg_file = tmp_path / "config.ini"
        cfg_file.write_text("[section]\nkey = value\n")
        with pytest.raises(ValueError, match="Unsupported config file format"):
            load_config(cfg_file)


# ---------------------------------------------------------------------------
# DatasetAnalyzer — custom config respected by checks
# ---------------------------------------------------------------------------


rng = np.random.default_rng(0)


class TestAnalyzerCustomConfig:
    def test_default_config_is_set(self):
        df = pd.DataFrame({"x": rng.standard_normal(100)})
        analyzer = DatasetAnalyzer(df, auto_sample=False)
        assert analyzer.config == DEFAULT_CONFIG

    def test_custom_config_stored(self):
        df = pd.DataFrame({"x": rng.standard_normal(100)})
        custom = config_from_dict({"outliers": {"z_score": 2.0}})
        analyzer = DatasetAnalyzer(df, auto_sample=False, config=custom)
        assert analyzer.config.outliers.z_score == 2.0

    def test_high_missing_threshold_suppresses_issue(self):
        # Column has 50% missing — normally a warning, but with warning=0.9 it should be silent
        data = [1.0] * 50 + [float("nan")] * 50
        df = pd.DataFrame({"x": data})
        custom = config_from_dict({"missing_values": {"warning": 0.9, "critical": 0.95}})
        analyzer = DatasetAnalyzer(df, auto_sample=False, config=custom, selected_checks=["high_missing_values"])
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "missing_values" not in categories

    def test_low_missing_threshold_triggers_issue(self):
        # Column has 10% missing — default threshold is 0.4 (warning), but with 0.05 it should fire
        data = [1.0] * 90 + [float("nan")] * 10
        df = pd.DataFrame({"x": data})
        custom = config_from_dict({"missing_values": {"warning": 0.05, "critical": 0.5}})
        analyzer = DatasetAnalyzer(df, auto_sample=False, config=custom, selected_checks=["high_missing_values"])
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "missing_values" in categories

    def test_skewness_threshold_respected(self):
        # Highly skewed data — lower the threshold to catch it with warning=0.5
        data = [1.0] * 90 + [100.0] * 10
        df = pd.DataFrame({"x": data})
        custom = config_from_dict({"outliers": {"skewness_warning": 0.5, "skewness_critical": 20.0}})
        analyzer = DatasetAnalyzer(df, auto_sample=False, config=custom, selected_checks=["skewness"])
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "skewness" in categories

    def test_load_config_from_yaml_used_in_analyzer(self, tmp_path):
        yaml_content = "missing_values:\n  warning: 0.05\n  critical: 0.5\n"
        cfg_file = tmp_path / "custom.yaml"
        cfg_file.write_text(yaml_content)

        data = [1.0] * 90 + [float("nan")] * 10
        df = pd.DataFrame({"x": data})
        cfg = load_config(cfg_file)
        analyzer = DatasetAnalyzer(df, auto_sample=False, config=cfg, selected_checks=["high_missing_values"])
        summary = analyzer.analyze()
        categories = [i["category"] for i in summary["issues"]]
        assert "missing_values" in categories
