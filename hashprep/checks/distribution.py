from typing import List

from scipy.stats import kstest

from .core import Issue
from ..config import DEFAULT_CONFIG

_DIST = DEFAULT_CONFIG.distribution

def _check_uniform_distribution(analyzer, p_threshold: float = _DIST.uniform_p_value) -> List[Issue]:
    """
    Detect uniformly distributed numeric columns using Kolmogorov-Smirnov test.
    Uniform distributions often indicate synthetic IDs or sequential data.
    """
    issues = []

    for col in analyzer.df.select_dtypes(include="number").columns:
        series = analyzer.df[col].dropna()
        if len(series) < _DIST.uniform_min_samples:
            continue

        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            continue

        normalized = (series - min_val) / (max_val - min_val)
        _, p_val = kstest(normalized, "uniform")
        is_monotonic = series.is_monotonic_increasing or series.is_monotonic_decreasing

        if p_val > p_threshold or is_monotonic:
            monotonic_note = " and monotonic" if is_monotonic else ""
            issues.append(
                Issue(
                    category="uniform_distribution",
                    severity="warning",
                    column=col,
                    description=f"'{col}' is uniformly distributed{monotonic_note}",
                    impact_score="low",
                    quick_fix=(
                        "Options:\n"
                        "- Drop column: Likely an ID or index (Pros: Reduces noise; Cons: None if not predictive).\n"
                        "- Verify purpose: Check if meaningful for prediction.\n"
                        "- Retain for joins: Keep if needed for data linking."
                    ),
                )
            )

    return issues


def _check_unique_values(analyzer, threshold: float = _DIST.unique_value_ratio) -> List[Issue]:
    """
    Detect columns where nearly all values are unique.
    High uniqueness often indicates identifiers, names, or free-text fields.
    """
    issues = []

    for col in analyzer.df.columns:
        series = analyzer.df[col].dropna()
        if len(series) < _DIST.unique_min_samples:
            continue

        unique_count = series.nunique()
        unique_ratio = unique_count / len(series)

        if unique_ratio >= threshold:
            issues.append(
                Issue(
                    category="unique_values",
                    severity="warning",
                    column=col,
                    description=f"'{col}' has unique values",
                    impact_score="low",
                    quick_fix=(
                        "Options:\n"
                        "- Drop column: Unique values add no predictive power (Pros: Simplifies model; Cons: Loses potential patterns).\n"
                        "- Extract features: Parse for patterns (e.g., titles from names).\n"
                        "- Use for text embedding: If NLP model appropriate."
                    ),
                )
            )

    return issues
