from datetime import datetime

import pandas as pd
from jinja2 import Template
from weasyprint import HTML

import hashprep


class PdfReport:
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

    def generate(self, summary, full=False, output_file=None, **kwargs):
        template = Template(self._get_template())

        head_df = pd.DataFrame(summary["summaries"]["head"])
        tail_df = pd.DataFrame(summary["summaries"]["tail"])
        sample_df = pd.DataFrame(summary["summaries"]["sample"])

        dataset_info = summary["summaries"]["dataset_info"]
        reproduction_info = summary["summaries"].get("reproduction_info", {})
        variable_type_counts = summary["summaries"].get("variable_type_counts", {})

        alerts_by_type = self._group_alerts_by_type(summary["issues"])

        context = {
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "critical_count": summary["critical_count"],
            "warning_count": summary["warning_count"],
            "total_issues": summary["total_issues"],
            "rows": dataset_info["rows"],
            "columns": dataset_info["columns"],
            "missing_cells": dataset_info["missing_cells"],
            "missing_percentage": dataset_info["missing_percentage"],
            "duplicate_rows": dataset_info.get("duplicate_rows", 0),
            "duplicate_percentage": dataset_info.get("duplicate_percentage", 0),
            "memory_kib": dataset_info.get("memory_kib", 0),
            "average_record_size": dataset_info.get("average_record_size_bytes", 0),
            "variable_type_counts": variable_type_counts,
            "alerts_by_type": alerts_by_type,
            "analysis_started": reproduction_info.get("analysis_started", ""),
            "analysis_finished": reproduction_info.get("analysis_finished", ""),
            "duration_seconds": reproduction_info.get("duration_seconds", 0),
            "version": hashprep.__version__,
            "full": full,
            "head_table": head_df.to_html(index=False, border=0),
            "tail_table": tail_df.to_html(index=False, border=0),
            "sample_table": sample_df.to_html(index=False, border=0),
            "variables": summary["summaries"].get("variables", {}),
            "numeric_correlations": summary["summaries"].get("numeric_correlations", {}),
            "categorical_correlations": summary["summaries"].get("categorical_correlations", {}),
            "missing_values": summary["summaries"].get("missing_values", {}),
            "missing_plots": summary["summaries"].get("plots", {}),
        }

        html_content = template.render(context)
        pdf_content = HTML(string=html_content).write_pdf()
        if output_file:
            with open(output_file, "wb") as f:
                f.write(pdf_content)
        return pdf_content

    def _group_alerts_by_type(self, issues: list[dict]) -> dict[str, list[dict]]:
        groups: dict[str, list[dict]] = {}
        for issue in issues:
            alert_type = self.ALERT_TYPE_MAPPING.get(issue["category"], "Other")
            if alert_type not in groups:
                groups[alert_type] = []
            groups[alert_type].append(issue)
        return groups

    def _get_template(self):
        return """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {
        size: A4;
        margin: 1.5cm 2cm;
    }
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 9pt;
        color: #1a1a1a;
        line-height: 1.5;
    }
    h1 { font-size: 20pt; margin: 0 0 4pt 0; color: #111; }
    h2 { font-size: 14pt; margin: 20pt 0 8pt 0; color: #111; border-bottom: 2px solid #e5e7eb; padding-bottom: 4pt; }
    h3 { font-size: 11pt; margin: 14pt 0 6pt 0; color: #333; }
    h4 { font-size: 9pt; margin: 10pt 0 4pt 0; color: #555; text-transform: uppercase; letter-spacing: 0.5pt; }

    .header { margin-bottom: 16pt; }
    .header .version { font-size: 9pt; color: #888; }
    .header .badges { margin-top: 4pt; }
    .badge {
        display: inline-block;
        padding: 2pt 8pt;
        font-size: 8pt;
        font-weight: bold;
        border-radius: 3pt;
        margin-right: 4pt;
    }
    .badge-critical { background: #fee2e2; color: #b91c1c; }
    .badge-warning { background: #fef3c7; color: #b45309; }
    .badge-type { background: #eff6ff; color: #1d4ed8; }
    .badge-alert-unique { background: #fef3c7; color: #b45309; }
    .badge-alert-missing { background: #fee2e2; color: #dc2626; }

    /* Overview grid */
    .overview-grid {
        display: flex;
        gap: 16pt;
        margin-bottom: 12pt;
    }
    .overview-grid .panel {
        flex: 1;
        border: 1px solid #e5e7eb;
        border-radius: 4pt;
        padding: 10pt;
    }

    /* Stats table */
    .stats-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 8pt;
    }
    .stats-table td {
        padding: 3pt 6pt;
        border-bottom: 1px solid #f3f4f6;
        vertical-align: top;
    }
    .stats-table td:first-child { color: #6b7280; }
    .stats-table td:last-child { text-align: right; font-weight: 500; font-family: 'Courier New', monospace; font-size: 8.5pt; }

    /* Alerts */
    .alert-group { margin-bottom: 8pt; }
    .alert-group-title {
        font-size: 8pt;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5pt;
        color: #6b7280;
        padding: 3pt 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 4pt;
    }
    .alert-item {
        padding: 3pt 0 3pt 12pt;
        font-size: 8.5pt;
        position: relative;
    }
    .alert-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 8pt;
        width: 5pt;
        height: 5pt;
        border-radius: 50%;
    }
    .alert-critical::before { background: #dc2626; }
    .alert-warning::before { background: #f59e0b; }

    /* Variable cards */
    .var-card {
        border: 1px solid #e5e7eb;
        border-radius: 4pt;
        margin-bottom: 14pt;
        padding: 10pt;
    }
    .var-header {
        margin-bottom: 8pt;
        padding-bottom: 6pt;
        border-bottom: 1px solid #f3f4f6;
    }
    .var-name { font-size: 12pt; font-weight: bold; color: #111; display: inline; }

    /* Stat cards row */
    .stat-cards {
        display: flex;
        gap: 8pt;
        margin-bottom: 10pt;
    }
    .stat-card {
        flex: 1;
        background: #f9fafb;
        border-radius: 3pt;
        padding: 6pt 8pt;
    }
    .stat-card .label { font-size: 7pt; text-transform: uppercase; color: #6b7280; letter-spacing: 0.3pt; }
    .stat-card .value { font-size: 11pt; font-weight: bold; color: #111; }
    .stat-card .sub { font-size: 7pt; color: #9ca3af; }

    /* Variable content columns */
    .var-content {
        display: flex;
        gap: 12pt;
    }
    .var-content .col-stats { flex: 1; }
    .var-content .col-chart { width: 220pt; flex-shrink: 0; }
    .var-content .col-chart img { width: 100%; height: auto; }

    /* Detail sections */
    .var-details {
        display: flex;
        gap: 16pt;
        margin-top: 10pt;
        padding-top: 8pt;
        border-top: 1px solid #f3f4f6;
    }
    .var-details .detail-col { flex: 1; }

    /* Common values table */
    .cv-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 8.5pt;
    }
    .cv-table th {
        text-align: left;
        font-size: 7.5pt;
        text-transform: uppercase;
        color: #6b7280;
        border-bottom: 1px solid #e5e7eb;
        padding: 3pt 4pt;
    }
    .cv-table th:nth-child(2), .cv-table th:nth-child(3) { text-align: right; }
    .cv-table td {
        padding: 2pt 4pt;
        border-bottom: 1px solid #f3f4f6;
        font-family: 'Courier New', monospace;
        font-size: 8pt;
    }
    .cv-table td:nth-child(2), .cv-table td:nth-child(3) { text-align: right; }

    /* Extreme values */
    .extreme-val {
        display: inline-block;
        background: #eff6ff;
        color: #1d4ed8;
        padding: 1pt 4pt;
        border-radius: 2pt;
        font-size: 7.5pt;
        font-family: 'Courier New', monospace;
        margin: 1pt;
    }

    /* Correlation / Missing images */
    .plot-grid {
        display: flex;
        gap: 12pt;
        flex-wrap: wrap;
    }
    .plot-grid .plot-item { flex: 1; min-width: 200pt; text-align: center; }
    .plot-grid .plot-item img { width: 100%; height: auto; }
    .plot-grid .plot-item h4 { text-align: center; }

    /* Data tables */
    .data-table { width: 100%; border-collapse: collapse; font-size: 5.5pt; margin-bottom: 10pt; table-layout: fixed; }
    .data-table th { background: #f9fafb; padding: 2pt 3pt; text-align: left; font-weight: 600; border-bottom: 1.5px solid #e5e7eb; font-size: 5.5pt; word-wrap: break-word; }
    .data-table td { padding: 2pt 3pt; border-bottom: 1px solid #f3f4f6; word-wrap: break-word; overflow-wrap: break-word; font-size: 5.5pt; }

    /* Reproduction */
    .repro-grid {
        display: flex;
        gap: 16pt;
    }
    .repro-grid .repro-item { flex: 1; }
    .repro-grid .repro-item .label { font-size: 8pt; color: #6b7280; }
    .repro-grid .repro-item .value { font-family: 'Courier New', monospace; font-size: 9pt; }

    .footer { text-align: center; font-size: 8pt; color: #9ca3af; margin-top: 20pt; padding-top: 8pt; border-top: 1px solid #e5e7eb; }
</style>
</head>
<body>

<!-- Header -->
<div class="header">
    <h1>HashPrep Report</h1>
    <span class="version">v{{ version }}</span>
    <div class="badges">
        <span class="badge badge-critical">{{ critical_count }} Critical</span>
        <span class="badge badge-warning">{{ warning_count }} Warnings</span>
    </div>
</div>

<!-- Overview -->
<h2>Overview</h2>
<div class="overview-grid">
    <div class="panel">
        <h4>Dataset Statistics</h4>
        <table class="stats-table">
            <tr><td>Variables</td><td>{{ columns }}</td></tr>
            <tr><td>Observations</td><td>{{ rows }}</td></tr>
            <tr><td>Missing cells</td><td>{{ missing_cells }} ({{ missing_percentage }}%)</td></tr>
            <tr><td>Duplicate rows</td><td>{{ duplicate_rows }} ({{ duplicate_percentage }}%)</td></tr>
            <tr><td>Memory</td><td>{{ memory_kib }} KiB</td></tr>
            <tr><td>Avg record size</td><td>{{ average_record_size }} B</td></tr>
        </table>
    </div>
    <div class="panel">
        <h4>Variable Types</h4>
        <table class="stats-table">
            {% for type_name, count in variable_type_counts.items() %}
            {% if count > 0 %}
            <tr><td>{{ type_name }}</td><td>{{ count }}</td></tr>
            {% endif %}
            {% endfor %}
        </table>
    </div>
</div>

<!-- Alerts -->
<h2>Alerts</h2>
{% for alert_type, alerts in alerts_by_type.items() %}
<div class="alert-group">
    <div class="alert-group-title">{{ alert_type }}</div>
    {% for alert in alerts %}
    <div class="alert-item {% if alert.severity == 'critical' %}alert-critical{% else %}alert-warning{% endif %}">
        {{ alert.description }}
    </div>
    {% endfor %}
</div>
{% endfor %}

<!-- Reproduction -->
<h2>Reproduction</h2>
<div class="repro-grid">
    <div class="repro-item">
        <div class="label">Analysis started</div>
        <div class="value">{{ analysis_started[:19] if analysis_started else 'N/A' }}</div>
    </div>
    <div class="repro-item">
        <div class="label">Analysis finished</div>
        <div class="value">{{ analysis_finished[:19] if analysis_finished else 'N/A' }}</div>
    </div>
    <div class="repro-item">
        <div class="label">Duration</div>
        <div class="value">{{ duration_seconds }} seconds</div>
    </div>
    <div class="repro-item">
        <div class="label">Software version</div>
        <div class="value">hashprep v{{ version }}</div>
    </div>
</div>

{% if full %}
<!-- Variables -->
<h2>Variables</h2>
{% for col, stats in variables.items() %}
<div class="var-card">
    <div class="var-header">
        <span class="var-name">{{ col }}</span>
        <span class="badge badge-type">{{ stats.category }}</span>
        {% if stats.distinct_percentage >= 95 %}
        <span class="badge badge-alert-unique">Unique</span>
        {% endif %}
        {% if stats.missing_percentage > 0 %}
        <span class="badge badge-alert-missing">{{ "%.1f"|format(stats.missing_percentage) }}% missing</span>
        {% endif %}
    </div>

    <!-- Stat cards -->
    <div class="stat-cards">
        <div class="stat-card">
            <div class="label">Distinct</div>
            <div class="value">{{ stats.distinct_count }}</div>
            <div class="sub">{{ "%.1f"|format(stats.distinct_percentage) }}%</div>
        </div>
        <div class="stat-card">
            <div class="label">Missing</div>
            <div class="value">{{ stats.missing_count }}</div>
            <div class="sub">{{ "%.1f"|format(stats.missing_percentage) }}%</div>
        </div>
        {% if stats.category == 'Numeric' %}
        <div class="stat-card">
            <div class="label">Mean</div>
            <div class="value">{{ "%.4g"|format(stats.mean) if stats.mean is not none else 'N/A' }}</div>
        </div>
        <div class="stat-card">
            <div class="label">Range</div>
            <div class="value">{{ "%.4g"|format(stats.minimum) if stats.minimum is not none else '?' }} &ndash; {{ "%.4g"|format(stats.maximum) if stats.maximum is not none else '?' }}</div>
        </div>
        {% else %}
        <div class="stat-card">
            <div class="label">Memory</div>
            <div class="value">{{ "%.1f"|format(stats.memory_size / 1024) }} KiB</div>
        </div>
        <div class="stat-card">
            <div class="label">Length</div>
            {% if stats.overview and stats.overview.length %}
            <div class="value">{{ stats.overview.length.min_length }} &ndash; {{ stats.overview.length.max_length }}</div>
            <div class="sub">chars</div>
            {% else %}
            <div class="value">&ndash;</div>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <!-- Chart + Stats side by side -->
    <div class="var-content">
        <div class="col-stats">
            {% if stats.category == 'Numeric' and stats.statistics %}
            <h4>Quantile Statistics</h4>
            <table class="stats-table">
                <tr><td>Minimum</td><td>{{ "%.6g"|format(stats.statistics.quantiles.minimum) }}</td></tr>
                <tr><td>5th percentile</td><td>{{ "%.6g"|format(stats.statistics.quantiles.p5) }}</td></tr>
                <tr><td>Q1 (25%)</td><td>{{ "%.6g"|format(stats.statistics.quantiles.q1) }}</td></tr>
                <tr><td>Median (50%)</td><td>{{ "%.6g"|format(stats.statistics.quantiles.median) }}</td></tr>
                <tr><td>Q3 (75%)</td><td>{{ "%.6g"|format(stats.statistics.quantiles.q3) }}</td></tr>
                <tr><td>95th percentile</td><td>{{ "%.6g"|format(stats.statistics.quantiles.p95) }}</td></tr>
                <tr><td>Maximum</td><td>{{ "%.6g"|format(stats.statistics.quantiles.maximum) }}</td></tr>
                <tr><td>Range</td><td>{{ "%.6g"|format(stats.statistics.quantiles.range) }}</td></tr>
                <tr><td>IQR</td><td>{{ "%.6g"|format(stats.statistics.quantiles.iqr) }}</td></tr>
            </table>
            <h4>Descriptive Statistics</h4>
            <table class="stats-table">
                <tr><td>Mean</td><td>{{ "%.6g"|format(stats.statistics.descriptive.mean) }}</td></tr>
                <tr><td>Std deviation</td><td>{{ "%.6g"|format(stats.statistics.descriptive.standard_deviation) }}</td></tr>
                <tr><td>Variance</td><td>{{ "%.6g"|format(stats.statistics.descriptive.variance) }}</td></tr>
                <tr><td>CV</td><td>{{ "%.6g"|format(stats.statistics.descriptive.coefficient_of_variation) if stats.statistics.descriptive.coefficient_of_variation else 'N/A' }}</td></tr>
                <tr><td>Skewness</td><td>{{ "%.6g"|format(stats.statistics.descriptive.skewness) }}</td></tr>
                <tr><td>Kurtosis</td><td>{{ "%.6g"|format(stats.statistics.descriptive.kurtosis) }}</td></tr>
                <tr><td>MAD</td><td>{{ "%.6g"|format(stats.statistics.descriptive.mad) }}</td></tr>
                <tr><td>Sum</td><td>{{ "%.6g"|format(stats.statistics.descriptive.sum) }}</td></tr>
                <tr><td>Monotonicity</td><td>{{ stats.statistics.descriptive.monotonicity | capitalize }}</td></tr>
            </table>
            {% elif stats.overview %}
            <h4>Length Statistics</h4>
            <table class="stats-table">
                <tr><td>Min length</td><td>{{ stats.overview.length.min_length }}</td></tr>
                <tr><td>Max length</td><td>{{ stats.overview.length.max_length }}</td></tr>
                <tr><td>Mean length</td><td>{{ "%.2f"|format(stats.overview.length.mean_length) if stats.overview.length.mean_length else 'N/A' }}</td></tr>
                <tr><td>Median length</td><td>{{ "%.2f"|format(stats.overview.length.median_length) if stats.overview.length.median_length else 'N/A' }}</td></tr>
            </table>
            <h4>Character Statistics</h4>
            <table class="stats-table">
                <tr><td>Total characters</td><td>{{ stats.overview.characters_and_unicode.total_characters }}</td></tr>
                <tr><td>Distinct characters</td><td>{{ stats.overview.characters_and_unicode.distinct_characters }}</td></tr>
                <tr><td>Distinct categories</td><td>{{ stats.overview.characters_and_unicode.distinct_categories }}</td></tr>
            </table>
            {% endif %}
        </div>
        {% if stats.plots %}
        <div class="col-chart">
            {% if stats.plots.histogram %}
            <img src="data:image/png;base64,{{ stats.plots.histogram }}" />
            {% elif stats.plots.common_values_bar %}
            <img src="data:image/png;base64,{{ stats.plots.common_values_bar }}" />
            {% elif stats.plots.word_bar %}
            <img src="data:image/png;base64,{{ stats.plots.word_bar }}" />
            {% endif %}
        </div>
        {% endif %}
    </div>

    <!-- Common Values / Extreme Values / Value Counts -->
    <div class="var-details">
        <div class="detail-col">
            {% if stats.common_values or (stats.categories and stats.categories.common_values) %}
            <h4>Common Values</h4>
            <table class="cv-table">
                <thead><tr><th>Value</th><th>Count</th><th>%</th></tr></thead>
                <tbody>
                {% set cv = stats.common_values if stats.common_values else stats.categories.common_values %}
                {% for val, info in cv.items() %}
                <tr><td>{{ val }}</td><td>{{ info.count }}</td><td>{{ "%.1f"|format(info.percentage) }}%</td></tr>
                {% endfor %}
                </tbody>
            </table>
            {% endif %}
        </div>
        <div class="detail-col">
            {% if stats.extreme_values %}
            <h4>Extreme Values</h4>
            <div style="margin-bottom: 4pt;">
                <div style="font-size: 7pt; color: #6b7280; text-transform: uppercase; margin-bottom: 2pt;">Minimum</div>
                {% for val in stats.extreme_values.minimum_10 %}
                <span class="extreme-val">{{ "%.4g"|format(val) }}</span>
                {% endfor %}
            </div>
            <div>
                <div style="font-size: 7pt; color: #6b7280; text-transform: uppercase; margin-bottom: 2pt;">Maximum</div>
                {% for val in stats.extreme_values.maximum_10 %}
                <span class="extreme-val">{{ "%.4g"|format(val) }}</span>
                {% endfor %}
            </div>
            {% endif %}

            {% if stats.category == 'Numeric' %}
            <h4>Value Counts</h4>
            <table class="stats-table">
                <tr><td>Zeros</td><td>{{ stats.zeros_count if stats.zeros_count is defined else 0 }} ({{ "%.1f"|format(stats.zeros_percentage) if stats.zeros_percentage is defined else '0.0' }}%)</td></tr>
                <tr><td>Negative</td><td>{{ stats.negative_count if stats.negative_count is defined else 0 }} ({{ "%.1f"|format(stats.negative_percentage) if stats.negative_percentage is defined else '0.0' }}%)</td></tr>
                <tr><td>Infinite</td><td>{{ stats.infinite_count if stats.infinite_count is defined else 0 }} ({{ "%.1f"|format(stats.infinite_percentage) if stats.infinite_percentage is defined else '0.0' }}%)</td></tr>
            </table>
            {% endif %}
        </div>
    </div>
</div>
{% endfor %}

<!-- Correlations -->
<h2>Correlations</h2>
{% if numeric_correlations.plots %}
<div class="plot-grid">
    {% for method, plot_data in numeric_correlations.plots.items() %}
    <div class="plot-item">
        <h4>{{ method | capitalize }}</h4>
        <img src="data:image/png;base64,{{ plot_data }}" />
    </div>
    {% endfor %}
</div>
{% elif numeric_correlations.pearson %}
<h3>Numeric Correlations (Pearson - Top Pairs)</h3>
<table class="stats-table" style="margin-bottom: 16pt;">
    <thead>
        <tr>
            <th>Feature 1</th>
            <th>Feature 2</th>
            <th>Correlation</th>
        </tr>
    </thead>
    <tbody>
        {% set pairs = [] %}
        {% for c1, corrs in numeric_correlations.pearson.items() %}
            {% for c2, val in corrs.items() %}
                {% if c1 < c2 %}
                    {% set _ = pairs.append((c1, c2, val|abs, val)) %}
                {% endif %}
            {% endfor %}
        {% endfor %}
        {% for c1, c2, abs_val, val in pairs|sort(attribute='2', reverse=True) %}
        {% if loop.index <= 20 %}
        <tr>
            <td>{{ c1 }}</td>
            <td>{{ c2 }}</td>
            <td>{{ "%.3f"|format(val) }}</td>
        </tr>
        {% endif %}
        {% endfor %}
    </tbody>
</table>

{% if categorical_correlations %}
<h3>Categorical Correlations (Cramer's V - Top Pairs)</h3>
<table class="stats-table">
    <thead>
        <tr>
            <th>Pair</th>
            <th>Value</th>
        </tr>
    </thead>
    <tbody>
        {% for pair, val in categorical_correlations.items()|sort(attribute='1', reverse=True) %}
        {% if loop.index <= 20 %}
        <tr>
            <td>{{ pair }}</td>
            <td>{{ "%.3f"|format(val) }}</td>
        </tr>
        {% endif %}
        {% endfor %}
    </tbody>
</table>
{% endif %}
{% else %}
<p style="color: #6b7280;">No correlation data available.</p>
{% endif %}

<!-- Missing Values -->
<h2>Missing Values</h2>
{% if missing_plots.missing_bar or missing_plots.missing_heatmap %}
<div class="plot-grid">
    {% if missing_plots.missing_bar %}
    <div class="plot-item">
        <h4>Missing Count per Column</h4>
        <img src="data:image/png;base64,{{ missing_plots.missing_bar }}" />
    </div>
    {% endif %}
    {% if missing_plots.missing_heatmap %}
    <div class="plot-item">
        <h4>Missing Pattern Matrix</h4>
        <img src="data:image/png;base64,{{ missing_plots.missing_heatmap }}" />
    </div>
    {% endif %}
</div>
{% else %}
<h3>Missing Values by Column</h3>
<table class="stats-table">
    <thead>
        <tr>
            <th>Column</th>
            <th>Count</th>
            <th>Percentage</th>
        </tr>
    </thead>
    <tbody>
        {% for col, count in missing_values.count.items()|sort(attribute='1', reverse=True) %}
        {% if count > 0 %}
        <tr>
            <td style="font-weight: 600;">{{ col }}</td>
            <td>{{ count }}</td>
            <td>{{ "%.2f"|format(missing_values.percentage[col]) }}%</td>
        </tr>
        {% endif %}
        {% endfor %}
    </tbody>
</table>
{% endif %}

<!-- Sample Data -->
<h2>Sample Data</h2>
<h3>Head (first 5 rows)</h3>
<div class="data-table">{{ head_table | safe }}</div>
<h3>Random Sample (10 rows)</h3>
<div class="data-table">{{ sample_table | safe }}</div>
<h3>Tail (last 5 rows)</h3>
<div class="data-table">{{ tail_table | safe }}</div>
{% endif %}

<div class="footer">Generated by HashPrep v{{ version }}</div>
</body>
</html>"""
