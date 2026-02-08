import json
from datetime import datetime
from typing import Dict, List

import pandas as pd
import yaml
from jinja2 import Template

import hashprep


class HtmlReport:
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

    def generate(self, summary, full=False, output_file=None, theme="minimal", pdf_mode=False):
        template_str = self._get_template(theme)
        template = Template(template_str)

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
            "pdf_mode": pdf_mode,
            # Dataset Overview
            "rows": dataset_info["rows"],
            "columns": dataset_info["columns"],
            "missing_cells": dataset_info["missing_cells"],
            "missing_percentage": dataset_info["missing_percentage"],
            "duplicate_rows": dataset_info.get("duplicate_rows", 0),
            "duplicate_percentage": dataset_info.get("duplicate_percentage", 0),
            "memory_kib": dataset_info.get("memory_kib", dataset_info.get("memory_mb", 0) * 1024),
            "average_record_size": dataset_info.get("average_record_size_bytes", 0),
            # Variable Types
            "variable_type_counts": variable_type_counts,
            # Alerts
            "alerts_by_type": alerts_by_type,
            "issues": summary["issues"],
            # Reproduction
            "analysis_started": reproduction_info.get("analysis_started", ""),
            "analysis_finished": reproduction_info.get("analysis_finished", ""),
            "duration_seconds": reproduction_info.get("duration_seconds", 0),
            "dataset_hash": reproduction_info.get("dataset_hash", ""),
            "version": hashprep.__version__,
            "config_json": json.dumps(self._generate_config(summary), indent=2),
            # Full report data
            "full": full,
            "head_table": head_df.to_html(index=False, classes="min-w-full divide-y divide-gray-200"),
            "tail_table": tail_df.to_html(index=False, classes="min-w-full divide-y divide-gray-200"),
            "sample_table": sample_df.to_html(index=False, classes="min-w-full divide-y divide-gray-200"),
            "variables": summary["summaries"].get("variables", {}),
            "numeric_correlations": summary["summaries"].get("numeric_correlations", {}),
            "categorical_correlations": summary["summaries"].get("categorical_correlations", {}),
            "mixed_correlations": summary["summaries"].get("mixed_correlations", {}),
            "missing_values": summary["summaries"].get("missing_values", {}),
            "missing_patterns": summary["summaries"].get("missing_patterns", {}),
            "missing_plots": summary["summaries"].get("plots", {}),
            "yaml_dump": yaml.safe_dump,
            "json_dump": lambda x: json.dumps(x, indent=2),
        }

        html_content = template.render(context)
        if output_file:
            with open(output_file, "w") as f:
                f.write(html_content)
        return html_content

    def _group_alerts_by_type(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """Group issues into display categories for the alerts section."""
        groups: Dict[str, List[Dict]] = {}

        for issue in issues:
            alert_type = self.ALERT_TYPE_MAPPING.get(issue["category"], "Other")
            if alert_type not in groups:
                groups[alert_type] = []
            groups[alert_type].append(issue)

        return groups

    def _generate_config(self, summary) -> Dict:
        """Generate configuration dict for download."""
        reproduction_info = summary["summaries"].get("reproduction_info", {})
        return {
            "hashprep_version": hashprep.__version__,
            "analysis_timestamp": reproduction_info.get("analysis_started"),
            "dataset_hash": reproduction_info.get("dataset_hash"),
            "dataset_info": summary["summaries"].get("dataset_info", {}),
            "variable_type_counts": summary["summaries"].get("variable_type_counts", {}),
        }

    def _get_template(self, theme):
        if theme == "neubrutalism":
            return self._neubrutalism_template()
        return self._minimal_template()

    def _minimal_template(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HashPrep Quality Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        code, pre { font-family: 'JetBrains Mono', monospace; }
        .table-container table { min-width: 100%; border-collapse: collapse; }
        .table-container th { padding: 0.75rem 1rem; background-color: #f9fafb; text-align: left; font-size: 0.75rem; font-weight: 500; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
        .table-container td { padding: 0.75rem 1rem; white-space: nowrap; font-size: 0.875rem; color: #111827; border-bottom: 1px solid #f3f4f6; }
        [x-cloak] { display: none !important; }
    </style>
</head>
<body class="bg-gray-50 text-gray-900 antialiased" x-data="{ activeTab: 'overview', alertsOpen: true }">
    <!-- Navigation -->
    <nav class="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-14">
                <div class="flex items-center space-x-2">
                    <span class="font-bold text-lg">HashPrep</span>
                    <span class="text-gray-400 text-sm">v{{ version }}</span>
                </div>
                <div class="flex space-x-1">
                    <button @click="activeTab = 'overview'"
                            :class="activeTab === 'overview' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:text-gray-900'"
                            class="px-4 py-2 text-sm font-medium rounded-lg transition-colors">
                        Overview
                    </button>
                    {% if full %}
                    <button @click="activeTab = 'variables'"
                            :class="activeTab === 'variables' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:text-gray-900'"
                            class="px-4 py-2 text-sm font-medium rounded-lg transition-colors">
                        Variables
                    </button>
                    <button @click="activeTab = 'correlations'"
                            :class="activeTab === 'correlations' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:text-gray-900'"
                            class="px-4 py-2 text-sm font-medium rounded-lg transition-colors">
                        Correlations
                    </button>
                    <button @click="activeTab = 'missing'"
                            :class="activeTab === 'missing' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:text-gray-900'"
                            class="px-4 py-2 text-sm font-medium rounded-lg transition-colors">
                        Missing
                    </button>
                    <button @click="activeTab = 'sample'"
                            :class="activeTab === 'sample' ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:text-gray-900'"
                            class="px-4 py-2 text-sm font-medium rounded-lg transition-colors">
                        Sample
                    </button>
                    {% endif %}
                </div>
                <div class="flex items-center space-x-3">
                    <span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">{{ critical_count }} Critical</span>
                    <span class="px-2 py-1 text-xs font-medium bg-amber-100 text-amber-700 rounded-full">{{ warning_count }} Warnings</span>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- OVERVIEW TAB -->
        <div x-show="activeTab === 'overview'" {% if not pdf_mode %}x-cloak{% endif %}>
            <!-- Dataset Overview -->
            <section class="mb-8">
                <h2 class="text-xl font-semibold mb-4">Overview</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Dataset Statistics -->
                    <div class="bg-white rounded-xl border border-gray-200 p-6">
                        <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Dataset Statistics</h3>
                        <dl class="grid grid-cols-2 gap-4">
                            <div>
                                <dt class="text-sm text-gray-500">Number of variables</dt>
                                <dd class="text-2xl font-bold text-gray-900">{{ columns }}</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Number of observations</dt>
                                <dd class="text-2xl font-bold text-gray-900">{{ rows }}</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Missing cells</dt>
                                <dd class="text-lg font-semibold text-gray-900">{{ missing_cells }}</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Missing cells (%)</dt>
                                <dd class="text-lg font-semibold text-gray-900">{{ missing_percentage }}%</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Duplicate rows</dt>
                                <dd class="text-lg font-semibold text-gray-900">{{ duplicate_rows }}</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Duplicate rows (%)</dt>
                                <dd class="text-lg font-semibold text-gray-900">{{ duplicate_percentage }}%</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Total size in memory</dt>
                                <dd class="text-lg font-semibold text-gray-900">{{ memory_kib }} KiB</dd>
                            </div>
                            <div>
                                <dt class="text-sm text-gray-500">Average record size</dt>
                                <dd class="text-lg font-semibold text-gray-900">{{ average_record_size }} B</dd>
                            </div>
                        </dl>
                    </div>

                    <!-- Variable Types -->
                    <div class="bg-white rounded-xl border border-gray-200 p-6">
                        <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Variable Types</h3>
                        <dl class="space-y-3">
                            {% for type_name, count in variable_type_counts.items() %}
                            {% if count > 0 %}
                            <div class="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                                <dt class="text-gray-600">{{ type_name }}</dt>
                                <dd class="font-bold text-xl text-gray-900">{{ count }}</dd>
                            </div>
                            {% endif %}
                            {% endfor %}
                        </dl>
                    </div>
                </div>
            </section>

            <!-- Alerts Section -->
            <section class="mb-8">
                <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                    <div class="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center cursor-pointer"
                         @click="alertsOpen = !alertsOpen">
                        <h2 class="text-lg font-semibold">Alerts</h2>
                        <div class="flex items-center space-x-4">
                            <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">{{ critical_count }} Critical</span>
                            <span class="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium">{{ warning_count }} Warnings</span>
                            <svg :class="alertsOpen ? 'rotate-180' : ''" class="w-5 h-5 text-gray-400 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </div>
                    </div>

                    <div x-show="alertsOpen || {{ 'true' if pdf_mode else 'false' }}" x-collapse {% if not pdf_mode %}x-cloak{% endif %}>
                        {% for alert_type, alerts in alerts_by_type.items() %}
                        <div class="border-b border-gray-100 last:border-b-0">
                            <h3 class="px-6 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider">{{ alert_type }}</h3>
                            <ul class="divide-y divide-gray-100">
                                {% for alert in alerts %}
                                <li class="px-6 py-3 flex items-start space-x-3 hover:bg-gray-50">
                                    <span class="flex-shrink-0 w-2 h-2 mt-2 rounded-full
                                        {% if alert.severity == 'critical' %}bg-red-500{% else %}bg-amber-500{% endif %}">
                                    </span>
                                    <div class="flex-1 min-w-0">
                                        <p class="text-sm text-gray-900">{{ alert.description }}</p>
                                        <p class="text-xs text-gray-500 mt-1">{{ alert_type }}</p>
                                    </div>
                                </li>
                                {% endfor %}
                            </ul>
                        </div>
                        {% endfor %}
                        {% if not alerts_by_type %}
                        <div class="px-6 py-8 text-center text-gray-500">
                            No issues detected.
                        </div>
                        {% endif %}
                    </div>
                </div>
            </section>

            <!-- Reproduction Section -->
            <section class="mb-8">
                <div class="bg-white rounded-xl border border-gray-200 p-6">
                    <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Reproduction</h2>
                    <dl class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                            <dt class="text-gray-500">Analysis started</dt>
                            <dd class="font-mono text-gray-900">{{ analysis_started[:19] if analysis_started else 'N/A' }}</dd>
                        </div>
                        <div>
                            <dt class="text-gray-500">Analysis finished</dt>
                            <dd class="font-mono text-gray-900">{{ analysis_finished[:19] if analysis_finished else 'N/A' }}</dd>
                        </div>
                        <div>
                            <dt class="text-gray-500">Duration</dt>
                            <dd class="font-mono text-gray-900">{{ duration_seconds }} seconds</dd>
                        </div>
                        <div>
                            <dt class="text-gray-500">Software version</dt>
                            <dd class="font-mono text-gray-900">hashprep v{{ version }}</dd>
                        </div>
                    </dl>
                    {% if not pdf_mode %}
                    <div class="mt-4 pt-4 border-t border-gray-100">
                        <button onclick="downloadConfig()" class="text-sm text-blue-600 hover:text-blue-800 hover:underline">
                            Download configuration (config.json)
                        </button>
                    </div>
                    {% endif %}
                </div>
            </section>
        </div>

        {% if full %}
        <!-- VARIABLES TAB -->
        <div x-show="activeTab === 'variables'" {% if not pdf_mode %}x-cloak{% endif %}>
            <section>
                <h2 class="text-xl font-semibold mb-6">Variables</h2>
                <div class="space-y-6">
                    {% for col, stats in variables.items() %}
                    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden" x-data="{ expanded: false }">
                        <!-- Variable Card Header -->
                        <div class="p-5">
                            <!-- Title Row -->
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center gap-3">
                                    <h3 class="text-lg font-semibold text-gray-900">{{ col }}</h3>
                                    <span class="px-2.5 py-1 text-xs font-medium bg-blue-50 text-blue-700 rounded-full">{{ stats.category }}</span>
                                    {% if stats.distinct_percentage >= 95 %}
                                    <span class="px-2 py-0.5 text-xs font-medium bg-amber-100 text-amber-700 rounded-full">Unique</span>
                                    {% endif %}
                                    {% if stats.missing_percentage > 0 %}
                                    <span class="px-2 py-0.5 text-xs font-medium bg-red-50 text-red-600 rounded-full">{{ "%.1f"|format(stats.missing_percentage) }}% missing</span>
                                    {% endif %}
                                    {% if stats.category == 'Numeric' and stats.zeros_percentage and stats.zeros_percentage > 50 %}
                                    <span class="px-2 py-0.5 text-xs font-medium bg-amber-100 text-amber-700 rounded-full">High zeros</span>
                                    {% endif %}
                                </div>
                                <button @click="expanded = !expanded" class="text-gray-400 hover:text-gray-600 transition-colors">
                                    <svg :class="expanded ? 'rotate-180' : ''" class="w-5 h-5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                    </svg>
                                </button>
                            </div>

                            <!-- Main Content: Stats + Chart side by side -->
                            <div class="flex flex-col lg:flex-row gap-6">
                                <!-- Left: Key Statistics -->
                                <div class="flex-1 min-w-0">
                                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                                        <div class="bg-gray-50 rounded-lg p-3">
                                            <div class="text-xs text-gray-500 uppercase tracking-wide">Distinct</div>
                                            <div class="text-lg font-semibold text-gray-900">{{ stats.distinct_count }}</div>
                                            <div class="text-xs text-gray-400">{{ "%.1f"|format(stats.distinct_percentage) }}%</div>
                                        </div>
                                        <div class="bg-gray-50 rounded-lg p-3">
                                            <div class="text-xs text-gray-500 uppercase tracking-wide">Missing</div>
                                            <div class="text-lg font-semibold text-gray-900">{{ stats.missing_count }}</div>
                                            <div class="text-xs text-gray-400">{{ "%.1f"|format(stats.missing_percentage) }}%</div>
                                        </div>
                                        {% if stats.category == 'Numeric' %}
                                        <div class="bg-gray-50 rounded-lg p-3">
                                            <div class="text-xs text-gray-500 uppercase tracking-wide">Mean</div>
                                            <div class="text-lg font-semibold text-gray-900">{{ "%.4g"|format(stats.mean) if stats.mean is not none else 'N/A' }}</div>
                                            <div class="text-xs text-gray-400">avg value</div>
                                        </div>
                                        <div class="bg-gray-50 rounded-lg p-3">
                                            <div class="text-xs text-gray-500 uppercase tracking-wide">Range</div>
                                            <div class="text-lg font-semibold text-gray-900">{{ "%.4g"|format(stats.minimum) if stats.minimum is not none else '?' }} - {{ "%.4g"|format(stats.maximum) if stats.maximum is not none else '?' }}</div>
                                            <div class="text-xs text-gray-400">min - max</div>
                                        </div>
                                        {% else %}
                                        <div class="bg-gray-50 rounded-lg p-3">
                                            <div class="text-xs text-gray-500 uppercase tracking-wide">Memory</div>
                                            <div class="text-lg font-semibold text-gray-900">{{ "%.1f"|format(stats.memory_size / 1024) }}</div>
                                            <div class="text-xs text-gray-400">KiB</div>
                                        </div>
                                        <div class="bg-gray-50 rounded-lg p-3">
                                            <div class="text-xs text-gray-500 uppercase tracking-wide">Length</div>
                                            {% if stats.overview and stats.overview.length %}
                                            <div class="text-lg font-semibold text-gray-900">{{ stats.overview.length.min_length }} - {{ stats.overview.length.max_length }}</div>
                                            <div class="text-xs text-gray-400">chars</div>
                                            {% else %}
                                            <div class="text-lg font-semibold text-gray-900">-</div>
                                            {% endif %}
                                        </div>
                                        {% endif %}
                                    </div>
                                </div>

                                <!-- Right: Chart -->
                                {% if stats.plots %}
                                <div class="lg:w-80 flex-shrink-0">
                                    {% if stats.plots.histogram %}
                                    <img src="data:image/png;base64,{{ stats.plots.histogram }}" class="w-full h-auto" alt="Distribution of {{ col }}" />
                                    {% elif stats.plots.common_values_bar %}
                                    <img src="data:image/png;base64,{{ stats.plots.common_values_bar }}" class="w-full h-auto" alt="Top values of {{ col }}" />
                                    {% elif stats.plots.word_bar %}
                                    <img src="data:image/png;base64,{{ stats.plots.word_bar }}" class="w-full h-auto" alt="Top words in {{ col }}" />
                                    {% endif %}
                                </div>
                                {% endif %}
                            </div>
                        </div>

                        <!-- Expandable Details Section -->
                        <div x-show="expanded || {{ 'true' if pdf_mode else 'false' }}" x-collapse {% if not pdf_mode %}x-cloak{% endif %}>
                            <div class="border-t border-gray-100 bg-gray-50/50 p-5">
                                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    <!-- Statistics Column -->
                                    <div>
                                        {% if stats.category == 'Numeric' and stats.statistics %}
                                        <h4 class="text-sm font-semibold text-gray-700 mb-3">Quantile Statistics</h4>
                                        <table class="w-full text-sm mb-6">
                                            <tbody class="divide-y divide-gray-200">
                                                <tr><td class="py-1.5 text-gray-600">Minimum</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.minimum) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">5th percentile</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.p5) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Q1 (25%)</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.q1) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Median (50%)</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.median) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Q3 (75%)</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.q3) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">95th percentile</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.p95) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Maximum</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.maximum) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Range</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.range) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">IQR</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.quantiles.iqr) }}</td></tr>
                                            </tbody>
                                        </table>

                                        <h4 class="text-sm font-semibold text-gray-700 mb-3">Descriptive Statistics</h4>
                                        <table class="w-full text-sm">
                                            <tbody class="divide-y divide-gray-200">
                                                <tr><td class="py-1.5 text-gray-600">Mean</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.mean) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Std deviation</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.standard_deviation) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Variance</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.variance) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">CV</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.coefficient_of_variation) if stats.statistics.descriptive.coefficient_of_variation else 'N/A' }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Skewness</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.skewness) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Kurtosis</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.kurtosis) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">MAD</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.mad) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Sum</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.6g"|format(stats.statistics.descriptive.sum) }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Monotonicity</td><td class="py-1.5 text-right font-medium text-blue-600">{{ stats.statistics.descriptive.monotonicity | capitalize }}</td></tr>
                                            </tbody>
                                        </table>
                                        {% elif stats.overview %}
                                        <h4 class="text-sm font-semibold text-gray-700 mb-3">Length Statistics</h4>
                                        <table class="w-full text-sm mb-6">
                                            <tbody class="divide-y divide-gray-200">
                                                <tr><td class="py-1.5 text-gray-600">Min length</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.overview.length.min_length }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Max length</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.overview.length.max_length }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Mean length</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.2f"|format(stats.overview.length.mean_length) if stats.overview.length.mean_length else 'N/A' }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Median length</td><td class="py-1.5 text-right font-medium font-mono">{{ "%.2f"|format(stats.overview.length.median_length) if stats.overview.length.median_length else 'N/A' }}</td></tr>
                                            </tbody>
                                        </table>

                                        <h4 class="text-sm font-semibold text-gray-700 mb-3">Character Statistics</h4>
                                        <table class="w-full text-sm">
                                            <tbody class="divide-y divide-gray-200">
                                                <tr><td class="py-1.5 text-gray-600">Total characters</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.overview.characters_and_unicode.total_characters }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Distinct characters</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.overview.characters_and_unicode.distinct_characters }}</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Distinct categories</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.overview.characters_and_unicode.distinct_categories }}</td></tr>
                                            </tbody>
                                        </table>
                                        {% endif %}
                                    </div>

                                    <!-- Common Values / Extreme Values Column -->
                                    <div>
                                        {% if stats.common_values or (stats.categories and stats.categories.common_values) %}
                                        <h4 class="text-sm font-semibold text-gray-700 mb-3">Common Values</h4>
                                        <table class="w-full text-sm mb-6">
                                            <thead>
                                                <tr class="border-b border-gray-200">
                                                    <th class="py-2 text-left text-gray-500 font-medium text-xs uppercase">Value</th>
                                                    <th class="py-2 text-right text-gray-500 font-medium text-xs uppercase">Count</th>
                                                    <th class="py-2 text-right text-gray-500 font-medium text-xs uppercase">%</th>
                                                </tr>
                                            </thead>
                                            <tbody class="divide-y divide-gray-100">
                                                {% set cv = stats.common_values if stats.common_values else stats.categories.common_values %}
                                                {% for val, info in cv.items() %}
                                                <tr>
                                                    <td class="py-1.5 font-mono text-gray-900 truncate max-w-[200px]" title="{{ val }}">{{ val }}</td>
                                                    <td class="py-1.5 text-right font-mono">{{ info.count }}</td>
                                                    <td class="py-1.5 text-right font-mono">{{ "%.1f"|format(info.percentage) }}%</td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                        {% endif %}

                                        {% if stats.extreme_values %}
                                        <h4 class="text-sm font-semibold text-gray-700 mb-3">Extreme Values</h4>
                                        <div class="space-y-4">
                                            <div>
                                                <div class="text-xs text-gray-500 uppercase mb-2">Minimum values</div>
                                                <div class="flex flex-wrap gap-1.5">
                                                    {% for val in stats.extreme_values.minimum_10 %}
                                                    <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded font-mono">{{ "%.4g"|format(val) }}</span>
                                                    {% endfor %}
                                                </div>
                                            </div>
                                            <div>
                                                <div class="text-xs text-gray-500 uppercase mb-2">Maximum values</div>
                                                <div class="flex flex-wrap gap-1.5">
                                                    {% for val in stats.extreme_values.maximum_10 %}
                                                    <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded font-mono">{{ "%.4g"|format(val) }}</span>
                                                    {% endfor %}
                                                </div>
                                            </div>
                                        </div>
                                        {% endif %}

                                        {% if stats.category == 'Numeric' %}
                                        <h4 class="text-sm font-semibold text-gray-700 mb-3 mt-6">Value Counts</h4>
                                        <table class="w-full text-sm">
                                            <tbody class="divide-y divide-gray-200">
                                                <tr><td class="py-1.5 text-gray-600">Zeros</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.zeros_count if stats.zeros_count is defined else 0 }} ({{ "%.1f"|format(stats.zeros_percentage) if stats.zeros_percentage is defined else '0.0' }}%)</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Negative</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.negative_count if stats.negative_count is defined else 0 }} ({{ "%.1f"|format(stats.negative_percentage) if stats.negative_percentage is defined else '0.0' }}%)</td></tr>
                                                <tr><td class="py-1.5 text-gray-600">Infinite</td><td class="py-1.5 text-right font-medium font-mono">{{ stats.infinite_count if stats.infinite_count is defined else 0 }} ({{ "%.1f"|format(stats.infinite_percentage) if stats.infinite_percentage is defined else '0.0' }}%)</td></tr>
                                            </tbody>
                                        </table>
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
        </div>

        <!-- CORRELATIONS TAB -->
        <div x-show="activeTab === 'correlations'" {% if not pdf_mode %}x-cloak{% endif %}>
            <section>
                <h2 class="text-xl font-semibold mb-6">Correlations</h2>
                <div class="bg-white rounded-lg border border-gray-200 p-6">
                    {% if numeric_correlations.plots %}
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {% for method, plot_data in numeric_correlations.plots.items() %}
                        <div>
                            <h3 class="text-sm font-medium text-gray-700 mb-4 capitalize">{{ method }} Correlation</h3>
                            <img src="data:image/png;base64,{{ plot_data }}" class="w-full h-auto" alt="{{ method }} correlation heatmap" />
                        </div>
                        {% endfor %}
                    </div>
                    {% elif numeric_correlations.pearson %}
                    <h3 class="text-sm font-medium text-gray-700 mb-4">Numeric Correlations (Pearson - Top Pairs)</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Feature 1</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Feature 2</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Correlation</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
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
                                    <td class="px-4 py-2 text-sm text-gray-900">{{ c1 }}</td>
                                    <td class="px-4 py-2 text-sm text-gray-900">{{ c2 }}</td>
                                    <td class="px-4 py-2 text-sm text-gray-900">{{ "%.3f"|format(val) }}</td>
                                </tr>
                                {% endif %}
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>

                    {% if categorical_correlations %}
                    <h3 class="text-sm font-medium text-gray-700 mt-6 mb-4">Categorical Correlations (Cramer's V - Top Pairs)</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Pair</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                {% for pair, val in categorical_correlations.items()|sort(attribute='1', reverse=True) %}
                                {% if loop.index <= 20 %}
                                <tr>
                                    <td class="px-4 py-2 text-sm text-gray-900">{{ pair }}</td>
                                    <td class="px-4 py-2 text-sm text-gray-900">{{ "%.3f"|format(val) }}</td>
                                </tr>
                                {% endif %}
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}
                    {% else %}
                    <p class="text-gray-500 italic">No numeric correlations available.</p>
                    {% endif %}
                </div>
            </section>
        </div>

        <!-- MISSING TAB -->
        <div x-show="activeTab === 'missing'" {% if not pdf_mode %}x-cloak{% endif %}>
            <section>
                <h2 class="text-xl font-semibold mb-6">Missing Values</h2>
                <div class="bg-white rounded-lg border border-gray-200 p-6">
                    {% if missing_plots.missing_bar or missing_plots.missing_heatmap %}
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {% if missing_plots.missing_bar %}
                        <div>
                            <h3 class="text-sm font-medium text-gray-700 mb-4">Missing Count per Column</h3>
                            <img src="data:image/png;base64,{{ missing_plots.missing_bar }}" class="w-full h-auto" alt="Missing values bar chart" />
                        </div>
                        {% endif %}
                        {% if missing_plots.missing_heatmap %}
                        <div>
                            <h3 class="text-sm font-medium text-gray-700 mb-4">Missing Pattern Matrix</h3>
                            <img src="data:image/png;base64,{{ missing_plots.missing_heatmap }}" class="w-full h-auto" alt="Missing values heatmap" />
                        </div>
                        {% endif %}
                    </div>
                    {% else %}
                    <h3 class="text-sm font-medium text-gray-700 mb-4">Missing Values by Column</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Column</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Count</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Percentage</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                {% for col, count in missing_values.count.items()|sort(attribute='1', reverse=True) %}
                                {% if count > 0 %}
                                <tr>
                                    <td class="px-4 py-2 text-sm text-gray-900 font-medium">{{ col }}</td>
                                    <td class="px-4 py-2 text-sm text-gray-900">{{ count }}</td>
                                    <td class="px-4 py-2 text-sm text-gray-900">{{ "%.2f"|format(missing_values.percentage[col]) }}%</td>
                                </tr>
                                {% endif %}
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}
                </div>
            </section>
        </div>

        <!-- SAMPLE TAB -->
        <div x-show="activeTab === 'sample'" {% if not pdf_mode %}x-cloak{% endif %}>
            <section class="space-y-6">
                <h2 class="text-xl font-semibold">Sample Data</h2>

                <!-- Head (First 5 rows) -->
                <div>
                    <h3 class="text-sm font-medium text-gray-700 mb-3">Head <span class="text-gray-400 font-normal">(first 5 rows)</span></h3>
                    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
                        <div class="table-container overflow-x-auto">
                            {{ head_table | safe }}
                        </div>
                    </div>
                </div>

                <!-- Sample (Random 10 rows) -->
                <div>
                    <h3 class="text-sm font-medium text-gray-700 mb-3">Random Sample <span class="text-gray-400 font-normal">(10 rows)</span></h3>
                    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
                        <div class="table-container overflow-x-auto">
                            {{ sample_table | safe }}
                        </div>
                    </div>
                </div>

                <!-- Tail (Last 5 rows) -->
                <div>
                    <h3 class="text-sm font-medium text-gray-700 mb-3">Tail <span class="text-gray-400 font-normal">(last 5 rows)</span></h3>
                    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
                        <div class="table-container overflow-x-auto">
                            {{ tail_table | safe }}
                        </div>
                    </div>
                </div>
            </section>
        </div>
        {% endif %}
    </main>

    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-t border-gray-200 text-center text-gray-500">
        <p class="text-sm">Built with HashPrep</p>
    </footer>

    <script>
        const configData = {{ config_json | safe }};

        function downloadConfig() {
            const blob = new Blob([JSON.stringify(configData, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'hashprep_config.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
"""

    def _neubrutalism_template(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HashPrep Quality Report [NEO]</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'JetBrains Mono', monospace; }
        .brutal-card { border: 4px solid black; box-shadow: 8px 8px 0px 0px rgba(0,0,0,1); background-color: white; padding: 1.5rem; }
        .brutal-table th { border: 4px solid black; background-color: #fde047; padding: 0.75rem; text-align: left; font-weight: bold; }
        .brutal-table td { border: 4px solid black; padding: 0.75rem; }
        .brutal-img { border: 4px solid black; }

        /* Pandas dataframe table styling for sample data */
        table.dataframe { border-collapse: collapse; width: 100%; border: 4px solid black; }
        table.dataframe th { border: 2px solid black; background-color: #fde047; padding: 0.5rem; text-align: left; font-weight: bold; white-space: nowrap; }
        table.dataframe td { border: 2px solid black; padding: 0.5rem; white-space: nowrap; }

        [x-cloak] { display: none !important; }
    </style>
</head>
<body class="bg-gray-100 p-8" x-data="{ activeTab: 'overview', alertsOpen: true }">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <header class="brutal-card mb-8 bg-white">
            <div class="flex justify-between items-center flex-wrap gap-4">
                <div>
                    <h1 class="text-4xl font-black uppercase italic">HashPrep // Report</h1>
                    <p class="font-bold mt-2">VERSION: {{ version }}</p>
                </div>
                <div class="flex gap-4">
                    <div class="brutal-card bg-red-400 py-2 px-4">
                        <span class="font-black text-2xl">CRIT: {{ critical_count }}</span>
                    </div>
                    <div class="brutal-card bg-orange-300 py-2 px-4">
                        <span class="font-black text-2xl">WARN: {{ warning_count }}</span>
                    </div>
                </div>
            </div>
        </header>

        <!-- Navigation -->
        <nav class="mb-8 flex flex-wrap gap-2">
            <button @click="activeTab = 'overview'"
                    :class="activeTab === 'overview' ? 'bg-black text-white' : 'bg-white'"
                    class="brutal-card py-2 px-4 font-bold uppercase">Overview</button>
            {% if full %}
            <button @click="activeTab = 'variables'"
                    :class="activeTab === 'variables' ? 'bg-black text-white' : 'bg-white'"
                    class="brutal-card py-2 px-4 font-bold uppercase">Variables</button>
            <button @click="activeTab = 'correlations'"
                    :class="activeTab === 'correlations' ? 'bg-black text-white' : 'bg-white'"
                    class="brutal-card py-2 px-4 font-bold uppercase">Correlations</button>
            <button @click="activeTab = 'missing'"
                    :class="activeTab === 'missing' ? 'bg-black text-white' : 'bg-white'"
                    class="brutal-card py-2 px-4 font-bold uppercase">Missing</button>
            <button @click="activeTab = 'sample'"
                    :class="activeTab === 'sample' ? 'bg-black text-white' : 'bg-white'"
                    class="brutal-card py-2 px-4 font-bold uppercase">Sample</button>
            {% endif %}
        </nav>

        <!-- OVERVIEW TAB -->
        <div x-show="activeTab === 'overview'" {% if not pdf_mode %}x-cloak{% endif %}>
            <!-- Dataset Overview -->
            <section class="mb-8">
                <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Overview</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="brutal-card">
                        <h3 class="font-black uppercase mb-4 border-b-4 border-black pb-2">Dataset Statistics</h3>
                        <dl class="grid grid-cols-2 gap-4">
                            <div><dt class="text-sm">Variables</dt><dd class="text-2xl font-black">{{ columns }}</dd></div>
                            <div><dt class="text-sm">Observations</dt><dd class="text-2xl font-black">{{ rows }}</dd></div>
                            <div><dt class="text-sm">Missing cells</dt><dd class="text-xl font-bold">{{ missing_cells }} ({{ missing_percentage }}%)</dd></div>
                            <div><dt class="text-sm">Duplicate rows</dt><dd class="text-xl font-bold">{{ duplicate_rows }} ({{ duplicate_percentage }}%)</dd></div>
                            <div><dt class="text-sm">Memory</dt><dd class="text-xl font-bold">{{ memory_kib }} KiB</dd></div>
                            <div><dt class="text-sm">Avg record</dt><dd class="text-xl font-bold">{{ average_record_size }} B</dd></div>
                        </dl>
                    </div>
                    <div class="brutal-card">
                        <h3 class="font-black uppercase mb-4 border-b-4 border-black pb-2">Variable Types</h3>
                        <dl class="space-y-2">
                            {% for type_name, count in variable_type_counts.items() %}
                            {% if count > 0 %}
                            <div class="flex justify-between items-center border-b-2 border-black pb-2">
                                <dt class="uppercase">{{ type_name }}</dt>
                                <dd class="font-black text-2xl">{{ count }}</dd>
                            </div>
                            {% endif %}
                            {% endfor %}
                        </dl>
                    </div>
                </div>
            </section>

            <!-- Alerts -->
            <section class="mb-8">
                <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Alerts</h2>
                <div class="brutal-card">
                    {% for alert_type, alerts in alerts_by_type.items() %}
                    <div class="mb-4 last:mb-0">
                        <h3 class="font-black uppercase bg-yellow-300 px-2 py-1 inline-block mb-2">{{ alert_type }}</h3>
                        <ul class="space-y-1">
                            {% for alert in alerts %}
                            <li class="flex items-start space-x-2 {% if alert.severity == 'critical' %}bg-red-100{% else %}bg-orange-100{% endif %} p-2 border-2 border-black">
                                <span class="font-black">{% if alert.severity == 'critical' %}!!{% else %}!{% endif %}</span>
                                <span>{{ alert.description }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endfor %}
                </div>
            </section>

            <!-- Reproduction -->
            <section class="mb-8">
                <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Reproduction</h2>
                <div class="brutal-card">
                    <dl class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div><dt class="uppercase font-bold">Started</dt><dd class="font-mono">{{ analysis_started[:19] if analysis_started else 'N/A' }}</dd></div>
                        <div><dt class="uppercase font-bold">Finished</dt><dd class="font-mono">{{ analysis_finished[:19] if analysis_finished else 'N/A' }}</dd></div>
                        <div><dt class="uppercase font-bold">Duration</dt><dd class="font-mono">{{ duration_seconds }}s</dd></div>
                        <div><dt class="uppercase font-bold">Version</dt><dd class="font-mono">v{{ version }}</dd></div>
                    </dl>
                </div>
            </section>
        </div>

        {% if full %}
        <!-- VARIABLES TAB -->
        <div x-show="activeTab === 'variables'" {% if not pdf_mode %}x-cloak{% endif %}>
            <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Variables</h2>
            <div class="space-y-8">
                {% for col, stats in variables.items() %}
                <div class="brutal-card" x-data="{ expanded: false }">
                    <!-- Header -->
                    <div class="flex justify-between items-center mb-4 border-b-4 border-black pb-2 cursor-pointer" @click="expanded = !expanded">
                        <div class="flex items-center gap-3 flex-wrap">
                            <h3 class="text-xl font-black">{{ col }}</h3>
                            <span class="bg-black text-white px-2 py-1 font-bold text-xs">{{ stats.category }}</span>
                            {% if stats.distinct_percentage >= 95 %}
                            <span class="bg-yellow-300 px-2 py-1 font-bold text-xs border-2 border-black">UNIQUE</span>
                            {% endif %}
                            {% if stats.missing_percentage > 0 %}
                            <span class="bg-red-300 px-2 py-1 font-bold text-xs border-2 border-black">{{ "%.1f"|format(stats.missing_percentage) }}% MISSING</span>
                            {% endif %}
                        </div>
                        <svg :class="expanded ? 'rotate-180' : ''" class="w-6 h-6 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </div>

                    <!-- Quick Stats + Chart -->
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <!-- Stat Cards -->
                        <div class="lg:col-span-2 grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <div class="border-2 border-black p-3 bg-gray-50">
                                <div class="text-xs font-bold uppercase">Distinct</div>
                                <div class="text-lg font-black">{{ stats.distinct_count }}</div>
                                <div class="text-xs">{{ "%.1f"|format(stats.distinct_percentage) }}%</div>
                            </div>
                            <div class="border-2 border-black p-3 bg-gray-50">
                                <div class="text-xs font-bold uppercase">Missing</div>
                                <div class="text-lg font-black">{{ stats.missing_count }}</div>
                                <div class="text-xs">{{ "%.1f"|format(stats.missing_percentage) }}%</div>
                            </div>
                            {% if stats.category == 'Numeric' %}
                            <div class="border-2 border-black p-3 bg-gray-50">
                                <div class="text-xs font-bold uppercase">Mean</div>
                                <div class="text-lg font-black">{{ "%.4g"|format(stats.mean) if stats.mean is not none else 'N/A' }}</div>
                            </div>
                            <div class="border-2 border-black p-3 bg-gray-50">
                                <div class="text-xs font-bold uppercase">Range</div>
                                <div class="text-lg font-black">{{ "%.4g"|format(stats.minimum) if stats.minimum is not none else '?' }} - {{ "%.4g"|format(stats.maximum) if stats.maximum is not none else '?' }}</div>
                            </div>
                            {% else %}
                            <div class="border-2 border-black p-3 bg-gray-50">
                                <div class="text-xs font-bold uppercase">Memory</div>
                                <div class="text-lg font-black">{{ "%.1f"|format(stats.memory_size / 1024) }} KiB</div>
                            </div>
                            <div class="border-2 border-black p-3 bg-gray-50">
                                <div class="text-xs font-bold uppercase">Length</div>
                                {% if stats.overview and stats.overview.length %}
                                <div class="text-lg font-black">{{ stats.overview.length.min_length }} - {{ stats.overview.length.max_length }}</div>
                                {% else %}
                                <div class="text-lg font-black">-</div>
                                {% endif %}
                            </div>
                            {% endif %}
                        </div>

                        <!-- Chart -->
                        {% if stats.plots %}
                        <div>
                            {% if stats.plots.histogram %}
                            <img src="data:image/png;base64,{{ stats.plots.histogram }}" class="w-full h-auto" />
                            {% elif stats.plots.common_values_bar %}
                            <img src="data:image/png;base64,{{ stats.plots.common_values_bar }}" class="w-full h-auto" />
                            {% elif stats.plots.word_bar %}
                            <img src="data:image/png;base64,{{ stats.plots.word_bar }}" class="w-full h-auto" />
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>

                    <!-- Expandable Details -->
                    <div x-show="expanded || {{ 'true' if pdf_mode else 'false' }}" x-collapse {% if not pdf_mode %}x-cloak{% endif %}>
                        <div class="mt-6 pt-4 border-t-4 border-black grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <!-- Statistics -->
                            <div>
                                {% if stats.category == 'Numeric' and stats.statistics %}
                                <h4 class="font-bold uppercase text-sm mb-2 bg-yellow-300 inline-block px-2">Quantile Statistics</h4>
                                <table class="w-full text-sm mb-4">
                                    <tbody>
                                        <tr class="border-b border-black"><td class="py-1">Minimum</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.minimum) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">5th pctl</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.p5) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Q1</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.q1) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Median</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.median) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Q3</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.q3) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">95th pctl</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.p95) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Maximum</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.maximum) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Range</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.range) }}</td></tr>
                                        <tr><td class="py-1">IQR</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.quantiles.iqr) }}</td></tr>
                                    </tbody>
                                </table>
                                <h4 class="font-bold uppercase text-sm mb-2 bg-yellow-300 inline-block px-2">Descriptive Statistics</h4>
                                <table class="w-full text-sm">
                                    <tbody>
                                        <tr class="border-b border-black"><td class="py-1">Mean</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.mean) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Std Dev</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.standard_deviation) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Variance</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.variance) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">CV</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.coefficient_of_variation) if stats.statistics.descriptive.coefficient_of_variation else 'N/A' }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Skewness</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.skewness) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Kurtosis</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.kurtosis) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">MAD</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.mad) }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Sum</td><td class="py-1 text-right font-mono font-bold">{{ "%.6g"|format(stats.statistics.descriptive.sum) }}</td></tr>
                                        <tr><td class="py-1">Monotonicity</td><td class="py-1 text-right font-bold text-blue-600">{{ stats.statistics.descriptive.monotonicity | capitalize }}</td></tr>
                                    </tbody>
                                </table>
                                {% elif stats.overview %}
                                <h4 class="font-bold uppercase text-sm mb-2 bg-yellow-300 inline-block px-2">Length Statistics</h4>
                                <table class="w-full text-sm mb-4">
                                    <tbody>
                                        <tr class="border-b border-black"><td class="py-1">Min length</td><td class="py-1 text-right font-mono font-bold">{{ stats.overview.length.min_length }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Max length</td><td class="py-1 text-right font-mono font-bold">{{ stats.overview.length.max_length }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Mean length</td><td class="py-1 text-right font-mono font-bold">{{ "%.2f"|format(stats.overview.length.mean_length) if stats.overview.length.mean_length else 'N/A' }}</td></tr>
                                        <tr><td class="py-1">Median length</td><td class="py-1 text-right font-mono font-bold">{{ "%.2f"|format(stats.overview.length.median_length) if stats.overview.length.median_length else 'N/A' }}</td></tr>
                                    </tbody>
                                </table>
                                <h4 class="font-bold uppercase text-sm mb-2 bg-yellow-300 inline-block px-2">Character Statistics</h4>
                                <table class="w-full text-sm">
                                    <tbody>
                                        <tr class="border-b border-black"><td class="py-1">Total characters</td><td class="py-1 text-right font-mono font-bold">{{ stats.overview.characters_and_unicode.total_characters }}</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Distinct characters</td><td class="py-1 text-right font-mono font-bold">{{ stats.overview.characters_and_unicode.distinct_characters }}</td></tr>
                                        <tr><td class="py-1">Distinct categories</td><td class="py-1 text-right font-mono font-bold">{{ stats.overview.characters_and_unicode.distinct_categories }}</td></tr>
                                    </tbody>
                                </table>
                                {% endif %}
                            </div>

                            <!-- Common Values / Extreme Values / Value Counts -->
                            <div>
                                {% if stats.common_values or (stats.categories and stats.categories.common_values) %}
                                <h4 class="font-bold uppercase text-sm mb-2 bg-yellow-300 inline-block px-2">Common Values</h4>
                                <table class="w-full text-sm mb-4">
                                    <thead>
                                        <tr class="border-b-2 border-black">
                                            <th class="py-1 text-left font-bold">Value</th>
                                            <th class="py-1 text-right font-bold">Count</th>
                                            <th class="py-1 text-right font-bold">%</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% set cv = stats.common_values if stats.common_values else stats.categories.common_values %}
                                        {% for val, info in cv.items() %}
                                        <tr class="border-b border-black">
                                            <td class="py-1 font-mono truncate max-w-[200px]">{{ val }}</td>
                                            <td class="py-1 text-right font-mono">{{ info.count }}</td>
                                            <td class="py-1 text-right font-mono">{{ "%.1f"|format(info.percentage) }}%</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                                {% endif %}

                                {% if stats.extreme_values %}
                                <h4 class="font-bold uppercase text-sm mb-2 bg-yellow-300 inline-block px-2">Extreme Values</h4>
                                <div class="mb-2">
                                    <div class="text-xs font-bold uppercase mb-1">Minimum</div>
                                    <div class="flex flex-wrap gap-1">
                                        {% for val in stats.extreme_values.minimum_10 %}
                                        <span class="px-2 py-0.5 bg-blue-100 border-2 border-black text-xs font-mono font-bold">{{ "%.4g"|format(val) }}</span>
                                        {% endfor %}
                                    </div>
                                </div>
                                <div class="mb-4">
                                    <div class="text-xs font-bold uppercase mb-1">Maximum</div>
                                    <div class="flex flex-wrap gap-1">
                                        {% for val in stats.extreme_values.maximum_10 %}
                                        <span class="px-2 py-0.5 bg-red-100 border-2 border-black text-xs font-mono font-bold">{{ "%.4g"|format(val) }}</span>
                                        {% endfor %}
                                    </div>
                                </div>
                                {% endif %}

                                {% if stats.category == 'Numeric' %}
                                <h4 class="font-bold uppercase text-sm mb-2 bg-yellow-300 inline-block px-2">Value Counts</h4>
                                <table class="w-full text-sm">
                                    <tbody>
                                        <tr class="border-b border-black"><td class="py-1">Zeros</td><td class="py-1 text-right font-mono font-bold">{{ stats.zeros_count if stats.zeros_count is defined else 0 }} ({{ "%.1f"|format(stats.zeros_percentage) if stats.zeros_percentage is defined else '0.0' }}%)</td></tr>
                                        <tr class="border-b border-black"><td class="py-1">Negative</td><td class="py-1 text-right font-mono font-bold">{{ stats.negative_count if stats.negative_count is defined else 0 }} ({{ "%.1f"|format(stats.negative_percentage) if stats.negative_percentage is defined else '0.0' }}%)</td></tr>
                                        <tr><td class="py-1">Infinite</td><td class="py-1 text-right font-mono font-bold">{{ stats.infinite_count if stats.infinite_count is defined else 0 }} ({{ "%.1f"|format(stats.infinite_percentage) if stats.infinite_percentage is defined else '0.0' }}%)</td></tr>
                                    </tbody>
                                </table>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- CORRELATIONS TAB -->
        <div x-show="activeTab === 'correlations'" {% if not pdf_mode %}x-cloak{% endif %}>
            <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Correlations</h2>
            <div class="brutal-card">
                {% if numeric_correlations.plots %}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {% for method, plot_data in numeric_correlations.plots.items() %}
                    <div>
                        <h3 class="font-bold mb-2 uppercase">{{ method }}</h3>
                        <img src="data:image/png;base64,{{ plot_data }}" class="w-full h-auto" />
                    </div>
                    {% endfor %}
                </div>
                {% elif numeric_correlations.pearson %}
                <h3 class="font-bold mb-4 uppercase">Numeric (Pearson - Top Pairs)</h3>
                <div class="overflow-x-auto mb-6">
                    <table class="w-full border-4 border-black">
                        <thead class="bg-black text-white">
                            <tr>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Feature 1</th>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Feature 2</th>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Correlation</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white">
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
                                <td class="border-2 border-black px-3 py-2">{{ c1 }}</td>
                                <td class="border-2 border-black px-3 py-2">{{ c2 }}</td>
                                <td class="border-2 border-black px-3 py-2 font-mono">{{ "%.3f"|format(val) }}</td>
                            </tr>
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                {% if categorical_correlations %}
                <h3 class="font-bold mb-4 uppercase">Categorical (Cramer's V - Top Pairs)</h3>
                <div class="overflow-x-auto">
                    <table class="w-full border-4 border-black">
                        <thead class="bg-black text-white">
                            <tr>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Pair</th>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Value</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white">
                            {% for pair, val in categorical_correlations.items()|sort(attribute='1', reverse=True) %}
                            {% if loop.index <= 20 %}
                            <tr>
                                <td class="border-2 border-black px-3 py-2">{{ pair }}</td>
                                <td class="border-2 border-black px-3 py-2 font-mono">{{ "%.3f"|format(val) }}</td>
                            </tr>
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}
                {% else %}
                <p class="text-gray-600 italic">No correlation data available.</p>
                {% endif %}
            </div>
        </div>

        <!-- MISSING TAB -->
        <div x-show="activeTab === 'missing'" {% if not pdf_mode %}x-cloak{% endif %}>
            <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Missing</h2>
            <div class="brutal-card">
                {% if missing_plots.missing_bar or missing_plots.missing_heatmap %}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {% if missing_plots.missing_bar %}
                    <div>
                        <h3 class="font-bold mb-2">COUNTS</h3>
                        <img src="data:image/png;base64,{{ missing_plots.missing_bar }}" class="w-full h-auto" />
                    </div>
                    {% endif %}
                    {% if missing_plots.missing_heatmap %}
                    <div>
                        <h3 class="font-bold mb-2">PATTERN</h3>
                        <img src="data:image/png;base64,{{ missing_plots.missing_heatmap }}" class="w-full h-auto" />
                    </div>
                    {% endif %}
                </div>
                {% else %}
                <h3 class="font-bold mb-4 uppercase">Missing Values by Column</h3>
                <div class="overflow-x-auto">
                    <table class="w-full border-4 border-black">
                        <thead class="bg-black text-white">
                            <tr>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Column</th>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Count</th>
                                <th class="border-2 border-black px-3 py-2 text-left font-bold uppercase">Percentage</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white">
                            {% for col, count in missing_values.count.items()|sort(attribute='1', reverse=True) %}
                            {% if count > 0 %}
                            <tr>
                                <td class="border-2 border-black px-3 py-2 font-bold">{{ col }}</td>
                                <td class="border-2 border-black px-3 py-2">{{ count }}</td>
                                <td class="border-2 border-black px-3 py-2 font-mono">{{ "%.2f"|format(missing_values.percentage[col]) }}%</td>
                            </tr>
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- SAMPLE TAB -->
        <div x-show="activeTab === 'sample'" {% if not pdf_mode %}x-cloak{% endif %}>
            <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Sample</h2>
            <div class="space-y-6">
                <div class="brutal-card">
                    <h3 class="font-bold uppercase mb-2 border-b-2 border-black pb-1">Head (first 5 rows)</h3>
                    <div class="overflow-x-auto">{{ head_table | safe }}</div>
                </div>
                <div class="brutal-card">
                    <h3 class="font-bold uppercase mb-2 border-b-2 border-black pb-1">Random Sample (10 rows)</h3>
                    <div class="overflow-x-auto">{{ sample_table | safe }}</div>
                </div>
                <div class="brutal-card">
                    <h3 class="font-bold uppercase mb-2 border-b-2 border-black pb-1">Tail (last 5 rows)</h3>
                    <div class="overflow-x-auto">{{ tail_table | safe }}</div>
                </div>
            </div>
        </div>
        {% endif %}

        <footer class="text-center font-black uppercase mt-12">
            *** HashPrep ::: Dataset Debugger ***
        </footer>
    </div>

    <script>
        const configData = {{ config_json | safe }};

        function downloadConfig() {
            const blob = new Blob([JSON.stringify(configData, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'hashprep_config.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
"""
