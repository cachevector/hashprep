import json
from datetime import datetime

import pandas as pd
import yaml
from jinja2 import Template

import hashprep


class HtmlReport:
    def generate(self, summary, full=False, output_file=None, theme="minimal"):
        template_str = self._get_template(theme)
        template = Template(template_str)

        head_df = pd.DataFrame(summary["summaries"]["head"])
        tail_df = pd.DataFrame(summary["summaries"]["tail"])
        sample_df = pd.DataFrame(summary["summaries"]["sample"])

        context = {
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "critical_count": summary["critical_count"],
            "warning_count": summary["warning_count"],
            "total_issues": summary["total_issues"],
            "rows": summary["summaries"]["dataset_info"]["rows"],
            "columns": summary["summaries"]["dataset_info"]["columns"],
            "issues": summary["issues"],
            "full": full,
            "head_table": head_df.to_html(
                index=False, classes="min-w-full divide-y divide-gray-200"
            ),
            "tail_table": tail_df.to_html(
                index=False, classes="min-w-full divide-y divide-gray-200"
            ),
            "sample_table": sample_df.to_html(
                index=False, classes="min-w-full divide-y divide-gray-200"
            ),
            "variables": summary["summaries"].get("variables", {}),
            "numeric_correlations": summary["summaries"].get(
                "numeric_correlations", {}
            ),
            "categorical_correlations": summary["summaries"].get(
                "categorical_correlations", {}
            ),
            "mixed_correlations": summary["summaries"].get("mixed_correlations", {}),
            "missing_values": summary["summaries"].get("missing_values", {}),
            "missing_patterns": summary["summaries"].get("missing_patterns", {}),
            "yaml_dump": yaml.safe_dump,
            "json_dump": lambda x: json.dumps(x, indent=2),
            "version": hashprep.__version__,
        }

        html_content = template.render(context)
        if output_file:
            with open(output_file, "w") as f:
                f.write(html_content)
        return html_content

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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        code, pre { font-family: 'JetBrains Mono', monospace; }
        .table-container table { min-width: 100%; border-collapse: collapse; }
        .table-container th { padding: 0.75rem 1.5rem; background-color: #f9fafb; text-align: left; font-size: 0.75rem; font-weight: 500; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
        .table-container td { padding: 1rem 1.5rem; white-space: nowrap; font-size: 0.875rem; color: #111827; border-bottom: 1px solid #f3f4f6; }
    </style>
</head>
<body class="bg-white text-gray-900 antialiased">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header class="mb-12 border-b border-gray-100 pb-8">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Dataset Quality Report</h1>
                    <p class="mt-2 text-sm text-gray-500">Generated on {{ generated }} • HashPrep v{{ version }}</p>
                </div>
                <div class="flex space-x-4">
                    <div class="bg-red-50 px-4 py-2 rounded-lg border border-red-100">
                        <span class="block text-xs font-medium text-red-600 uppercase">Critical</span>
                        <span class="text-2xl font-bold text-red-700">{{ critical_count }}</span>
                    </div>
                    <div class="bg-amber-50 px-4 py-2 rounded-lg border border-amber-100">
                        <span class="block text-xs font-medium text-amber-600 uppercase">Warnings</span>
                        <span class="text-2xl font-bold text-amber-700">{{ warning_count }}</span>
                    </div>
                </div>
            </div>
        </header>

        <section class="mb-12">
            <h2 class="text-xl font-semibold mb-6">Issues Overview</h2>
            <div class="overflow-hidden border border-gray-200 rounded-xl">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Column</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fix Suggestion</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {% for issue in issues %}
                        <tr class="hover:bg-gray-50 transition-colors">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 py-1 text-xs font-medium rounded-full
                                    {% if issue.severity == 'critical' %} bg-red-100 text-red-800 {% else %} bg-amber-100 text-amber-800 {% endif %}">
                                    {{ issue.category | replace('_', ' ') | capitalize }}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ issue.column }}</td>
                            <td class="px-6 py-4 text-sm text-gray-600">{{ issue.description }}</td>
                            <td class="px-6 py-4 text-sm text-gray-500 italic">{{ issue.quick_fix | replace('\\n', '<br>') | safe }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </section>

        {% if full %}
        <section class="mb-12">
            <h2 class="text-xl font-semibold mb-6">Dataset Profile</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="p-6 bg-gray-50 rounded-xl border border-gray-100">
                    <span class="text-xs font-medium text-gray-500 uppercase">Rows</span>
                    <span class="block text-2xl font-bold">{{ rows }}</span>
                </div>
                <div class="p-6 bg-gray-50 rounded-xl border border-gray-100">
                    <span class="text-xs font-medium text-gray-500 uppercase">Columns</span>
                    <span class="block text-2xl font-bold">{{ columns }}</span>
                </div>
                <div class="p-6 bg-gray-50 rounded-xl border border-gray-100">
                    <span class="text-xs font-medium text-gray-500 uppercase">Total Issues</span>
                    <span class="block text-2xl font-bold">{{ total_issues }}</span>
                </div>
            </div>

            <div class="space-y-8">
                <div>
                    <h3 class="text-lg font-medium mb-4">Sample Data</h3>
                    <div class="table-container overflow-x-auto border border-gray-200 rounded-xl">
                        {{ head_table | safe }}
                    </div>
                </div>
            </div>
        </section>
        {% endif %}

        <footer class="mt-20 pt-8 border-t border-gray-100 text-center">
            <p class="text-sm text-gray-400">Built with HashPrep • Open Source Dataset QA</p>
        </footer>
    </div>
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
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'JetBrains Mono', monospace; }
        .brutal-card { border: 4px solid black; box-shadow: 8px 8px 0px 0px rgba(0,0,0,1); background-color: white; padding: 1.5rem; }
        .brutal-table th { border: 4px solid black; background-color: #fde047; padding: 0.75rem; text-align: left; font-weight: bold; }
        .brutal-table td { border: 4px solid black; padding: 0.75rem; }
    </style>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-7xl mx-auto">
        <header class="brutal-card mb-8 flex justify-between items-center bg-white">
            <div>
                <h1 class="text-4xl font-black uppercase italic">HashPrep // Report</h1>
                <p class="font-bold mt-2">DATE: {{ generated }} | VERSION: {{ version }}</p>
            </div>
            <div class="flex gap-4">
                <div class="brutal-card bg-red-400 py-2 px-4">
                    <span class="font-black text-2xl">CRIT: {{ critical_count }}</span>
                </div>
                <div class="brutal-card bg-orange-300 py-2 px-4">
                    <span class="font-black text-2xl">WARN: {{ warning_count }}</span>
                </div>
            </div>
        </header>

        <section class="mb-12">
            <h2 class="text-2xl font-black uppercase mb-4 bg-black text-white inline-block px-4 py-1">Issues</h2>
            <div class="overflow-x-auto">
                <table class="w-full brutal-table border-collapse">
                    <thead>
                        <tr>
                            <th>CATEGORY</th>
                            <th>COL</th>
                            <th>DESCRIPTION</th>
                            <th>FIX</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white">
                        {% for issue in issues %}
                        <tr>
                            <td class="font-bold {% if issue.severity == 'critical' %} bg-red-200 {% else %} bg-orange-100 {% endif %}">
                                {{ issue.category | upper }}
                            </td>
                            <td class="font-bold">{{ issue.column }}</td>
                            <td>{{ issue.description }}</td>
                            <td class="text-sm italic">{{ issue.quick_fix }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </section>

        <footer class="text-center font-black uppercase mt-12">
            *** HashPrep ::: Dataset Debugger ***
        </footer>
    </div>
</body>
</html>
"""
