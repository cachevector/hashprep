import json
from datetime import datetime
from typing import Dict

import numpy as np

import hashprep


def json_numpy_handler(obj):
    if hasattr(obj, "tolist"):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class JsonReport:
    def generate(self, summary, full=False, output_file=None):
        dataset_info = summary["summaries"]["dataset_info"]
        reproduction_info = summary["summaries"].get("reproduction_info", {})

        report: Dict = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "version": hashprep.__version__,
            },
            "dataset_overview": {
                "statistics": {
                    "variables": dataset_info["columns"],
                    "observations": dataset_info["rows"],
                    "missing_cells": dataset_info["missing_cells"],
                    "missing_percentage": dataset_info["missing_percentage"],
                    "duplicate_rows": dataset_info.get("duplicate_rows", 0),
                    "duplicate_percentage": dataset_info.get("duplicate_percentage", 0),
                    "memory_bytes": dataset_info.get("memory_bytes", 0),
                    "memory_kib": dataset_info.get("memory_kib", 0),
                    "average_record_size_bytes": dataset_info.get("average_record_size_bytes", 0),
                },
                "variable_types": summary["summaries"].get("variable_type_counts", {}),
            },
            "alerts": {
                "critical_count": summary["critical_count"],
                "warning_count": summary["warning_count"],
                "total": summary["total_issues"],
                "issues": summary["issues"],
            },
            "reproduction": {
                "analysis_started": reproduction_info.get("analysis_started"),
                "analysis_finished": reproduction_info.get("analysis_finished"),
                "duration_seconds": reproduction_info.get("duration_seconds"),
                "software_version": reproduction_info.get("software_version"),
                "dataset_hash": reproduction_info.get("dataset_hash"),
            },
        }

        if full:
            report["variables"] = summary["summaries"].get("variables", {})
            report["correlations"] = {
                "numeric": summary["summaries"].get("numeric_correlations", {}),
                "categorical": summary["summaries"].get("categorical_correlations", {}),
                "mixed": summary["summaries"].get("mixed_correlations", {}),
            }
            report["missing_values"] = summary["summaries"].get("missing_values", {})
            report["column_types"] = summary.get("column_types", {})
            report["sample_data"] = {
                "head": summary["summaries"].get("head", []),
                "tail": summary["summaries"].get("tail", []),
                "sample": summary["summaries"].get("sample", []),
            }

        json_content = json.dumps(report, indent=2, default=json_numpy_handler)
        if output_file:
            with open(output_file, "w") as f:
                f.write(json_content)
        return json_content
