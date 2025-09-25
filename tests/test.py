#!/usr/bin/env python3

import hashprep
import pandas as pd
from hashprep.analyzer import DatasetAnalyzer

TARGET_COLUMN = "Survived"
VALID_CHECKS = [
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

df = pd.read_csv("datasets/train.csv")

analyzer = DatasetAnalyzer(df, target_col=TARGET_COLUMN, selected_checks=VALID_CHECKS)
summary = analyzer.analyze()

issues = summary["issues"]
critical = [i for i in issues if i["severity"] == "critical"]
warnings = [i for i in issues if i["severity"] == "warning"]

print(hashprep.__version__)
print(issues)
print(critical)
print(warnings)
