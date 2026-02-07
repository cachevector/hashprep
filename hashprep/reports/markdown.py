import base64
import os
from typing import Dict, List

import pandas as pd
import yaml

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
                content += f"### {col} ({stats.get('category', 'Unknown')})\n"
                content += f"- Missing: {stats.get('missing_count', 0)} ({stats.get('missing_percentage', 0)}%)\n"
                content += f"- Distinct: {stats.get('distinct_count', 0)}\n\n"

                details = stats.get("statistics") if stats.get("statistics") else stats.get("overview")
                if details:
                    content += "#### Statistics\n```yaml\n"
                    content += yaml.safe_dump(details, default_flow_style=False)
                    content += "```\n\n"

                if "common_values" in stats and stats["common_values"]:
                    content += "#### Common Values\n"
                    content += "| Value | Count | Percentage |\n|---|---|---|\n"
                    cv = stats["common_values"]
                    if isinstance(cv, dict):
                        for val, metrics in list(cv.items())[:5]:
                            content += f"| {val} | {metrics['count']} | {metrics['percentage']:.1f}% |\n"
                    content += "\n"

                if "plots" in stats and stats["plots"] and img_dir:
                    content += "#### Visualizations\n"
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
                    content += f"| {col} | {count} | {pct}% |\n"

            # Dataset Preview
            content += "\n## Dataset Preview\n\n"
            content += "### Head\n\n" + pd.DataFrame(summary["summaries"]["head"]).to_markdown(index=False) + "\n\n"

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
