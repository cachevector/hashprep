import pandas as pd
import json
import yaml
import hashprep
from datetime import datetime
import os
import base64

class MarkdownReport:
    def generate(self, summary, full=False, output_file=None):
        content = "# Dataset Quality Report\n\n"
        content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"HashPrep Version: {hashprep.__version__}\n\n"
        content += "## Executive Summary\n"
        content += f"- Total Issues: {summary['total_issues']}\n"
        content += f"- Critical Issues: {summary['critical_count']}\n"
        content += f"- Warnings: {summary['warning_count']}\n"
        content += f"- Rows: {summary['summaries']['dataset_info']['rows']}\n"
        content += f"- Columns: {summary['summaries']['dataset_info']['columns']}\n\n"
        content += "## Issues Overview\n\n"
        content += "| Category | Severity | Column | Description | Impact | Quick Fix |\n"
        content += "|----------|----------|--------|-------------|--------|-----------|\n"
        for issue in summary["issues"]:
            quick_fix_inline = issue["quick_fix"].replace("\n", " ").replace("- ", "• ")
            content += f"| {issue['category']} | {issue['severity']} | {issue['column']} | {issue['description']} | {issue['impact_score']} | {quick_fix_inline} |\n"
        
        if full:
            # Prepare image directory if needed
            img_dir = None
            if output_file:
                report_dir = os.path.dirname(output_file)
                report_name = os.path.splitext(os.path.basename(output_file))[0]
                img_dir = os.path.join(report_dir, f"{report_name}_images")
                os.makedirs(img_dir, exist_ok=True)

            content += "\n## Variable Analysis\n\n"
            for col, stats in summary['summaries']['variables'].items():
                content += f"### {col} ({stats.get('category', 'Unknown')})\n"
                content += f"- Missing: {stats.get('missing_count', 0)} ({stats.get('missing_percentage', 0)}%)\n"
                content += f"- Distinct: {stats.get('distinct_count', 0)}\n\n"
                
                # Render statistics (numeric/text/etc)
                details = stats.get('statistics') if stats.get('statistics') else stats.get('overview')
                if details:
                    content += "#### Statistics\n```yaml\n"
                    content += yaml.safe_dump(details, default_flow_style=False)
                    content += "\n```\n\n"
                
                # Render common values
                if 'common_values' in stats and stats['common_values']:
                    content += "#### Common Values\n"
                    content += "| Value | Count | Percentage |\n|---|---|---|\n"
                    # Handle different structures of common_values (dict vs list)
                    cv = stats['common_values']
                    if isinstance(cv, dict):
                        for val, metrics in list(cv.items())[:5]:
                            content += f"| {val} | {metrics['count']} | {metrics['percentage']:.1f}% |\n"
                    content += "\n"
                
                # Save and Link Plots
                if 'plots' in stats and stats['plots'] and img_dir:
                    content += "#### Visualizations\n"
                    for plot_name, plot_data in stats['plots'].items():
                        img_filename = f"{col}_{plot_name}.png".replace(" ", "_").replace("/", "-")
                        img_path = os.path.join(img_dir, img_filename)
                        
                        # Decode and save
                        try:
                            with open(img_path, "wb") as img_f:
                                img_f.write(base64.b64decode(plot_data))
                            
                            # Link relative to report
                            rel_path = os.path.join(f"{report_name}_images", img_filename)
                            content += f"![{plot_name}]({rel_path})\n\n"
                        except Exception:
                            content += f"*(Error saving plot {plot_name})*\n\n"

            content += "\n## Correlations\n\n"
            # Numeric
            num_corr = summary['summaries'].get('numeric_correlations', {})
            if 'pearson' in num_corr:
                content += "### Numeric (Pearson - Top pairs)\n\n"
                # Correlation Plots
                if 'plots' in num_corr and num_corr['plots'] and img_dir:
                     for method, plot_data in num_corr['plots'].items():
                        img_filename = f"correlation_{method}.png"
                        img_path = os.path.join(img_dir, img_filename)
                        try:
                            with open(img_path, "wb") as img_f:
                                img_f.write(base64.b64decode(plot_data))
                            rel_path = os.path.join(f"{report_name}_images", img_filename)
                            content += f"![{method} Correlation]({rel_path})\n\n"
                        except Exception:
                            pass
                # Flatten the dict to list pairs
                pairs = []
                for c1, corrs in num_corr['pearson'].items():
                    for c2, val in corrs.items():
                        if c1 < c2: # Avoid dupes
                            pairs.append((c1, c2, val))
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                
                content += "| Feature 1 | Feature 2 | Correlation |\n|---|---|---|\n"
                for c1, c2, val in pairs[:10]:
                     content += f"| {c1} | {c2} | {val:.3f} |\n"
                content += "\n"

            # Categorical
            content += "### Categorical (Cramer's V)\n\n| Pair | Value |\n|---|---|\n"
            cat_corrs = summary['summaries'].get('categorical_correlations', {})
            # Add table header
            for pair, val in sorted(cat_corrs.items(), key=lambda x: x[1], reverse=True)[:10]:
                content += f"| {pair} | {val:.2f} |\n"
            
            content += "\n## Missing Values\n\n| Column | Count | Percentage |\n|--------|-------|------------|\n"
            missing_stats = summary['summaries'].get('missing_values', {})
            for col, count in missing_stats.get('count', {}).items():
                pct = missing_stats.get('percentage', {}).get(col, 0)
                if count > 0:
                    content += f"| {col} | {count} | {pct} |\n"
            
            content += "\n## Dataset Preview\n\n"
            content += "### Head\n\n" + pd.DataFrame(summary['summaries']['head']).to_markdown(index=False) + "\n\n"

        content += "\n## Next Steps\n- Address critical issues by following fix suggestions\n- Generate Reproducible Code: Run `hashprep report <dataset> --with-code` to get a `fixes.py` script\n- Refine Dataset: Apply suggested transformations and re-analyze\n\n---\nGenerated by HashPrep"
        
        if output_file:
            with open(output_file, "w") as f:
                f.write(content)
        return content