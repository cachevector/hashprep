import json
import os

import click
import fuzzybunny
import numpy as np
import pandas as pd

import hashprep
from hashprep import DatasetAnalyzer
from hashprep.checks.core import Issue
from hashprep.preparers.codegen import CodeGenerator
from hashprep.preparers.pipeline_builder import PipelineBuilder
from hashprep.preparers.suggestions import SuggestionProvider
from hashprep.reports import generate_report
from hashprep.utils.sampling import SamplingConfig


def json_numpy_handler(obj):
    """Custom JSON encoder to handle numpy types."""
    if hasattr(obj, "tolist"):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def suggest_check_names(invalid_check, valid_checks, cutoff=0.4):
    """Suggest similar check names for an invalid check using fuzzybunny."""
    # Use fuzzybunny to find the top 3 most similar check names
    results = fuzzybunny.rank(
        invalid_check,
        valid_checks,
        scorer='levenshtein',
        threshold=cutoff,
        top_n=3
    )
    # Extract just the matched strings from the results
    suggestions = [match[0] for match in results]
    return suggestions


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
    help=f"Comma-separated checks to run. Defaults to all: {','.join(DatasetAnalyzer.ALL_CHECKS)}",
)
@click.option(
    "--comparison",
    type=click.Path(exists=True),
    default=None,
    help="Comparison dataset for drift detection",
)
@click.option(
    "--sample-size",
    type=int,
    default=None,
    help="Max rows for sampling (default: 100000)",
)
@click.option("--no-sample", is_flag=True, help="Disable automatic sampling")
def scan(
    file_path, critical_only, quiet, json_out, target, checks, comparison, sample_size, no_sample
):
    df = pd.read_csv(file_path)
    comparison_df = pd.read_csv(comparison) if comparison else None

    selected_checks = checks.split(",") if checks else None
    valid_checks = DatasetAnalyzer.ALL_CHECKS
    if selected_checks:
        invalid_checks = [c for c in selected_checks if c not in valid_checks]
        if invalid_checks:
            click.echo(f"Warning: Invalid checks ignored: {', '.join(invalid_checks)}")
            for invalid in invalid_checks:
                suggestions = suggest_check_names(invalid, valid_checks)
                if suggestions:
                    click.echo(f"  Did you mean: {', '.join(suggestions)}?")
            selected_checks = [c for c in selected_checks if c in valid_checks]

    sampling_config = None
    if not no_sample and sample_size:
        sampling_config = SamplingConfig(max_rows=sample_size)

    analyzer = DatasetAnalyzer(
        df,
        target_col=target,
        selected_checks=selected_checks,
        comparison_df=comparison_df,
        sampling_config=sampling_config,
        auto_sample=not no_sample,
    )
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
        if "sampling_info" in summary:
            json_data["sampling_info"] = summary["sampling_info"]
        click.echo(json.dumps(json_data, default=json_numpy_handler))
        return

    if quiet:
        click.echo(f"CRITICAL ISSUES: {len(critical)}, WARNINGS: {len(warnings)}")
        return

    click.echo(f"Dataset Health Check: {file_path}")
    click.echo(
        f"Size: {summary['summaries']['dataset_info']['rows']} rows x {summary['summaries']['dataset_info']['columns']} columns"
    )

    if "sampling_info" in summary and summary["sampling_info"].get("was_sampled"):
        info = summary["sampling_info"]
        click.echo(
            f"Sampled: {info['sample_fraction']*100:.1f}% of {info['original_rows']} rows"
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
    help=f"Comma-separated checks to run. Defaults to all: {','.join(DatasetAnalyzer.ALL_CHECKS)}",
)
@click.option(
    "--comparison",
    type=click.Path(exists=True),
    default=None,
    help="Comparison dataset for drift detection",
)
@click.option(
    "--sample-size",
    type=int,
    default=None,
    help="Max rows for sampling (default: 100000)",
)
@click.option("--no-sample", is_flag=True, help="Disable automatic sampling")
def details(file_path, target, checks, comparison, sample_size, no_sample):
    df = pd.read_csv(file_path)
    comparison_df = pd.read_csv(comparison) if comparison else None

    selected_checks = checks.split(",") if checks else None
    valid_checks = DatasetAnalyzer.ALL_CHECKS
    if selected_checks:
        invalid_checks = [c for c in selected_checks if c not in valid_checks]
        if invalid_checks:
            click.echo(f"Warning: Invalid checks ignored: {', '.join(invalid_checks)}")
            for invalid in invalid_checks:
                suggestions = suggest_check_names(invalid, valid_checks)
                if suggestions:
                    click.echo(f"  Did you mean: {', '.join(suggestions)}?")
            selected_checks = [c for c in selected_checks if c in valid_checks]

    sampling_config = None
    if not no_sample and sample_size:
        sampling_config = SamplingConfig(max_rows=sample_size)

    analyzer = DatasetAnalyzer(
        df,
        target_col=target,
        selected_checks=selected_checks,
        comparison_df=comparison_df,
        sampling_config=sampling_config,
        auto_sample=not no_sample,
    )
    summary = analyzer.analyze()

    issues = summary["issues"]
    critical = [i for i in issues if i["severity"] == "critical"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    click.echo(f"Detailed Analysis: {file_path}")

    if "sampling_info" in summary and summary["sampling_info"].get("was_sampled"):
        info = summary["sampling_info"]
        click.echo(
            f"Note: Analysis performed on {info['sample_fraction']*100:.1f}% sample ({int(info['original_rows'] * info['sample_fraction'])} of {info['original_rows']} rows)"
        )

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
    click.echo(f"- Missing: {info['missing_cells']} ({info['missing_percentage']} %)")
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
    if "analysis_started" in repro and repro["analysis_started"]:
        click.echo(f"- Analysis Started: {repro['analysis_started'][:19]}")
    if "duration_seconds" in repro:
        click.echo(f"- Duration: {repro['duration_seconds']} seconds")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--with-code", is_flag=True, help="Generate fixes.py and pipeline.py scripts")
@click.option(
    "--full/--no-full", default=True, help="Include full summaries in report (default: True)"
)
@click.option("--format", default="md", help="Report format: md, json, html, pdf")
@click.option("--theme", default="minimal", help="HTML report theme: minimal, neubrutalism")
@click.option("--target", default=None, help="Target column for relevant checks")
@click.option(
    "--checks",
    default=None,
    help=f"Comma-separated checks to run. Defaults to all: {','.join(DatasetAnalyzer.ALL_CHECKS)}",
)
@click.option(
    "--visualizations/--no-visualizations",
    default=True,
    help="Include plots in report (default: True)",
)
@click.option(
    "--comparison",
    type=click.Path(exists=True),
    default=None,
    help="Comparison dataset for drift detection",
)
@click.option(
    "--sample-size",
    type=int,
    default=None,
    help="Max rows for sampling (default: 100000)",
)
@click.option("--no-sample", is_flag=True, help="Disable automatic sampling")
def report(
    file_path,
    with_code,
    full,
    format,
    theme,
    target,
    checks,
    visualizations,
    comparison,
    sample_size,
    no_sample,
):
    df = pd.read_csv(file_path)
    comparison_df = pd.read_csv(comparison) if comparison else None

    selected_checks = checks.split(",") if checks else None
    valid_checks = DatasetAnalyzer.ALL_CHECKS
    if selected_checks:
        invalid_checks = [c for c in selected_checks if c not in valid_checks]
        if invalid_checks:
            click.echo(f"Warning: Invalid checks ignored: {', '.join(invalid_checks)}")
            for invalid in invalid_checks:
                suggestions = suggest_check_names(invalid, valid_checks)
                if suggestions:
                    click.echo(f"  Did you mean: {', '.join(suggestions)}?")
            selected_checks = [c for c in selected_checks if c in valid_checks]

    sampling_config = None
    if not no_sample and sample_size:
        sampling_config = SamplingConfig(max_rows=sample_size)

    analyzer = DatasetAnalyzer(
        df,
        target_col=target,
        selected_checks=selected_checks,
        include_plots=visualizations,
        comparison_df=comparison_df,
        sampling_config=sampling_config,
        auto_sample=not no_sample,
    )
    summary = analyzer.analyze()

    base_name = os.path.splitext(os.path.basename(file_path))[0] + "_hashprep_report"
    report_dir = "examples/reports/"
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"{base_name}.{format}")

    generate_report(
        summary,
        format=format,
        full=full,
        output_file=report_file,
        theme=theme,
    )
    click.echo(f"Report saved to: {report_file}")
    click.echo(
        f"Summary: {summary['critical_count']} critical, {summary['warning_count']} warnings"
    )

    if "sampling_info" in summary and summary["sampling_info"].get("was_sampled"):
        info = summary["sampling_info"]
        click.echo(
            f"Note: Analysis performed on {info['sample_fraction']*100:.1f}% sample"
        )

    if with_code:
        issues = [Issue(**i) for i in summary["issues"]]
        column_types = summary.get("column_types", {})

        provider = SuggestionProvider(
            issues=issues,
            column_types=column_types,
            target_col=target,
        )
        suggestions = provider.get_suggestions()

        codegen = CodeGenerator(suggestions)
        fixes_file = os.path.join(report_dir, f"{base_name}_fixes.py")
        fixes_code = codegen.generate_pandas_script()
        with open(fixes_file, "w") as f:
            f.write(fixes_code)
        click.echo(f"Pandas fixes script saved to: {fixes_file}")

        builder = PipelineBuilder(suggestions)
        pipeline_file = os.path.join(report_dir, f"{base_name}_pipeline.py")
        pipeline_code = builder.generate_pipeline_code()
        with open(pipeline_file, "w") as f:
            f.write(pipeline_code)
        click.echo(f"sklearn pipeline script saved to: {pipeline_file}")


if __name__ == "__main__":
    cli()
