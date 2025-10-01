import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def summarize_variables(df, include_plots=False):
    variables = {}
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            variables[column] = _summarize_numeric_column(df, column, include_plots)
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            variables[column] = _summarize_datetime_column(df, column, include_plots)
        elif pd.api.types.is_string_dtype(df[column]):
            variables[column] = _summarize_text_column(df, column, include_plots)
        else:
            variables[column] = _summarize_categorical_column(df, column, include_plots)
    return variables


def _summarize_numeric_column(df, col, include_plots):
    series = df[col].dropna()
    stats = {
        "count": int(series.count()),
        "mean": float(series.mean().item()) if not series.empty else None,
        "std": float(series.std().item()) if not series.empty else None,
        "min": float(series.min().item()) if not series.empty else None,
        "max": float(series.max().item()) if not series.empty else None,
        "quantiles": (
            {
                "25%": float(series.quantile(0.25).item()),
                "50%": float(series.quantile(0.50).item()),
                "75%": float(series.quantile(0.75).item()),
            }
            if not series.empty
            else None
        ),
        "missing": int(df[col].isna().sum()),
        "zeros": int((series == 0).sum()),
    }
    if not series.empty:
        hist, bin_edges = np.histogram(
            series, bins=10, range=(series.min(), series.max())
        )
        stats["histogram"] = {
            "bin_edges": [float(x) for x in bin_edges],
            "counts": [int(x) for x in hist],
        }
        if include_plots:
            fig, ax = plt.subplots(figsize=(4, 3))
            sns.histplot(series, bins=10, ax=ax)
            ax.set_title(f"Histogram of {col}")
            ax.set_xlabel(col)
            ax.set_ylabel("Count")
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
            plt.close(fig)
            stats["plot"] = img_str  # Store plot directly in stats["plot"]
    else:
        stats["histogram"] = {"bin_edges": None, "counts": None}
    return stats


def _summarize_categorical_column(df, col, include_plots):
    series = df[col].dropna().astype(str)
    stats = {
        "count": int(series.count()),
        "unique": int(series.nunique()),
        "top_values": series.value_counts().head(10).to_dict(),
        "most_frequent": str(series.mode().iloc[0]) if not series.empty else None,
        "missing": int(df[col].isna().sum()),
    }
    if include_plots and not series.empty:
        fig, ax = plt.subplots(figsize=(4, 3))
        series.value_counts().head(10).plot(kind="bar", ax=ax)
        ax.set_title(f"Top Values of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)
        stats["plot"] = img_str
    return stats


def _summarize_text_column(df, col, include_plots):
    series = df[col].dropna().astype(str)
    lengths = series.str.len()
    stats = {
        "count": int(series.count()),
        "missing": int(df[col].isna().sum()),
        "avg_length": float(lengths.mean().item()) if not lengths.empty else None,
        "min_length": float(lengths.min().item()) if not lengths.empty else None,
        "max_length": float(lengths.max().item()) if not lengths.empty else None,
        "common_lengths": lengths.value_counts().head(5).to_dict(),
        "char_freq": (
            dict(
                zip(
                    list(
                        pd.Series(list("".join(series))).value_counts().head(10).index
                    ),
                    [
                        int(x)
                        for x in pd.Series(list("".join(series)))
                        .value_counts()
                        .head(10)
                        .values
                    ],
                )
            )
            if not series.empty
            else None
        ),
    }
    if include_plots and not lengths.empty:
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.histplot(lengths, bins=10, ax=ax)
        ax.set_title(f"Length Distribution of {col}")
        ax.set_xlabel("Length")
        ax.set_ylabel("Count")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)
        stats["plot"] = img_str
    return stats


def _summarize_datetime_column(df, col, include_plots):
    series = pd.to_datetime(df[col], errors="coerce").dropna()
    stats = {
        "count": int(series.count()),
        "missing": int(df[col].isna().sum()),
        "min": str(series.min()) if not series.empty else None,
        "max": str(series.max()) if not series.empty else None,
        "year_counts": (
            series.dt.year.value_counts().to_dict() if not series.empty else None
        ),
        "month_counts": (
            series.dt.month.value_counts().to_dict() if not series.empty else None
        ),
        "day_counts": (
            series.dt.day.value_counts().to_dict() if not series.empty else None
        ),
    }
    if include_plots and not series.empty:
        fig, ax = plt.subplots(figsize=(4, 3))
        series.dt.year.value_counts().sort_index().plot(kind="bar", ax=ax)
        ax.set_title(f"Year Distribution of {col}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)
        stats["plot"] = img_str
    return stats
