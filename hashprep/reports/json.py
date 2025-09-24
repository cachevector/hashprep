import numpy as np
import json

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
        report = summary.copy()
        if not full:
            report.pop('summaries', None)
        json_content = json.dumps(report, indent=2, default=json_numpy_handler)
        if output_file:
            with open(output_file, "w") as f:
                f.write(json_content)
        return json_content