import base64
import os
from typing import Dict, List

import pandas as pd

import hashprep


class MarkdownReport:
    ALERT_TYPE_MAPPING = {
        "feature_correlation": "High Correlation",
        "categorical_correlation": "High Correlation",
        "mixed_correlation": "High Correlation",
        "missing_values": "Missing",
        "high_missing_values": "Missing",
        "dataset_missingness": "Missing",
        "missing_patterns": "Missing",
        "uniform_distribution": "Uniform",
        "unique_values": "Unique",
        "high_zero_counts": "Zeros",
        "outliers": "Outliers",
        "skewness": "Skewness",
        "high_cardinality": "High Cardinality",
        "duplicates": "Duplicates",
        "data_leakage": "Leakage",
        "target_leakage_patterns": "Leakage",
        "class_imbalance": "Imbalance",
        "empty_columns": "Empty",
        "single_value_columns": "Constant",
        "mixed_data_types": "Mixed Types",
        "extreme_text_lengths": "Text Length",
        "datetime_skew": "DateTime Skew",
        "dataset_drift": "Drift",
        "infinite_values": "Infinite",
        "constant_length": "Constant Length",
        "empty_dataset": "Empty Dataset",
    }

    def generate(self, summary, full=False, output_file=None):
        dataset_info = summary["summaries"]["dataset_info"]
        reproduction_info = summary["summaries"].get("reproduction_info", {})
        variable_type_counts = summary["summaries"].get("variable_type_counts", {})

        content = "# Dataset Quality Report\n\n"

        # Dataset Overview
        content += "## Overview\n\n"
        content += "### Dataset Statistics\n\n"
        content += "| Metric | Value |\n|--------|-------|\n"
        content += f"| Number of variables | {dataset_info['columns']} |\n"
        content += f"| Number of observations | {dataset_info['rows']} |\n"
        content += f"| Missing cells | {dataset_info['missing_cells']} |\n"
        content += f"| Missing cells (%) | {dataset_info['missing_percentage']}% |\n"
        content += f"| Duplicate rows | {dataset_info.get('duplicate_rows', 0)} |\n"
        content += f"| Duplicate rows (%) | {dataset_info.get('duplicate_percentage', 0)}% |\n"
        content += f"| Total size in memory | {dataset_info.get('memory_kib', 0)} KiB |\n"
        content += f"| Average record size | {dataset_info.get('average_record_size_bytes', 0)} B |\n\n"

        content += "### Variable Types\n\n"
        content += "| Type | Count |\n|------|-------|\n"
        for type_name, count in variable_type_counts.items():
            if count > 0:
                content += f"| {type_name} | {count} |\n"
        content += "\n"

        # Alerts Section
        content += "## Alerts\n\n"
        content += f"**Critical Issues:** {summary['critical_count']} | **Warnings:** {summary['warning_count']}\n\n"

        alerts_by_type = self._group_alerts_by_type(summary["issues"])
        for alert_type, alerts in alerts_by_type.items():
            if alerts:
                content += f"### {alert_type}\n\n"
                for alert in alerts:
                    severity_marker = "**" if alert["severity"] == "critical" else ""
                    content += f"- {severity_marker}{alert['description']}{severity_marker}\n"
                content += "\n"

        # Reproduction Section
        content += "## Reproduction\n\n"
        content += "| Property | Value |\n|----------|-------|\n"
        analysis_started = reproduction_info.get("analysis_started", "N/A")
        analysis_finished = reproduction_info.get("analysis_finished", "N/A")
        content += f"| Analysis started | {analysis_started[:19] if analysis_started != 'N/A' else 'N/A'} |\n"
        content += f"| Analysis finished | {analysis_finished[:19] if analysis_finished != 'N/A' else 'N/A'} |\n"
        content += f"| Duration | {reproduction_info.get('duration_seconds', 0)} seconds |\n"
        content += f"| Software version | hashprep v{hashprep.__version__} |\n\n"

        if full:
            img_dir = None
            report_name = None
            if output_file:
                report_dir = os.path.dirname(output_file) or "."
                report_name = os.path.splitext(os.path.basename(output_file))[0]
                img_dir = os.path.join(report_dir, f"{report_name}_images")
                os.makedirs(img_dir, exist_ok=True)

            # Variable Analysis
            content += "## Variable Analysis\n\n"
            for col, stats in summary["summaries"]["variables"].items():
                cat = stats.get("category", "Unknown")
                badges = f"`{cat}`"
                if stats.get("distinct_percentage", 0) >= 95:
                    badges += " `Unique`"
                if stats.get("missing_percentage", 0) > 0:
                    badges += f" `{stats['missing_percentage']:.1f}% missing`"

                content += f"### {col}\n"
                content += f"{badges}\n\n"

                # Summary line
                content += "| Metric | Value |\n|--------|-------|\n"
                content += f"| Distinct | {stats.get('distinct_count', 0)} ({stats.get('distinct_percentage', 0):.1f}%) |\n"
                content += f"| Missing | {stats.get('missing_count', 0)} ({stats.get('missing_percentage', 0):.1f}%) |\n"
                if cat == "Numeric":
                    mean_val = stats.get("mean")
                    content += f"| Mean | {f'{mean_val:.6g}' if mean_val is not None else 'N/A'} |\n"
                    min_val = stats.get("minimum")
                    max_val = stats.get("maximum")
                    content += f"| Min | {f'{min_val:.6g}' if min_val is not None else 'N/A'} |\n"
                    content += f"| Max | {f'{max_val:.6g}' if max_val is not None else 'N/A'} |\n"
                    content += f"| Memory | {stats.get('memory_size', 0) / 1024:.1f} KiB |\n"
                else:
                    content += f"| Memory | {stats.get('memory_size', 0) / 1024:.1f} KiB |\n"
                    if stats.get("overview") and stats["overview"].get("length"):
                        ln = stats["overview"]["length"]
                        content += f"| Min length | {ln.get('min_length', 'N/A')} |\n"
                        content += f"| Max length | {ln.get('max_length', 'N/A')} |\n"
                        mean_ln = ln.get("mean_length")
                        content += f"| Mean length | {f'{mean_ln:.2f}' if mean_ln else 'N/A'} |\n"
                content += "\n"

                # Detailed Statistics
                if cat == "Numeric" and stats.get("statistics"):
                    s = stats["statistics"]
                    content += "#### Quantile Statistics\n\n"
                    content += "| Statistic | Value |\n|-----------|-------|\n"
                    q = s.get("quantiles", {})
                    content += f"| Minimum | {q.get('minimum', 0):.6g} |\n"
                    content += f"| 5th percentile | {q.get('p5', 0):.6g} |\n"
                    content += f"| Q1 (25%) | {q.get('q1', 0):.6g} |\n"
                    content += f"| Median (50%) | {q.get('median', 0):.6g} |\n"
                    content += f"| Q3 (75%) | {q.get('q3', 0):.6g} |\n"
                    content += f"| 95th percentile | {q.get('p95', 0):.6g} |\n"
                    content += f"| Maximum | {q.get('maximum', 0):.6g} |\n"
                    content += f"| Range | {q.get('range', 0):.6g} |\n"
                    content += f"| IQR | {q.get('iqr', 0):.6g} |\n\n"

                    content += "#### Descriptive Statistics\n\n"
                    content += "| Statistic | Value |\n|-----------|-------|\n"
                    d = s.get("descriptive", {})
                    content += f"| Mean | {d.get('mean', 0):.6g} |\n"
                    content += f"| Std deviation | {d.get('standard_deviation', 0):.6g} |\n"
                    content += f"| Variance | {d.get('variance', 0):.6g} |\n"
                    cv = d.get("coefficient_of_variation")
                    content += f"| CV | {f'{cv:.6g}' if cv else 'N/A'} |\n"
                    content += f"| Skewness | {d.get('skewness', 0):.6g} |\n"
                    content += f"| Kurtosis | {d.get('kurtosis', 0):.6g} |\n"
                    content += f"| MAD | {d.get('mad', 0):.6g} |\n"
                    content += f"| Sum | {d.get('sum', 0):.6g} |\n"
                    content += f"| Monotonicity | {d.get('monotonicity', 'N/A').capitalize()} |\n\n"

                elif stats.get("overview"):
                    ov = stats["overview"]
                    if ov.get("characters_and_unicode"):
                        cu = ov["characters_and_unicode"]
                        content += "#### Character Statistics\n\n"
                        content += "| Statistic | Value |\n|-----------|-------|\n"
                        content += f"| Total characters | {cu.get('total_characters', 0)} |\n"
                        content += f"| Distinct characters | {cu.get('distinct_characters', 0)} |\n"
                        content += f"| Distinct categories | {cu.get('distinct_categories', 0)} |\n\n"

                if "common_values" in stats and stats["common_values"]:
                    content += "#### Common Values\n\n"
                    content += "| Value | Count | % |\n|-------|------:|----:|\n"
                    cv = stats["common_values"]
                    if isinstance(cv, dict):
                        for val, metrics in list(cv.items())[:10]:
                            content += f"| {val} | {metrics['count']} | {metrics['percentage']:.1f}% |\n"
                    content += "\n"

                if "extreme_values" in stats and stats["extreme_values"]:
                    content += "#### Extreme Values\n\n"
                    ev = stats["extreme_values"]
                    if "minimum_10" in ev:
                        content += f"**Minimum 10:** `{', '.join(f'{v:.4g}' for v in ev['minimum_10'])}`\n\n"
                    if "maximum_10" in ev:
                        content += f"**Maximum 10:** `{', '.join(f'{v:.4g}' for v in ev['maximum_10'])}`\n\n"

                if cat == "Numeric":
                    content += "#### Value Counts\n\n"
                    content += "| Type | Count | % |\n|------|------:|----:|\n"
                    content += f"| Zeros | {stats.get('zeros_count', 0)} | {stats.get('zeros_percentage', 0):.1f}% |\n"
                    content += f"| Negative | {stats.get('negative_count', 0)} | {stats.get('negative_percentage', 0):.1f}% |\n"
                    content += f"| Infinite | {stats.get('infinite_count', 0)} | {stats.get('infinite_percentage', 0):.1f}% |\n\n"

                if "plots" in stats and stats["plots"] and img_dir:
                    content += "#### Visualizations\n\n"
                    for plot_name, plot_data in stats["plots"].items():
                        img_filename = f"{col}_{plot_name}.png".replace(" ", "_").replace("/", "-")
                        img_path = os.path.join(img_dir, img_filename)
                        try:
                            with open(img_path, "wb") as img_f:
                                img_f.write(base64.b64decode(plot_data))
                            rel_path = os.path.join(f"{report_name}_images", img_filename)
                            content += f"![{plot_name}]({rel_path})\n\n"
                        except Exception:
                            content += f"*(Error saving plot {plot_name})*\n\n"

                content += "---\n\n"

            # Correlations
            content += "## Correlations\n\n"
            num_corr = summary["summaries"].get("numeric_correlations", {})
            if "pearson" in num_corr:
                content += "### Numeric (Pearson - Top pairs)\n\n"
                if "plots" in num_corr and num_corr["plots"] and img_dir:
                    for method, plot_data in num_corr["plots"].items():
                        img_filename = f"correlation_{method}.png"
                        img_path = os.path.join(img_dir, img_filename)
                        try:
                            with open(img_path, "wb") as img_f:
                                img_f.write(base64.b64decode(plot_data))
                            rel_path = os.path.join(f"{report_name}_images", img_filename)
                            content += f"![{method} Correlation]({rel_path})\n\n"
                        except Exception:
                            pass

                pairs = []
                for c1, corrs in num_corr["pearson"].items():
                    for c2, val in corrs.items():
                        if c1 < c2:
                            pairs.append((c1, c2, val))
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)

                content += "| Feature 1 | Feature 2 | Correlation |\n|---|---|---|\n"
                for c1, c2, val in pairs[:10]:
                    content += f"| {c1} | {c2} | {val:.3f} |\n"
                content += "\n"

            content += "### Categorical (Cramer's V)\n\n| Pair | Value |\n|---|---|\n"
            cat_corrs = summary["summaries"].get("categorical_correlations", {})
            for pair, val in sorted(cat_corrs.items(), key=lambda x: x[1], reverse=True)[:10]:
                content += f"| {pair} | {val:.2f} |\n"

            # Missing Values
            content += "\n## Missing Values\n\n| Column | Count | Percentage |\n|--------|-------|------------|\n"
            missing_stats = summary["summaries"].get("missing_values", {})
            for col, count in missing_stats.get("count", {}).items():
                pct = missing_stats.get("percentage", {}).get(col, 0)
                if count > 0:
                    content += f"| {col} | {count} | {pct:.2f}% |\n"

            # Dataset Preview
            content += "\n## Dataset Preview\n\n"
            content += "### Head (first 5 rows)\n\n"
            content += pd.DataFrame(summary["summaries"]["head"]).to_markdown(index=False) + "\n\n"
            content += "### Random Sample (10 rows)\n\n"
            content += pd.DataFrame(summary["summaries"]["sample"]).to_markdown(index=False) + "\n\n"
            content += "### Tail (last 5 rows)\n\n"
            content += pd.DataFrame(summary["summaries"]["tail"]).to_markdown(index=False) + "\n\n"

        content += "\n---\nGenerated by HashPrep\n"

        if output_file:
            with open(output_file, "w") as f:
                f.write(content)
        return content

    def _group_alerts_by_type(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """Group issues into display categories."""
        groups: Dict[str, List[Dict]] = {}
        for issue in issues:
            alert_type = self.ALERT_TYPE_MAPPING.get(issue["category"], "Other")
            if alert_type not in groups:
                groups[alert_type] = []
            groups[alert_type].append(issue)
        return groups
