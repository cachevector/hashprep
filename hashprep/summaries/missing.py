import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def summarize_missing_values(df, include_plots=False):
    missing_count = {col: int(val) for col, val in df.isnull().sum().to_dict().items()}
    missing_percentage = {
        col: float(val)
        for col, val in (df.isnull().mean() * 100).round(2).to_dict().items()
    }
    missing_patterns = {
        col: df[df[col].isna()].index.tolist()
        for col in df.columns
        if df[col].isna().any()
    }
    plots = {}
    if include_plots:
        # Missing value bar plot
        missing_data = pd.Series(missing_count)
        if missing_data.sum() > 0:
            fig, ax = plt.subplots(figsize=(5, 3))
            missing_data[missing_data > 0].plot(kind="bar", ax=ax)
            ax.set_title("Missing Values Count by Column")
            ax.set_xlabel("Columns")
            ax.set_ylabel("Count")
            plt.xticks(rotation=45, ha="right")
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
            plt.close(fig)
            plots["missing_bar"] = img_str
        # Missing value heatmap
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis", ax=ax)
        ax.set_title("Missing Values Heatmap")
        ax.set_xlabel("Columns")
        ax.set_ylabel("Rows")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)
        plots["missing_heatmap"] = img_str

    missing_data = {}
    missing_data["missing_values"] = {"count": missing_count, "percentage": missing_percentage}
    missing_data["missing_patterns"] = missing_patterns
    missing_data["plots"] = plots

    return missing_data
