import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from typing import Dict, Optional, List, Any

# Set style
plt.style.use('ggplot')
sns.set_palette("husl")

def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return data

def plot_histogram(series: pd.Series, title: str) -> str:
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.histplot(series, bins=10, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(series.name)
    ax.set_ylabel("Count")
    return _fig_to_base64(fig)

def plot_bar(series: pd.Series, title: str, xlabel: str, ylabel: str) -> str:
    fig, ax = plt.subplots(figsize=(4, 3))
    series.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    return _fig_to_base64(fig)

def plot_heatmap(corr_matrix: pd.DataFrame, title: str, vmin: float = -1, vmax: float = 1) -> str:
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=vmin, vmax=vmax, ax=ax)
    ax.set_title(title)
    return _fig_to_base64(fig)

def plot_scatter(df: pd.DataFrame, x: str, y: str) -> str:
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.scatterplot(data=df, x=x, y=y, ax=ax)
    ax.set_title(f"{x} vs {y}")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return _fig_to_base64(fig)

def plot_missing_bar(missing_data: pd.Series) -> str:
    if missing_data.sum() == 0:
        return ""
    fig, ax = plt.subplots(figsize=(5, 3))
    missing_data[missing_data > 0].plot(kind="bar", ax=ax)
    ax.set_title("Missing Values Count by Column")
    ax.set_xlabel("Columns")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    return _fig_to_base64(fig)

def plot_missing_heatmap(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.heatmap(df.isnull(), cbar=False, cmap="viridis", ax=ax)
    ax.set_title("Missing Values Heatmap")
    ax.set_xlabel("Columns")
    ax.set_ylabel("Rows")
    return _fig_to_base64(fig)
