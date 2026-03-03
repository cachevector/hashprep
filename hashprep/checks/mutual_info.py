"""
Check for features with near-zero mutual information with the target column.
Near-zero MI means the feature carries almost no information about the target
and is likely useless (or worse — noise) for a predictive model.
"""

from ..summaries.mutual_info import summarize_mutual_information
from .core import Issue


def _check_low_mutual_information(analyzer) -> list[Issue]:
    """
    Flag features whose mutual information with the target column is below
    the configured warning threshold. Requires target_col to be set.
    """
    if analyzer.target_col is None:
        return []

    mi_result = summarize_mutual_information(analyzer.df, analyzer.target_col, analyzer.column_types)
    if not mi_result or not mi_result.get("scores"):
        return []

    _cfg = analyzer.config.mutual_info
    issues = []
    scores = mi_result["scores"]
    task = mi_result["task"]

    for col, score in scores.items():
        if score < _cfg.low_mi_warning:
            issues.append(
                Issue(
                    category="low_mutual_information",
                    severity="warning",
                    column=col,
                    description=(
                        f"Column '{col}' has near-zero mutual information with target "
                        f"'{analyzer.target_col}' (MI={score:.4f} nats, task={task})"
                    ),
                    impact_score="medium",
                    quick_fix=(
                        "Options:\n"
                        "- Drop feature: Near-zero MI suggests no predictive signal for the target.\n"
                        "- Investigate interactions: Feature may be useful combined with others.\n"
                        "- Check encoding: Categorical features may need different encoding.\n"
                        "- Retain for now: MI is marginal; feature interactions may matter."
                    ),
                )
            )

    return issues
