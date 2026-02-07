import pandas as pd
import numpy as np
import unicodedata
import re
from collections import defaultdict
from scipy.stats import median_abs_deviation

from ..utils.type_inference import infer_types


def get_monotonicity(series: pd.Series) -> str:
    if series.is_monotonic_increasing:
        return "increasing"
    elif series.is_monotonic_decreasing:
        return "decreasing"
    else:
        return "none"


def summarize_variables(df):
    inferred_types = infer_types(df)
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
    hist, bin_edges = np.histogram(series, bins=10, range=(min_val, max_val))
    histogram = {
        "bin_edges": [float(x) for x in bin_edges],
        "counts": [int(x) for x in hist],
    }
    vc = series.value_counts().head(10)
    common_values = {
        str(v): {"count": int(c), "percentage": float(c / n * 100)}
        for v, c in vc.items()
    }
    extremes = {
        "minimum_10": [float(x) for x in sorted(series)[:10]],
        "maximum_10": [float(x) for x in sorted(series)[-10:]],
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


# def summarize_variables(df, include_plots=False):
#     variables = {}
#     for column in df.columns:
#         if pd.api.types.is_numeric_dtype(df[column]):
#             variables[column] = _summarize_numeric_column(df, column, include_plots)
#         elif pd.api.types.is_datetime64_any_dtype(df[column]):
#             variables[column] = _summarize_datetime_column(df, column, include_plots)
#         elif pd.api.types.is_string_dtype(df[column]):
#             variables[column] = _summarize_text_column(df, column, include_plots)
#         else:
#             variables[column] = _summarize_categorical_column(df, column, include_plots)
#     return variables


# def _summarize_numeric_column(df, col, include_plots):
#     series = df[col].dropna()
#     stats = {
#         "count": int(series.count()),
#         "mean": float(series.mean().item()) if not series.empty else None,
#         "std": float(series.std().item()) if not series.empty else None,
#         "min": float(series.min().item()) if not series.empty else None,
#         "max": float(series.max().item()) if not series.empty else None,
#         "quantiles": (
#             {
#                 "25%": float(series.quantile(0.25).item()),
#                 "50%": float(series.quantile(0.50).item()),
#                 "75%": float(series.quantile(0.75).item()),
#             }
#             if not series.empty
#             else None
#         ),
#         "missing": int(df[col].isna().sum()),
#         "zeros": int((series == 0).sum()),
#     }
#     if not series.empty:
#         hist, bin_edges = np.histogram(
#             series, bins=10, range=(series.min(), series.max())
#         )
#         stats["histogram"] = {
#             "bin_edges": [float(x) for x in bin_edges],
#             "counts": [int(x) for x in hist],
#         }
#         if include_plots:
#             fig, ax = plt.subplots(figsize=(4, 3))
#             sns.histplot(series, bins=10, ax=ax)
#             ax.set_title(f"Histogram of {col}")
#             ax.set_xlabel(col)
#             ax.set_ylabel("Count")
#             buf = io.BytesIO()
#             fig.savefig(buf, format="png", bbox_inches="tight")
#             buf.seek(0)
#             img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
#             plt.close(fig)
#             stats["plot"] = img_str  # Store plot directly in stats["plot"]
#     else:
#         stats["histogram"] = {"bin_edges": None, "counts": None}
#     return stats


# def _summarize_categorical_column(df, col, include_plots):
#     series = df[col].dropna().astype(str)
#     stats = {
#         "count": int(series.count()),
#         "unique": int(series.nunique()),
#         "top_values": series.value_counts().head(10).to_dict(),
#         "most_frequent": str(series.mode().iloc[0]) if not series.empty else None,
#         "missing": int(df[col].isna().sum()),
#     }
#     if include_plots and not series.empty:
#         fig, ax = plt.subplots(figsize=(4, 3))
#         series.value_counts().head(10).plot(kind="bar", ax=ax)
#         ax.set_title(f"Top Values of {col}")
#         ax.set_xlabel(col)
#         ax.set_ylabel("Count")
#         plt.xticks(rotation=45, ha="right")
#         buf = io.BytesIO()
#         fig.savefig(buf, format="png", bbox_inches="tight")
#         buf.seek(0)
#         img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
#         plt.close(fig)
#         stats["plot"] = img_str
#     return stats


# def _summarize_text_column(df, col, include_plots):
#     series = df[col].dropna().astype(str)
#     lengths = series.str.len()
#     stats = {
#         "count": int(series.count()),
#         "missing": int(df[col].isna().sum()),
#         "avg_length": float(lengths.mean().item()) if not lengths.empty else None,
#         "min_length": float(lengths.min().item()) if not lengths.empty else None,
#         "max_length": float(lengths.max().item()) if not lengths.empty else None,
#         "common_lengths": lengths.value_counts().head(5).to_dict(),
#         "char_freq": (
#             dict(
#                 zip(
#                     list(
#                         pd.Series(list("".join(series))).value_counts().head(10).index
#                     ),
#                     [
#                         int(x)
#                         for x in pd.Series(list("".join(series)))
#                         .value_counts()
#                         .head(10)
#                         .values
#                     ],
#                 )
#             )
#             if not series.empty
#             else None
#         ),
#     }
#     if include_plots and not lengths.empty:
#         fig, ax = plt.subplots(figsize=(4, 3))
#         sns.histplot(lengths, bins=10, ax=ax)
#         ax.set_title(f"Length Distribution of {col}")
#         ax.set_xlabel("Length")
#         ax.set_ylabel("Count")
#         buf = io.BytesIO()
#         fig.savefig(buf, format="png", bbox_inches="tight")
#         buf.seek(0)
#         img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
#         plt.close(fig)
#         stats["plot"] = img_str
#     return stats


# def _summarize_datetime_column(df, col, include_plots):
#     series = pd.to_datetime(df[col], errors="coerce").dropna()
#     stats = {
#         "count": int(series.count()),
#         "missing": int(df[col].isna().sum()),
#         "min": str(series.min()) if not series.empty else None,
#         "max": str(series.max()) if not series.empty else None,
#         "year_counts": (
#             series.dt.year.value_counts().to_dict() if not series.empty else None
#         ),
#         "month_counts": (
#             series.dt.month.value_counts().to_dict() if not series.empty else None
#         ),
#         "day_counts": (
#             series.dt.day.value_counts().to_dict() if not series.empty else None
#         ),
#     }
#     if include_plots and not series.empty:
#         fig, ax = plt.subplots(figsize=(4, 3))
#         series.dt.year.value_counts().sort_index().plot(kind="bar", ax=ax)
#         ax.set_title(f"Year Distribution of {col}")
#         ax.set_xlabel("Year")
#         ax.set_ylabel("Count")
#         buf = io.BytesIO()
#         fig.savefig(buf, format="png", bbox_inches="tight")
#         buf.seek(0)
#         img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
#         plt.close(fig)
#         stats["plot"] = img_str
#     return stats
