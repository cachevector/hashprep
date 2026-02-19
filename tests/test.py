#!/usr/bin/env python3

import pandas as pd

import hashprep
from hashprep import DatasetAnalyzer

TARGET_COLUMN = "Survived"
VALID_CHECKS = DatasetAnalyzer.ALL_CHECKS

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
