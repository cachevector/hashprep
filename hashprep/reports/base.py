"""Base report class with shared logic for all report renderers."""


class BaseReport:
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

    def _group_alerts_by_type(self, issues: list[dict]) -> dict[str, list[dict]]:
        """Group issues into display categories for the alerts section."""
        groups: dict[str, list[dict]] = {}
        for issue in issues:
            alert_type = self.ALERT_TYPE_MAPPING.get(issue["category"], "Other")
            if alert_type not in groups:
                groups[alert_type] = []
            groups[alert_type].append(issue)
        return groups
