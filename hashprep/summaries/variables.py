import re
import unicodedata
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy.stats import median_abs_deviation, normaltest, shapiro

from ..config import DEFAULT_CONFIG

_SUMMARY = DEFAULT_CONFIG.summaries
_ST = DEFAULT_CONFIG.statistical_tests


def get_monotonicity(series: pd.Series) -> str:
    if series.is_monotonic_increasing:
        return "increasing"
    elif series.is_monotonic_decreasing:
        return "decreasing"
    else:
        return "none"


def summarize_variables(df, column_types=None):
    if column_types is None:
        from ..utils.type_inference import infer_types

        column_types = infer_types(df)
    inferred_types = column_types
    variables = {}
    for column in df.columns:
        typ = inferred_types.get(column, "Unsupported")
        non_missing_count = df[column].notna().sum()
        distinct_count = df[column].nunique()
        distinct_percentage = (distinct_count / non_missing_count * 100) if non_missing_count > 0 else 0
        missing_count = int(df[column].isna().sum())
        missing_percentage = (missing_count / len(df) * 100) if len(df) > 0 else 0
        memory_size = df[column].memory_usage(deep=True)
        summary = {
            "category": typ,
            "alerts": [],
            "distinct_count": int(distinct_count),
            "distinct_percentage": float(distinct_percentage),
            "missing_count": missing_count,
            "missing_percentage": float(missing_percentage),
            "memory_size": memory_size,
        }
        if typ == "Numeric":
            summary.update(_summarize_numeric(df, column))
        elif typ == "Text":
            summary.update(_summarize_text(df, column))
        elif typ == "Categorical":
            summary.update(_summarize_categorical(df, column))
        elif typ == "DateTime":
            summary.update(_summarize_datetime(df, column))
        elif typ == "Boolean":
            summary.update(_summarize_boolean(df, column))
        else:  # Unsupported
            pass  # Basics already included
        variables[column] = summary
    return variables


def _summarize_numeric(df, col):
    series = df[col].dropna()
    if series.empty:
        return {
            "infinite_count": 0,
            "infinite_percentage": 0.0,
            "mean": None,
            "minimum": None,
            "maximum": None,
            "zeros_count": 0,
            "zeros_percentage": 0.0,
            "negative_count": 0,
            "negative_percentage": 0.0,
            "statistics": {"quantiles": None, "descriptive": None},
            "histogram": {"bin_edges": None, "counts": None},
            "common_values": None,
            "extreme_values": {"minimum_10": None, "maximum_10": None},
        }
    n = len(series)
    infinite_count = int(np.isinf(df[col]).sum())
    infinite_percentage = (infinite_count / len(df) * 100) if len(df) > 0 else 0.0
    zeros_count = int((series == 0).sum())
    zeros_percentage = zeros_count / n * 100
    negative_count = int((series < 0).sum())
    negative_percentage = negative_count / n * 100
    # Use finite-only series for distribution statistics to avoid np.histogram crashing
    finite = series[np.isfinite(series)]
    mean_val = float(finite.mean()) if not finite.empty else float("nan")
    min_val = float(finite.min()) if not finite.empty else float("nan")
    max_val = float(finite.max()) if not finite.empty else float("nan")
    q = finite.quantile([0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0])
    quantiles = {
        "minimum": float(q[0]),
        "p5": float(q[0.05]),
        "q1": float(q[0.25]),
        "median": float(q[0.5]),
        "q3": float(q[0.75]),
        "p95": float(q[0.95]),
        "maximum": float(q[1.0]),
        "range": float(q[1.0] - q[0]),
        "iqr": float(q[0.75] - q[0.25]),
    }
    cv = float(finite.std() / abs(mean_val)) if mean_val != 0 else None
    descriptive = {
        "standard_deviation": float(finite.std()),
        "coefficient_of_variation": cv,
        "kurtosis": float(finite.kurtosis()),
        "mean": mean_val,
        "mad": float(median_abs_deviation(finite)),
        "skewness": float(finite.skew()),
        "sum": float(finite.sum()),
        "variance": float(finite.var()),
        "monotonicity": get_monotonicity(finite),
    }
    hist, bin_edges = np.histogram(finite, bins=_SUMMARY.histogram_bins, range=(min_val, max_val))
    histogram = {
        "bin_edges": [float(x) for x in bin_edges],
        "counts": [int(x) for x in hist],
    }
    vc = finite.value_counts().head(_SUMMARY.top_n_values)
    common_values = {str(v): {"count": int(c), "percentage": float(c / n * 100)} for v, c in vc.items()}
    extremes = {
        "minimum_10": [float(x) for x in sorted(finite)[: _SUMMARY.extreme_values_count]],
        "maximum_10": [float(x) for x in sorted(finite)[-_SUMMARY.extreme_values_count :]],
    }
    # Normality test (Shapiro-Wilk for small n, D'Agostino-Pearson for large n)
    normality = None
    if n >= _ST.normality_min_n and series.nunique() > 1:
        finite = series[np.isfinite(series)]
        if len(finite) >= _ST.normality_min_n:
            if len(finite) <= _ST.shapiro_max_n:
                norm_stat, norm_p = shapiro(finite)
                norm_test = "shapiro_wilk"
            else:
                norm_stat, norm_p = normaltest(finite)
                norm_test = "dagostino_pearson"
            normality = {
                "test": norm_test,
                "statistic": float(norm_stat),
                "p_value": float(norm_p),
                "is_normal": float(norm_p) >= _ST.normality_p_value,
            }

    stats = {
        "infinite_count": infinite_count,
        "infinite_percentage": float(infinite_percentage),
        "mean": mean_val,
        "minimum": min_val,
        "maximum": max_val,
        "zeros_count": zeros_count,
        "zeros_percentage": zeros_percentage,
        "negative_count": negative_count,
        "negative_percentage": negative_percentage,
        "statistics": {"quantiles": quantiles, "descriptive": descriptive},
        "histogram": histogram,
        "common_values": common_values,
        "extreme_values": extremes,
        "normality": normality,
    }
    return stats


def _summarize_text(df, col):
    series = df[col].dropna().astype(str)
    if series.empty:
        return {
            "overview": {
                "length": {
                    "max_length": None,
                    "median_length": None,
                    "mean_length": None,
                    "min_length": None,
                },
                "characters_and_unicode": {
                    "total_characters": 0,
                    "distinct_characters": 0,
                    "distinct_categories": 0,
                    "distinct_scripts": None,
                    "distinct_blocks": None,
                },
                "sample": [],
            },
            "words": {},
            "characters": {
                "most_occurring_characters": {},
                "categories": {
                    "most_occurring_categories": {},
                    "most_frequent_character_per_category": {},
                },
                "scripts": {
                    "most_occurring_scripts": None,
                    "most_frequent_character_per_script": None,
                },
                "blocks": {
                    "most_occurring_blocks": None,
                    "most_frequent_character_per_block": None,
                },
            },
        }
    lengths = series.str.len()
    all_text = "".join(series)
    total_chars = len(all_text)

    # Single pass: collect char counts, category counts, and per-category char counts
    char_counts = Counter()
    cat_counts = Counter()
    cat_to_char_count = defaultdict(Counter)
    for c in all_text:
        char_counts[c] += 1
        cat = unicodedata.category(c)
        cat_counts[cat] += 1
        cat_to_char_count[cat][c] += 1

    distinct_chars = len(char_counts)
    distinct_categories = len(cat_counts)

    most_freq_per_cat = {}
    for cat, char_counter in cat_to_char_count.items():
        top_char, count = char_counter.most_common(1)[0]
        freq = (count / total_chars * 100) if total_chars > 0 else 0
        most_freq_per_cat[cat] = {
            "char": top_char,
            "count": count,
            "percentage": float(freq),
        }

    # Word analysis
    words = re.findall(r"\b\w+\b", all_text.lower())
    word_len = len(words)
    words_dict = {
        w: {
            "count": c,
            "frequency": float(c / word_len * 100) if word_len > 0 else 0.0,
        }
        for w, c in Counter(words).most_common(10)
    }

    # Top characters and categories
    char_dict = {
        str(c): {
            "count": v,
            "percentage": float(v / total_chars * 100) if total_chars > 0 else 0.0,
        }
        for c, v in char_counts.most_common(10)
    }
    cat_dict = {
        k: {
            "count": v,
            "percentage": float(v / total_chars * 100) if total_chars > 0 else 0.0,
        }
        for k, v in cat_counts.most_common(10)
    }
    sample = [str(s) for s in series.head(5).tolist()]
    stats = {
        "overview": {
            "length": {
                "max_length": int(lengths.max()),
                "median_length": float(lengths.median()),
                "mean_length": float(lengths.mean()),
                "min_length": int(lengths.min()),
            },
            "characters_and_unicode": {
                "total_characters": total_chars,
                "distinct_characters": distinct_chars,
                "distinct_categories": distinct_categories,
                "distinct_scripts": None,
                "distinct_blocks": None,
            },
            "sample": sample,
        },
        "words": words_dict,
        "characters": {
            "most_occurring_characters": char_dict,
            "categories": {
                "most_occurring_categories": cat_dict,
                "most_frequent_character_per_category": most_freq_per_cat,
            },
            "scripts": {
                "most_occurring_scripts": None,
                "most_frequent_character_per_script": None,
            },
            "blocks": {
                "most_occurring_blocks": None,
                "most_frequent_character_per_block": None,
            },
        },
    }
    return stats


def _summarize_categorical(df, col):
    series = df[col].dropna().astype(str)
    if series.empty:
        return {
            "overview": {
                "length": {
                    "max_length": None,
                    "median_length": None,
                    "mean_length": None,
                    "min_length": None,
                },
                "characters_and_unicode": {
                    "total_characters": 0,
                    "distinct_characters": 0,
                    "distinct_categories": 0,
                    "distinct_scripts": None,
                    "distinct_blocks": None,
                },
                "sample": [],
            },
            "categories": {"common_values": {}},
            "words": {},
            "characters": {
                "most_occurring_characters": {},
                "categories": {
                    "most_occurring_categories": {},
                    "most_frequent_character_per_category": {},
                },
                "scripts": {
                    "most_occurring_scripts": None,
                    "most_frequent_character_per_script": None,
                },
                "blocks": {
                    "most_occurring_blocks": None,
                    "most_frequent_character_per_block": None,
                },
            },
        }
    text_summary = _summarize_text(df, col)
    n = len(series)
    vc = series.value_counts().head(10)
    common_values = {v: {"count": int(c), "percentage": float(c / n * 100)} for v, c in vc.items()}
    stats = {
        "overview": text_summary["overview"],
        "categories": {
            "common_values": common_values,
            "length": text_summary["overview"]["length"],
        },
        "words": text_summary["words"],
        "characters": text_summary["characters"],
    }
    return stats


def _summarize_datetime(df, col):
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        dt_series = df[col]
        parse_fails = 0
    else:
        dt_series = pd.to_datetime(df[col], errors="coerce")
        parse_fails = int((dt_series.isna() & df[col].notna()).sum())

    valid_series = dt_series.dropna()
    invalid_percentage = (parse_fails / len(df) * 100) if len(df) > 0 else 0.0

    if valid_series.empty:
        return {
            "minimum": None,
            "maximum": None,
            "range_days": None,
            "invalid_count": parse_fails,
            "invalid_percentage": invalid_percentage,
            "counts": None,
            "gap_stats": None,
            "monotonicity": None,
            "future_count": None,
        }

    min_dt = valid_series.min()
    max_dt = valid_series.max()
    range_delta = max_dt - min_dt
    now = pd.Timestamp.now()

    year_counts = {int(k): int(v) for k, v in valid_series.dt.year.value_counts().items()}
    month_counts = {int(k): int(v) for k, v in valid_series.dt.month.value_counts().items()}
    weekday_counts = {int(k): int(v) for k, v in valid_series.dt.dayofweek.value_counts().items()}
    day_counts = {int(k): int(v) for k, v in valid_series.dt.day.value_counts().items()}

    # Sub-day precision: include hour distribution if values have non-zero hours
    has_time = bool((valid_series.dt.hour != 0).any() or (valid_series.dt.minute != 0).any())
    hour_counts = {int(k): int(v) for k, v in valid_series.dt.hour.value_counts().items()} if has_time else None

    # Gap statistics (sorted diffs)
    sorted_series = valid_series.sort_values()
    diffs = sorted_series.diff().dropna()
    gap_stats = None
    if len(diffs) > 0:
        diff_seconds = diffs.dt.total_seconds()
        gap_stats = {
            "median_gap_seconds": float(diff_seconds.median()),
            "max_gap_seconds": float(diff_seconds.max()),
            "min_gap_seconds": float(diff_seconds.min()),
            "mean_gap_seconds": float(diff_seconds.mean()),
        }

    # Monotonicity
    if valid_series.is_monotonic_increasing:
        monotonicity = "increasing"
    elif valid_series.is_monotonic_decreasing:
        monotonicity = "decreasing"
    else:
        monotonicity = "non-monotonic"

    # Future dates
    future_count = int((valid_series > now).sum())

    stats = {
        "minimum": str(min_dt),
        "maximum": str(max_dt),
        "range_days": int(range_delta.days),
        "range_str": str(range_delta),
        "invalid_count": parse_fails,
        "invalid_percentage": float(invalid_percentage),
        "future_count": future_count,
        "monotonicity": monotonicity,
        "has_time_component": has_time,
        "gap_stats": gap_stats,
        "counts": {
            "years": year_counts,
            "months": month_counts,
            "weekdays": weekday_counts,
            "days": day_counts,
            "hours": hour_counts,
        },
    }
    return stats


def _summarize_boolean(df, col):
    series = df[col]
    if series.dtype == "bool":
        vc = series.value_counts()
    else:
        bool_series = pd.to_numeric(series, errors="coerce").notna().astype(bool)
        vc = bool_series.value_counts()
    n = len(series)
    common_values = {str(k): {"count": int(v), "percentage": float(v / n * 100)} for k, v in vc.items()}
    stats = {"common_values": common_values}
    return stats
