"""Centralized configuration for all HashPrep thresholds and defaults.

All magic numbers and thresholds are defined here to make them:
- Discoverable: one place to find all tuning knobs
- Configurable: easy to override for different use cases
- Documented: each threshold explains its purpose
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class MissingValueThresholds:
    """Thresholds for missing value detection."""
    warning: float = 0.4
    critical: float = 0.7
    dataset_warning_pct: float = 20.0
    dataset_critical_pct: float = 50.0
    pattern_p_value: float = 0.01
    pattern_critical_p_value: float = 0.001
    pattern_cramers_v_min: float = 0.1
    pattern_cohens_d_min: float = 0.2
    pattern_effect_critical: float = 0.3
    pattern_min_missing_count: int = 10
    pattern_min_group_size: int = 10
    pattern_rare_category_count: int = 5
    pattern_top_correlations: int = 3


@dataclass(frozen=True)
class OutlierThresholds:
    """Thresholds for outlier detection."""
    z_score: float = 4.0
    outlier_ratio_critical: float = 0.1
    zero_count_warning: float = 0.5
    zero_count_critical: float = 0.8
    text_length_max: int = 1000
    text_length_min: int = 1
    extreme_ratio_critical: float = 0.1
    skewness_warning: float = 3.0
    skewness_critical: float = 10.0
    datetime_skew: float = 0.8
    infinite_ratio_critical: float = 0.01
    constant_length_ratio: float = 0.95
    min_sample_size: int = 10


@dataclass(frozen=True)
class ColumnThresholds:
    """Thresholds for column-level checks."""
    high_cardinality_count: int = 100
    high_cardinality_ratio_critical: float = 0.9
    duplicate_ratio_critical: float = 0.1


@dataclass(frozen=True)
class CorrelationThresholds:
    """Thresholds for correlation analysis."""
    spearman_warning: float = 0.7
    spearman_critical: float = 0.95
    pearson_warning: float = 0.7
    pearson_critical: float = 0.95
    kendall_warning: float = 0.6
    kendall_critical: float = 0.85
    categorical_warning: float = 0.5
    categorical_critical: float = 0.8
    mixed_warning: float = 0.5
    mixed_critical: float = 0.8
    max_distinct_categories: int = 50
    low_cardinality_numeric: int = 10

    def as_nested_dict(self) -> dict:
        """Return thresholds in the nested dict format used by correlation checks."""
        return {
            'numeric': {
                'spearman': {'warning': self.spearman_warning, 'critical': self.spearman_critical},
                'pearson': {'warning': self.pearson_warning, 'critical': self.pearson_critical},
                'kendall': {'warning': self.kendall_warning, 'critical': self.kendall_critical},
            },
            'categorical': {'warning': self.categorical_warning, 'critical': self.categorical_critical},
            'mixed': {'warning': self.mixed_warning, 'critical': self.mixed_critical},
        }


@dataclass(frozen=True)
class LeakageThresholds:
    """Thresholds for data leakage detection."""
    numeric_critical: float = 0.98
    numeric_warning: float = 0.95
    categorical_critical: float = 0.95
    categorical_warning: float = 0.8
    f_stat_critical: float = 20.0
    f_stat_warning: float = 10.0
    f_stat_p_value: float = 0.001


@dataclass(frozen=True)
class DriftThresholds:
    """Thresholds for dataset drift detection."""
    p_value: float = 0.05
    critical_p_value: float = 0.001
    max_categories_for_chi2: int = 50
    max_new_category_samples: int = 5


@dataclass(frozen=True)
class DistributionThresholds:
    """Thresholds for distribution checks."""
    uniform_p_value: float = 0.1
    uniform_min_samples: int = 20
    unique_value_ratio: float = 0.95
    unique_min_samples: int = 10


@dataclass(frozen=True)
class ImbalanceThresholds:
    """Thresholds for class imbalance detection."""
    majority_class_ratio: float = 0.9


@dataclass(frozen=True)
class TypeInferenceConfig:
    """Configuration for type inference."""
    cat_cardinality_threshold: int = 50
    cat_percentage_threshold: float = 0.05
    num_low_cat_threshold: int = 10
    bool_mappings: Dict[str, bool] = field(default_factory=lambda: {
        'true': True, 'false': False,
        'yes': True, 'no': False,
        't': True, 'f': False,
    })


@dataclass(frozen=True)
class SamplingDefaults:
    """Default values for dataset sampling."""
    max_rows: int = 100_000
    memory_threshold_mb: float = 500.0


@dataclass(frozen=True)
class SummaryDefaults:
    """Defaults for summary generation."""
    histogram_bins: int = 10
    top_n_values: int = 10
    extreme_values_count: int = 10
    top_n_words: int = 10


@dataclass(frozen=True)
class HashPrepConfig:
    """Root configuration aggregating all threshold groups."""
    missing_values: MissingValueThresholds = field(default_factory=MissingValueThresholds)
    outliers: OutlierThresholds = field(default_factory=OutlierThresholds)
    columns: ColumnThresholds = field(default_factory=ColumnThresholds)
    correlations: CorrelationThresholds = field(default_factory=CorrelationThresholds)
    leakage: LeakageThresholds = field(default_factory=LeakageThresholds)
    drift: DriftThresholds = field(default_factory=DriftThresholds)
    distribution: DistributionThresholds = field(default_factory=DistributionThresholds)
    imbalance: ImbalanceThresholds = field(default_factory=ImbalanceThresholds)
    type_inference: TypeInferenceConfig = field(default_factory=TypeInferenceConfig)
    sampling: SamplingDefaults = field(default_factory=SamplingDefaults)
    summaries: SummaryDefaults = field(default_factory=SummaryDefaults)


# Global default config instance
DEFAULT_CONFIG = HashPrepConfig()
