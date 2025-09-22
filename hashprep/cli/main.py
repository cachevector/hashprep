import click
import pandas as pd
from datetime import datetime
import json
import os
import yaml
from hashprep.analyzer import DatasetAnalyzer

@click.group()
def cli():
    pass

@cli.command()
def version():
    click.echo("HashPrep Version: 1.0.0-MVP")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--critical-only', is_flag=True, help='Show only critical issues')
@click.option('--quiet', is_flag=True, help='Show minimal output')
@click.option('--json', 'json_out', is_flag=True, help='Output in JSON format')
@click.option('--target', default=None, help='Target column for relevant checks')
@click.option('--checks', default=None, help='Comma-separated checks to run (e.g., feature_correlation,high_cardinality). Defaults to all: data_leakage,high_missing_values,empty_columns,single_value_columns,target_leakage,class_imbalance,high_cardinality,duplicates,mixed_data_types,outliers,feature_correlation,categorical_correlation,mixed_correlation,dataset_missingness,high_zero_counts,extreme_text_lengths,datetime_skew,missing_patterns')
def scan(file_path, critical_only, quiet, json_out, target, checks):
    df = pd.read_csv(file_path)
    selected_checks = checks.split(',') if checks else None
    # Validate checks
    valid_checks = [
        "data_leakage", "high_missing_values", "empty_columns", "single_value_columns",
        "target_leakage", "class_imbalance", "high_cardinality", "duplicates",
        "mixed_data_types", "outliers", "feature_correlation", "categorical_correlation",
        "mixed_correlation", "dataset_missingness", "high_zero_counts",
        "extreme_text_lengths", "datetime_skew", "missing_patterns"
    ]
    if selected_checks:
        invalid_checks = [c for c in selected_checks if c not in valid_checks]
        if invalid_checks:
            click.echo(f"Warning: Invalid checks ignored: {', '.join(invalid_checks)}")
            selected_checks = [c for c in selected_checks if c in valid_checks]
    analyzer = DatasetAnalyzer(df, target_col=target, selected_checks=selected_checks)
    summary = analyzer.analyze()
    issues = summary["issues"]
    critical = [i for i in issues if i["severity"] == "critical"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    if json_out:
        json_data = {
            "critical_issues": len(critical),
            "warnings": len(warnings),
            "issues": [{"type": i["severity"], **i} for i in issues],
            "recommendations": [i["quick_fix"] for i in issues]
        }
        click.echo(json.dumps(json_data))
        return
    if quiet:
        click.echo(f"CRITICAL: {len(critical)}, WARNINGS: {len(warnings)}")
        return
    click.echo(f"Dataset Health Check: {file_path}")
    click.echo(f"Size: {summary['summaries']['dataset_info']['rows']} rows x {summary['summaries']['dataset_info']['columns']} columns")
    if critical_only:
        click.echo("Critical Issues:")
        for i, issue in enumerate(critical, 1):
            click.echo(f"{i}. {issue['description']}")
        return
    click.echo("Critical Issues:")
    for issue in critical:
        click.echo(f"- {issue['description']}")
    click.echo("Warnings:")
    for issue in warnings:
        click.echo(f"- {issue['description']}")
    click.echo("Next steps: Run 'hashprep details' or 'hashprep report' for more info.")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--target', default=None, help='Target column for relevant checks')
@click.option('--checks', default=None, help='Comma-separated checks to run (e.g., feature_correlation,high_cardinality). Defaults to all: data_leakage,high_missing_values,empty_columns,single_value_columns,target_leakage,class_imbalance,high_cardinality,duplicates,mixed_data_types,outliers,feature_correlation,categorical_correlation,mixed_correlation,dataset_missingness,high_zero_counts,extreme_text_lengths,datetime_skew,missing_patterns')
def details(file_path, target, checks):
    df = pd.read_csv(file_path)
    selected_checks = checks.split(',') if checks else None
    valid_checks = [
        "data_leakage", "high_missing_values", "empty_columns", "single_value_columns",
        "target_leakage", "class_imbalance", "high_cardinality", "duplicates",
        "mixed_data_types", "outliers", "feature_correlation", "categorical_correlation",
        "mixed_correlation", "dataset_missingness", "high_zero_counts",
        "extreme_text_lengths", "datetime_skew", "missing_patterns"
    ]
    if selected_checks:
        invalid_checks = [c for c in selected_checks if c not in valid_checks]
        if invalid_checks:
            click.echo(f"Warning: Invalid checks ignored: {', '.join(invalid_checks)}")
            selected_checks = [c for c in selected_checks if c in valid_checks]
    analyzer = DatasetAnalyzer(df, target_col=target, selected_checks=selected_checks)
    summary = analyzer.analyze()
    issues = summary["issues"]
    critical = [i for i in issues if i["severity"] == "critical"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    click.echo(f"Detailed Analysis: {file_path}")
    click.echo("\nCritical Issues:")
    for i, issue in enumerate(critical, 1):
        click.echo(f"{i}. {issue['category'].upper()} - '{issue['column']}'")
        click.echo(f"   Description: {issue['description']}")
        click.echo(f"   Impact: {issue['impact_score'].capitalize()}")
        click.echo(f"   Quick fix: {issue['quick_fix']}")
    click.echo("\nWarnings:")
    for i, issue in enumerate(warnings, 1):
        click.echo(f"{i}. {issue['category'].upper()}")
        click.echo(f"   Description: {issue['description']}")
        click.echo(f"   Impact: {issue['impact_score'].capitalize()}")
        click.echo(f"   Quick fix: {issue['quick_fix']}")
    click.echo("\nDataset Summary:")
    info = summary['summaries']['dataset_info']
    click.echo(f"- Rows: {info['rows']}")
    click.echo(f"- Columns: {info['columns']}")
    click.echo(f"- Memory: ~{info['memory_mb']} MB")
    click.echo(f"- Missing: {info['missing_cells']} ({info['missing_percentage']}%)")
    click.echo("- Variable Types:")
    for col, typ in summary['summaries']['variable_types'].items():
        click.echo(f"  {col}: {typ}")
    click.echo("- Missing Values (by column):")
    for col, pct in sorted(summary['summaries']['missing_values']['percentage'].items(), key=lambda x: x[1], reverse=True):
        if pct > 0:
            click.echo(f"  {col}: {pct}%")
    repro = summary['summaries']['reproduction_info']
    click.echo(f"- Dataset Hash: {repro['dataset_hash']}")
    click.echo(f"- Analysis Time: {repro['analysis_timestamp']}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--with-code', is_flag=True, help='Generate fixes.py script')
@click.option('--full', is_flag=True, help='Include full summaries in report')
@click.option('--json', 'json_out', is_flag=True, help='Output report in JSON instead of Markdown')
@click.option('--target', default=None, help='Target column for relevant checks')
@click.option('--checks', default=None, help='Comma-separated checks to run (e.g., feature_correlation,high_cardinality). Defaults to all: data_leakage,high_missing_values,empty_columns,single_value_columns,target_leakage,class_imbalance,high_cardinality,duplicates,mixed_data_types,outliers,feature_correlation,categorical_correlation,mixed_correlation,dataset_missingness,high_zero_counts,extreme_text_lengths,datetime_skew,missing_patterns')
def report(file_path, with_code, full, json_out, target, checks):
    df = pd.read_csv(file_path)
    selected_checks = checks.split(',') if checks else None
    valid_checks = [
        "data_leakage", "high_missing_values", "empty_columns", "single_value_columns",
        "target_leakage", "class_imbalance", "high_cardinality", "duplicates",
        "mixed_data_types", "outliers", "feature_correlation", "categorical_correlation",
        "mixed_correlation", "dataset_missingness", "high_zero_counts",
        "extreme_text_lengths", "datetime_skew", "missing_patterns"
    ]
    if selected_checks:
        invalid_checks = [c for c in selected_checks if c not in valid_checks]
        if invalid_checks:
            click.echo(f"Warning: Invalid checks ignored: {', '.join(invalid_checks)}")
            selected_checks = [c for c in selected_checks if c in valid_checks]
    analyzer = DatasetAnalyzer(df, target_col=target, selected_checks=selected_checks)
    summary = analyzer.analyze()
    issues = summary["issues"]
    critical = [i for i in issues if i["severity"] == "critical"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    if json_out:
        report_file = f"{base_name}_hashprep_report.json"
        with open(report_file, "w") as f:
            json.dump(summary, f, indent=2)
        click.echo(f"Report saved to: {report_file}")
        return
    report_file = f"{base_name}_hashprep_report.md"
    with open(report_file, "w") as f:
        f.write("# Dataset Quality Report\n\n")
        f.write(f"File: {file_path}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("HashPrep Version: 1.0.0-MVP\n\n")
        f.write("## Executive Summary\n")
        f.write(f"- Critical Issues: {len(critical)}\n")
        f.write(f"- Warnings: {len(warnings)}\n")
        f.write(f"- Rows: {summary['summaries']['dataset_info']['rows']}\n")
        f.write(f"- Columns: {summary['summaries']['dataset_info']['columns']}\n\n")
        f.write("## Issues Overview\n\n")
        f.write("| Category | Severity | Column | Description | Impact | Quick Fix |\n")
        f.write("|----------|----------|--------|-------------|--------|-----------|\n")
        for issue in issues:
            # Inline quick_fix by replacing newlines with spaces and escaping bullets
            quick_fix_inline = issue['quick_fix'].replace('\n', ' ').replace('- ', '• ')
            f.write(f"| {issue['category']} | {issue['severity']} | {issue['column']} | {issue['description']} | {issue['impact_score']} | {quick_fix_inline} |\n")
        if full:
            f.write("\n## Dataset Preview\n\n")
            f.write("### Head\n\n" + pd.DataFrame(summary['summaries']['head']).to_markdown(index=False) + "\n\n")
            f.write("### Tail\n\n" + pd.DataFrame(summary['summaries']['tail']).to_markdown(index=False) + "\n\n")
            f.write("### Sample\n\n" + pd.DataFrame(summary['summaries']['sample']).to_markdown(index=False) + "\n\n")
            f.write("## Variables\n\n")
            for col, stats in summary['summaries']['variables'].items():
                f.write(f"### {col}\n\n```yaml\n{yaml.dump(stats)}\n```\n")
            f.write("## Correlations\n\n")
            f.write("### Numeric (Pearson)\n\n```json\n{json.dumps(summary['summaries'].get('numeric_correlations', {}).get('pearson', {}), indent=2)}\n```\n")
            f.write("### Categorical (Cramer's V)\n\n| Pair | Value |\n|------|-------|\n")
            for pair, val in summary['summaries'].get('categorical_correlations', {}).items():
                f.write(f"| {pair} | {val:.2f} |\n")
            f.write("\n### Mixed\n\n| Pair | F-Stat | P-Value |\n|------|--------|---------|\n")
            for pair, stats in summary['summaries'].get('mixed_correlations', {}).items():
                if "error" not in stats:
                    f.write(f"| {pair} | {stats['f_stat']:.2f} | {stats['p_value']:.4f} |\n")
            f.write("\n## Missing Values\n\n| Column | Count | Percentage |\n|--------|-------|------------|\n")
            for col in summary['summaries']['missing_values']['count']:
                count = summary['summaries']['missing_values']['count'][col]
                pct = summary['summaries']['missing_values']['percentage'][col]
                if count > 0:
                    f.write(f"| {col} | {count} | {pct} |\n")
            f.write("\n## Missing Patterns\n\n```json\n{json.dumps(summary['summaries']['missing_patterns'], indent=2)}\n```\n")
        f.write("\n## Next Steps\n- Address critical issues\n- Handle warnings\n- Re-analyze dataset\n\n---\nGenerated by HashPrep")
    click.echo(f"Report saved to: {report_file}")
    click.echo(f"Summary: {len(critical)} critical, {len(warnings)} warnings")
    if with_code:
        fixes_file = f"{base_name}_fixes.py"
        with open(fixes_file, "w") as f:
            f.write(f"# Fixes for {file_path}\n")
            f.write("import pandas as pd\n\n")
            f.write("def apply_fixes(df):\n")
            for issue in issues:
                f.write(f"# {issue['description']}\n")
                if 'drop' in issue['quick_fix'].lower() and issue['column'] != '__all__':
                    f.write(f"df = df.drop(columns=['{issue['column']}'])\n")
                elif issue['category'] == 'duplicates':
                    f.write("df = df.drop_duplicates()\n")
                elif issue['category'] == 'class_imbalance':
                    f.write("# Use resampling or weights\npass\n")
                elif issue['category'] == 'outliers':
                    f.write("# Winsorize or transform\npass\n")
                elif 'correlation' in issue['category']:
                    cols = issue['column'].split(',')
                    f.write(f"# Drop one: df = df.drop(columns=['{cols[1]}'])\n")
                elif issue['category'] == 'high_missing_values':
                    f.write(f"# Impute or drop: df['{issue['column']}'] = df['{issue['column']}'].fillna(method='ffill')\n")
                else:
                    f.write("# Manual fix needed\npass\n")
            f.write("return df\n")
        click.echo(f"Fixes script saved to: {fixes_file}")

if __name__ == "__main__":
    cli()