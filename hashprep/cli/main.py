# cli/main.py
import click
import pandas as pd
from datetime import datetime
import json
import os
import yaml
from hashprep.analyzer import DatasetAnalyzer  # If needed for typing

@click.group()
def cli():
    pass

@cli.command()
def version():
    click.echo("HashPrep Version: 1.0.0-MVP")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--critical-only', is_flag=True)
@click.option('--quiet', is_flag=True)
@click.option('--json', 'json_out', is_flag=True)
@click.option('--target', default=None, help='Target column for leakage and imbalance checks')
def scan(file_path, critical_only, quiet, json_out, target):
    df = pd.read_csv(file_path)
    analyzer = DatasetAnalyzer(df, target_col=target)
    summary = analyzer.analyze()
    critical = [i for i in summary["issues"] if i["severity"] == "critical"]
    warnings = [i for i in summary["issues"] if i["severity"] == "warning"]
    health_score = max(0, 100 - 10 * len(critical) - 2 * len(warnings))
    if critical_only:
        click.echo(click.style("🚨 CRITICAL ISSUES ONLY:", fg='red'))
        for i, issue in enumerate(critical, 1):
            click.echo(f"{i}. {issue['description']}")
        click.echo("Fix these before training your model!")
        return
    if quiet:
        click.echo(f"CRITICAL: {len(critical)}, WARNINGS: {len(warnings)}, HEALTH: {health_score}")
        return
    if json_out:
        json_data = {
            "health_score": health_score,
            "critical_issues": len(critical),
            "warnings": len(warnings),
            "issues": [{"type": i["severity"], **i} for i in summary["issues"]],
            "recommendations": [i["quick_fix"] for i in summary["issues"]]
        }
        click.echo(json.dumps(json_data))
        return
    click.echo("┌─────────────────────────────────────────────────────────┐")
    click.echo("│                 📊 DATASET HEALTH CHECK                 │")
    click.echo("├─────────────────────────────────────────────────────────┤")
    click.echo(f"│ File: {file_path}                                       │")
    click.echo(f"│ Size: {summary['summaries']['dataset_info']['rows']} rows × {summary['summaries']['dataset_info']['columns']} columns │")
    click.echo(f"│ Health Score: {health_score}/100 ⚠️                     │")
    click.echo("├─────────────────────────────────────────────────────────┤")
    click.echo(f"│ 🚨 CRITICAL ISSUES ({len(critical)}):                   │")
    for issue in critical:
        click.echo(f"│ • {issue['description']}                                │")
    click.echo("├─────────────────────────────────────────────────────────┤")
    click.echo(f"│ ⚠️ WARNINGS ({len(warnings)}):                          │")
    for issue in warnings:
        click.echo(f"│ • {issue['description']}                                │")
    click.echo("├─────────────────────────────────────────────────────────┤")
    click.echo("│ 💡 Next steps:                                          │")
    click.echo(f"│ • Run: hashprep details {file_path}                     │")
    click.echo(f"│ • Run: hashprep report {file_path}                      │")
    click.echo("└─────────────────────────────────────────────────────────┘")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--target', default=None)
def details(file_path, target):
    df = pd.read_csv(file_path)
    analyzer = DatasetAnalyzer(df, target_col=target)
    summary = analyzer.analyze()
    critical = [i for i in summary["issues"] if i["severity"] == "critical"]
    warnings = [i for i in summary["issues"] if i["severity"] == "warning"]
    click.echo(f"📋 DETAILED ANALYSIS: {file_path}")
    click.echo("\n🚨 CRITICAL ISSUES:")
    for i, issue in enumerate(critical, 1):
        click.echo(click.style(f"{i}. {issue['category'].upper()} - '{issue['column']}' column", fg='red'))
        click.echo(f"   └─ Why it's critical: {issue['description']}")
        click.echo(f"   └─ Impact: {issue['impact_score'].capitalize()}")
        click.echo(f"   └─ Quick fix: {issue['quick_fix']}")
        click.echo(f"   └─ Code: df = df.drop(columns=['{issue['column']}'])")
    click.echo("\n⚠️ WARNINGS:")
    for i, issue in enumerate(warnings, 1):
        click.echo(click.style(f"{i}. {issue['category'].upper()}", fg='yellow'))
        click.echo(f"   └─ Description: {issue['description']}")
        click.echo(f"   └─ Impact: {issue['impact_score'].capitalize()}")
        click.echo(f"   └─ Consider: {issue['quick_fix']}")
    click.echo("\nDATASET SUMMARY:")
    info = summary['summaries']['dataset_info']
    click.echo(f"├─ Rows: {info['rows']}")
    click.echo(f"├─ Columns: {info['columns']}")
    click.echo(f"├─ Memory usage: ~{info['memory_mb']} MB")
    click.echo(f"├─ Missing cells: {info['missing_cells']} ({info['missing_percentage']}%)")
    click.echo("├─ Variable Types:")
    for col, typ in summary['summaries']['variable_types'].items():
        click.echo(f"  │ {col}: {typ}")
    click.echo("├─ Missing Values (by column):")
    for col, pct in sorted(summary['summaries']['missing_values']['percentage'].items(), key=lambda x: x[1], reverse=True):
        if pct > 0:
            click.echo(f"  │ {col}: {pct}%")
    click.echo("├─ Reproduction Info:")
    repro = summary['summaries']['reproduction_info']
    click.echo(f"  │ Dataset Hash: {repro['dataset_hash']}")
    click.echo(f"  │ Analysis Timestamp: {repro['analysis_timestamp']}")
    click.echo("└─ Estimated cleaning time: 15-30 minutes")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--with-code', is_flag=True)
@click.option('--full', is_flag=True, help='Include full summaries, previews, variables, and correlations in report')
@click.option('--target', default=None)
def report(file_path, with_code, full, target):
    df = pd.read_csv(file_path)
    analyzer = DatasetAnalyzer(df, target_col=target)
    summary = analyzer.analyze()
    critical = [i for i in summary["issues"] if i["severity"] == "critical"]
    warnings = [i for i in summary["issues"] if i["severity"] == "warning"]
    health_score = max(0, 100 - 10 * len(critical) - 2 * len(warnings))
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    report_file = f"{base_name}_hashprep_report.md"
    with open(report_file, "w") as f:
        f.write("# Dataset Quality Report\n")
        f.write(f"**File:** {file_path}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("**HashPrep Version:** 1.0.0-MVP\n\n")
        f.write("## Summary\n")
        f.write(f"- **Health Score:** {health_score}/100\n")
        f.write(f"- **Critical Issues:** {len(critical)}\n")
        f.write(f"- **Warnings:** {len(warnings)}\n")
        f.write(f"- **Rows:** {summary['summaries']['dataset_info']['rows']}\n")
        f.write(f"- **Columns:** {summary['summaries']['dataset_info']['columns']}\n\n")
        f.write("## Critical Issues\n\n")
        for i, issue in enumerate(critical, 1):
            f.write(f"### {i}. {issue['category'].replace('_', ' ').title()} - '{issue['column']}'\n")
            f.write(f"**Risk Level:** {issue['impact_score'].upper()}\n")
            f.write(f"**Description:** {issue['description']}\n")
            f.write(f"**Recommendation:** {issue['quick_fix']}\n")
            f.write("```python\n")
            if issue['category'] == 'duplicates':
                f.write("df = df.drop_duplicates()\n")
            else:
                f.write(f"df = df.drop(columns=['{issue['column']}'])\n")
            f.write("```\n\n")
        f.write("## Warnings\n\n")
        for i, issue in enumerate(warnings, 1):
            f.write(f"### {i}. {issue['category'].replace('_', ' ').title()}\n")
            f.write(f"- Description: {issue['description']}\n")
            f.write(f"- Impact: {issue['impact_score']}\n")
            f.write(f"- Consider: {issue['quick_fix']}\n\n")
        if full:
            f.write("## Dataset Preview\n\n")
            f.write("### Head\n```json\n" + json.dumps(summary['summaries']['head'], indent=2) + "\n```\n\n")
            f.write("### Tail\n```json\n" + json.dumps(summary['summaries']['tail'], indent=2) + "\n```\n\n")
            f.write("### Sample\n```json\n" + json.dumps(summary['summaries']['sample'], indent=2) + "\n```\n\n")
            f.write("## Variables\n\n")
            for col, stats in summary['summaries']['variables'].items():
                f.write(f"### {col}\n```yaml\n" + yaml.dump(stats, default_flow_style=False) + "```\n\n")
            f.write("## Interactions and Correlations\n\n")
            f.write("### Numeric Correlations (Pearson)\n```json\n" + json.dumps(summary['summaries'].get('numeric_correlations', {}).get('pearson', {}), indent=2) + "\n```\n\n")
            f.write("### Categorical Correlations (Cramer's V)\n```json\n" + json.dumps(summary['summaries'].get('categorical_correlations', {}), indent=2) + "\n```\n\n")
            f.write("### Mixed Correlations\n```json\n" + json.dumps(summary['summaries'].get('mixed_correlations', {}), indent=2) + "\n```\n\n")
            f.write("## Missing Values\n```json\n" + json.dumps(summary['summaries']['missing_values'], indent=2) + "\n```\n\n")
            f.write("## Missing Patterns\n```json\n" + json.dumps(summary['summaries']['missing_patterns'], indent=2) + "\n```\n\n")
        f.write("## Next Steps\n1. Address critical issues first\n2. Handle warnings\n3. Re-run analysis\n4. Validate splits\n\n")
        f.write("---\n*Generated by HashPrep MVP v1.0*")
    click.echo("📄 Generating dataset quality report...")
    click.echo(f"✅ Report saved to: {report_file}")
    click.echo(f"✅ Summary: {len(critical)} critical issues, {len(warnings)} warnings found")
    click.echo("✅ Estimated fix time: 15-30 minutes")
    if with_code:
        fixes_file = f"{base_name}_fixes.py"
        with open(fixes_file, "w") as f:
            f.write(f"# HashPrep Generated Fixes for {file_path}\n")
            f.write("import pandas as pd\n\n")
            f.write("def quick_fixes(df: pd.DataFrame) -> pd.DataFrame:\n")
            f.write('    """Apply fixes identified by HashPrep"""\n\n')
            for issue in summary["issues"]:
                f.write(f"    # {issue['severity'].upper()}: {issue['category']} - {issue['description']}\n")
                if issue['category'] in ['duplicates']:
                    f.write("    initial_rows = len(df)\n")
                    f.write("    df = df.drop_duplicates()\n")
                    f.write("    print(f'Removed {{initial_rows - len(df)}} duplicates')\n")
                elif issue['category'] in ['class_imbalance']:
                    f.write("    # TODO: Use SMOTE or class weights\n    pass\n")
                elif issue['category'] in ['outliers']:
                    f.write("    # TODO: Winsorize or remove outliers\n    pass\n")
                elif issue['category'] == 'feature_correlation':
                    cols = issue['column'].split(',')
                    f.write(f"    # Drop one: df = df.drop(columns=['{cols[0]}'])\n")
                else:
                    if issue['column'] != '__all__':
                        f.write(f"    df = df.drop(columns=['{issue['column']}'])\n")
                f.write("\n")
            f.write("    return df\n\n")
            f.write("# Usage:\n")
            f.write(f"# df = pd.read_csv('{file_path}')\n")
            f.write("# df_cleaned = quick_fixes(df)\n")
            f.write("# df_cleaned.to_csv('cleaned_{file_path}', index=False)\n")
        click.echo(f"📄 Fixes script saved to: {fixes_file}")

if __name__ == "__main__":
    cli()