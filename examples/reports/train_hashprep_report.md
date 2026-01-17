# Dataset Quality Report

Generated: 2026-01-17 17:50:01  
HashPrep Version: 0.1.0a1

## Executive Summary
- Total Issues: 15
- Critical Issues: 2
- Warnings: 13
- Rows: 891
- Columns: 12

## Issues Overview

| Category | Severity | Column | Description | Impact | Quick Fix |
|----------|----------|--------|-------------|--------|-----------|
| missing_values | critical | Cabin | 77.1% missing values in 'Cabin' | high | Options:  • Drop column: Reduces bias from missing data (Pros: Simplifies model; Cons: Loses potential info). • Impute values: Use domain-informed methods (e.g., median, mode, or predictive model) (Pros: Retains feature; Cons: May introduce bias). • Create missingness indicator: Flag missing values as a new feature (Pros: Captures missingness pattern; Cons: Adds complexity). |
| high_cardinality | critical | Name | Column 'Name' has 891 unique values (100.0% of rows) | high | Options:  • Drop column: Avoids overfitting from unique identifiers (Pros: Simplifies model; Cons: Loses potential info). • Engineer feature: Extract patterns (e.g., titles from names) (Pros: Retains useful info; Cons: Requires domain knowledge). • Use hashing: Reduce dimensionality (Pros: Scalable; Cons: May lose interpretability). |
| high_cardinality | warning | Ticket | Column 'Ticket' has 681 unique values (76.4% of rows) | medium | Options:  • Group rare categories: Reduce cardinality (Pros: Simplifies feature; Cons: May lose nuance). • Use feature hashing: Map to lower dimensions (Pros: Scalable; Cons: Less interpretable). • Retain and test: Evaluate feature importance (Pros: Data-driven; Cons: Risk of overfitting). |
| high_cardinality | warning | Cabin | Column 'Cabin' has 147 unique values (16.5% of rows) | medium | Options:  • Group rare categories: Reduce cardinality (Pros: Simplifies feature; Cons: May lose nuance). • Use feature hashing: Map to lower dimensions (Pros: Scalable; Cons: Less interpretable). • Retain and test: Evaluate feature importance (Pros: Data-driven; Cons: Risk of overfitting). |
| outliers | warning | SibSp | Column 'SibSp' has 12 potential outliers (1.3% of non-missing values) | medium | Options:  • Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming). • Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| outliers | warning | Parch | Column 'Parch' has 10 potential outliers (1.1% of non-missing values) | medium | Options:  • Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming). • Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| outliers | warning | Fare | Column 'Fare' has 11 potential outliers (1.2% of non-missing values) | medium | Options:  • Investigate outliers: Verify if valid or errors (Pros: Ensures accuracy; Cons: Time-consuming). • Transform: Use log/sqrt to reduce impact (Pros: Retains data; Cons: Changes interpretation). • Retain and test: Use robust models (e.g., trees) (Pros: Keeps info; Cons: May affect sensitive models). |
| high_zero_counts | warning | Survived | Column 'Survived' has 61.6% zero values | medium | Options:  • Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results). • Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming). |
| high_zero_counts | warning | SibSp | Column 'SibSp' has 68.2% zero values | medium | Options:  • Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results). • Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming). |
| high_zero_counts | warning | Parch | Column 'Parch' has 76.1% zero values | medium | Options:  • Transform: Create binary indicator for zeros (Pros: Captures pattern; Cons: Adds complexity). • Retain and test: Evaluate with robust models (Pros: Keeps info; Cons: May skew results). • Investigate zeros: Verify validity (Pros: Ensures accuracy; Cons: Time-consuming). |
| missing_patterns | warning | Age | Missingness in 'Age' correlates with 6 columns (Pclass, Parch, Embarked) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| missing_patterns | warning | Cabin | Missingness in 'Cabin' correlates with 6 columns (Pclass, Fare, Survived) | medium | Options:  • Impute values: Use simple or domain-informed methods (Pros: Retains feature; Cons: Risk of bias). • Drop column: If less critical (Pros: Simplifies model; Cons: Loses info). • Test impact: Evaluate model with/without feature (Pros: Data-driven; Cons: Requires computation). |
| skewness | warning | SibSp | Column 'SibSp' is highly skewed (skewness: 3.70) | medium | Options:  • Square root transform: Reduces moderate skew. • Monitor: Evaluate model performance on skewed data. |
| skewness | warning | Fare | Column 'Fare' is highly skewed (skewness: 4.79) | medium | Options:  • Square root transform: Reduces moderate skew. • Monitor: Evaluate model performance on skewed data. |
| feature_correlation | warning | Survived,Sex | Categorical columns 'Survived' and 'Sex' highly associated (Cramer's V: 0.540) | medium | Options:  • Monitor redundancy.  • Re-encode. |

## Next Steps
- Address critical issues by following fix suggestions
- Generate Reproducible Code: Run `hashprep report <dataset> --with-code` to get a `fixes.py` script
- Refine Dataset: Apply suggested transformations and re-analyze

---
Generated by HashPrep