import click
import pandas as pd
from datetime import datetime
import json
import os
import yaml
import hashprep
from hashprep.analyzer import DatasetAnalyzer
import numpy as np
from hashprep.reports import generate_report

# from hashprep.fixes import generate_fixes_script


# Custom JSON encoder to handle numpy types
def json_numpy_handler(obj):
    if hasattr(obj, "tolist"):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


@click.group()
def cli():
    pass


@cli.command()
def version():
    click.echo(f"HashPrep Version: {hashprep.__version__}")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--critical-only", is_flag=True, help="Show only critical issues")
@click.option("--quiet", is_flag=True, help="Show minimal output")
@click.option("--json", "json_out", is_flag=True, help="Output in JSON format")
@click.option("--target", default=None, help="Target column for relevant checks")
@click.option(
    "--checks",
    default=None,
    help="Comma-separated checks to run (e.g., feature_correlation,high_cardinality). Defaults to all: data_leakage,high_missing_values,empty_columns,single_value_columns,target_leakage_patterns,class_imbalance,high_cardinality,duplicates,mixed_data_types,outliers,feature_correlation,categorical_correlation,mixed_correlation,dataset_missingness,high_zero_counts,extreme_text_lengths,datetime_skew,missing_patterns",
)
def scan(file_path, critical_only, quiet, json_out, target, checks):
    df = pd.read_csv(file_path)
    selected_checks = checks.split(",") if checks else None
    valid_checks = [
        "data_leakage",
        "high_missing_values",
        "empty_columns",
        "single_value_columns",
        "target_leakage_patterns",
        "class_imbalance",
        "high_cardinality",
        "duplicates",
        "mixed_data_types",
        "outliers",
        "feature_correlation",
        "categorical_correlation",
        "mixed_correlation",
        "dataset_missingness",
        "high_zero_counts",
        "extreme_text_lengths",
        "datetime_skew",
        "missing_patterns",
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
            "recommendations": [i["quick_fix"] for i in issues],
        }
        click.echo(json.dumps(json_data, default=json_numpy_handler))
        return
    if quiet:
        click.echo(f"CRITICAL ISSUES: {len(critical)}, WARNINGS: {len(warnings)}")
        return
    click.echo(f"Dataset Health Check: {file_path}")
    click.echo(
        f"Size: {summary['summaries']['dataset_info']['rows']} rows x {summary['summaries']['dataset_info']['columns']} columns"
    )
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
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--target", default=None, help="Target column for relevant checks")
@click.option(
    "--checks",
    default=None,
    help="Comma-separated checks to run (e.g., feature_correlation,high_cardinality). Defaults to all: data_leakage,high_missing_values,empty_columns,single_value_columns,target_leakage_patterns,class_imbalance,high_cardinality,duplicates,mixed_data_types,outliers,feature_correlation,categorical_correlation,mixed_correlation,dataset_missingness,high_zero_counts,extreme_text_lengths,datetime_skew,missing_patterns",
)
def details(file_path, target, checks):
    df = pd.read_csv(file_path)
    selected_checks = checks.split(",") if checks else None
    valid_checks = [
        "data_leakage",
        "high_missing_values",
        "empty_columns",
        "single_value_columns",
        "target_leakage_patterns",
        "class_imbalance",
        "high_cardinality",
        "duplicates",
        "mixed_data_types",
        "outliers",
        "feature_correlation",
        "categorical_correlation",
        "mixed_correlation",
        "dataset_missingness",
        "high_zero_counts",
        "extreme_text_lengths",
        "datetime_skew",
        "missing_patterns",
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
    info = summary["summaries"]["dataset_info"]
    click.echo(f"- Rows: {info['rows']}")
    click.echo(f"- Columns: {info['columns']}")
    click.echo(f"- Memory: ~{info['memory_mb']} MB")
    click.echo(f"- Missing: {info['missing_cells']} ({info['missing_percentage']}%)")
    click.echo("- Variable Types:")
    for col, typ in summary["summaries"]["variable_types"].items():
        click.echo(f"  {col}: {typ}")
    click.echo("- Missing Values (by column):")
    for col, pct in sorted(
        summary["summaries"]["missing_values"]["percentage"].items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        if pct > 0:
            click.echo(f"  {col}: {pct}%")
    repro = summary["summaries"]["reproduction_info"]
    click.echo(f"- Dataset Hash: {repro['dataset_hash']}")
    click.echo(f"- Analysis Time: {repro['analysis_timestamp']}")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--with-code", is_flag=True, help="Generate fixes.py script")
@click.option("--full", is_flag=True, help="Include full summaries in report")
@click.option("--format", default="md", help="Report format: md, json, html, pdf")
@click.option("--target", default=None, help="Target column for relevant checks")
@click.option(
    "--checks",
    default=None,
    help="Comma-separated checks to run (e.g., feature_correlation,high_cardinality). Defaults to all: data_leakage,high_missing_values,empty_columns,single_value_columns,target_leakage_patterns,class_imbalance,high_cardinality,duplicates,mixed_data_types,outliers,feature_correlation,categorical_correlation,mixed_correlation,dataset_missingness,high_zero_counts,extreme_text_lengths,datetime_skew,missing_patterns",
)
@click.option(
    "--include-plots",
    is_flag=True,
    help="Include plots in markdown, html, or pdf reports",
)
def report(file_path, with_code, full, format, target, checks, include_plots):
    df = pd.read_csv(file_path)
    selected_checks = checks.split(",") if checks else None
    valid_checks = [
        "data_leakage",
        "high_missing_values",
        "empty_columns",
        "single_value_columns",
        "target_leakage_patterns",
        "class_imbalance",
        "high_cardinality",
        "duplicates",
        "mixed_data_types",
        "outliers",
        "feature_correlation",
        "categorical_correlation",
        "mixed_correlation",
        "dataset_missingness",
        "high_zero_counts",
        "extreme_text_lengths",
        "datetime_skew",
        "missing_patterns",
    ]
    if selected_checks:
        invalid_checks = [c for c in selected_checks if c not in valid_checks]
        if invalid_checks:
            click.echo(f"Warning: Invalid checks ignored: {', '.join(invalid_checks)}")
            selected_checks = [c for c in selected_checks if c in valid_checks]
    analyzer = DatasetAnalyzer(
        df,
        target_col=target,
        selected_checks=selected_checks,
        include_plots=include_plots,
    )
    summary = analyzer.analyze()
    base_name = os.path.splitext(os.path.basename(file_path))[0] + "_hashprep_report"
    report_dir = "examples/reports/"
    os.makedirs(report_dir, exist_ok=True)  # create if it doesnt exist
    report_file = os.path.join(report_dir, f"{base_name}.{format}")
    generate_report(
        summary,
        format=format,
        full=full,
        output_file=report_file,
        include_plots=include_plots,
    )
    click.echo(f"Report saved to: {report_file}")
    click.echo(
        f"Summary: {summary['critical_count']} critical, {summary['warning_count']} warnings"
    )
    # if with_code:
    #     fixes_file = f"{base_name}_fixes.py"
    #     fixes_code = generate_fixes_script(summary['issues'], file_path)
    #     with open(fixes_file, "w") as f:
    #         f.write(fixes_code)
    #     click.echo(f"Fixes script saved to: {fixes_file}")


if __name__ == "__main__":
    cli()
