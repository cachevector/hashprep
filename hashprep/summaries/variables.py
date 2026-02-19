import pandas as pd
import numpy as np
import unicodedata
import re
from collections import defaultdict
from scipy.stats import median_abs_deviation
from ..config import DEFAULT_CONFIG

_SUMMARY = DEFAULT_CONFIG.summaries

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
        distinct_percentage = (
            (distinct_count / non_missing_count * 100) if non_missing_count > 0 else 0
        )
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
    mean_val = float(series.mean())
    min_val = float(series.min())
    max_val = float(series.max())
    q = series.quantile([0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0])
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
    cv = float(series.std() / abs(mean_val)) if mean_val != 0 else None
    descriptive = {
        "standard_deviation": float(series.std()),
        "coefficient_of_variation": cv,
        "kurtosis": float(series.kurtosis()),
        "mean": mean_val,
        "mad": float(median_abs_deviation(series)),
        "skewness": float(series.skew()),
        "sum": float(series.sum()),
        "variance": float(series.var()),
        "monotonicity": get_monotonicity(series),
    }
    hist, bin_edges = np.histogram(series, bins=_SUMMARY.histogram_bins, range=(min_val, max_val))
    histogram = {
        "bin_edges": [float(x) for x in bin_edges],
        "counts": [int(x) for x in hist],
    }
    vc = series.value_counts().head(_SUMMARY.top_n_values)
    common_values = {
        str(v): {"count": int(c), "percentage": float(c / n * 100)}
        for v, c in vc.items()
    }
    extremes = {
        "minimum_10": [float(x) for x in sorted(series)[:_SUMMARY.extreme_values_count]],
        "maximum_10": [float(x) for x in sorted(series)[-_SUMMARY.extreme_values_count:]],
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
    n = len(series)
    all_text = "".join(series)
    total_chars = len(all_text)
    distinct_chars = len(set(all_text))
    all_categories = [unicodedata.category(c) for c in all_text]
    cat_series = pd.Series(all_categories)
    distinct_categories = int(cat_series.nunique())
    most_occurring_categories = cat_series.value_counts().head(10).to_dict()
    cat_to_char_count = defaultdict(lambda: defaultdict(int))
    for c in all_text:
        cat = unicodedata.category(c)
        cat_to_char_count[cat][c] += 1
    most_freq_per_cat = {}
    for cat, char_count in cat_to_char_count.items():
        if char_count:
            top_char = max(char_count, key=char_count.get)
            count = char_count[top_char]
            freq = (count / total_chars * 100) if total_chars > 0 else 0
            most_freq_per_cat[cat] = {
                "char": top_char,
                "count": count,
                "percentage": float(freq),
            }
    distinct_scripts = None
    most_occurring_scripts = None
    words = re.findall(r"\b\w+\b", all_text.lower())
    word_len = len(words)
    word_vc = pd.Series(words).value_counts().head(10)
    words_dict = {
        w: {
            "count": int(c),
            "frequency": float(c / word_len * 100) if word_len > 0 else 0.0,
        }
        for w, c in word_vc.items()
    }
    char_vc = pd.Series(list(all_text)).value_counts().head(10)
    char_dict = {
        str(c): {
            "count": int(v),
            "percentage": float(v / total_chars * 100) if total_chars > 0 else 0.0,
        }
        for c, v in char_vc.items()
    }
    cat_dict = {
        k: {
            "count": v,
            "percentage": float(v / total_chars * 100) if total_chars > 0 else 0.0,
        }
        for k, v in most_occurring_categories.items()
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
                "distinct_scripts": distinct_scripts,
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
                "most_occurring_scripts": most_occurring_scripts,
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
    common_values = {
        v: {"count": int(c), "percentage": float(c / n * 100)} for v, c in vc.items()
    }
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
    dt_series = pd.to_datetime(df[col], errors="coerce")
    valid_series = dt_series.dropna()
    parse_fails = int((dt_series.isna() & df[col].notna()).sum())
    invalid_percentage = (parse_fails / len(df) * 100) if len(df) > 0 else 0.0

    if valid_series.empty:
        return {
            "minimum": None,
            "maximum": None,
            "range_days": None,
            "invalid_count": parse_fails,
            "invalid_percentage": invalid_percentage,
            "counts": None,
        }

    min_dt = valid_series.min()
    max_dt = valid_series.max()
    range_delta = max_dt - min_dt

    year_counts = valid_series.dt.year.value_counts().to_dict()
    month_counts = valid_series.dt.month.value_counts().to_dict()
    day_counts = valid_series.dt.day.value_counts().to_dict()

    stats = {
        "minimum": str(min_dt),
        "maximum": str(max_dt),
        "range_days": int(range_delta.days),
        "range_str": str(range_delta),
        "invalid_count": parse_fails,
        "invalid_percentage": invalid_percentage,
        "counts": {
            "years": year_counts,
            "months": month_counts,
            "days": day_counts,
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
    common_values = {
        str(k): {"count": int(v), "percentage": float(v / n * 100)}
        for k, v in vc.items()
    }
    stats = {"common_values": common_values}
    return stats
