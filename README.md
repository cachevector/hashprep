<div align="center">
  <picture>
    <img src="https://raw.githubusercontent.com/cachevector/hashprep/refs/heads/main/docs/assets/hashprep-wobg.svg" width="80">
  </picture>

  <h1>HashPrep</h1>
  <p>
    <b> Dataset Profiler & Debugger for Machine Learning </b>
  </p>

  <p align="center">
    <!-- Distribution -->
    <img src="https://img.shields.io/pypi/v/hashprep?color=blue&label=PyPI" />
    <!-- <img src="https://img.shields.io/badge/PyPI-Coming%20Soon-blue" /> -->
    <!-- License -->
    <img src="https://img.shields.io/badge/License-MIT-green" />
    <img src="https://img.shields.io/badge/CLI-Supported-orange" />
  </p>
  <p>
    <!-- Features -->
    <img src="https://img.shields.io/badge/Feature-Dataset%20Quality%20Assurance-critical" />
    <img src="https://img.shields.io/badge/Feature-Preprocessing%20%2B%20Profiling-blueviolet" />
    <img src="https://img.shields.io/badge/Feature-Report%20Generation-3f4f75" />
    <img src="https://img.shields.io/badge/Feature-Quick%20Fixes-success" />
  </p>
</div>

> [!NOTE]
> HashPrep is now in **beta** (v0.1.0b1). Core features are stable and tested, but the API may still evolve based on community feedback. Ready for testing in real-world ML workflows.

## Overview

**HashPrep** is a Python library for intelligent dataset profiling and debugging that acts as a comprehensive pre-training quality assurance tool for machine learning projects.
Think of it as **"Pandas Profiling + PyLint for datasets"**, designed specifically for machine learning workflows.

It catches critical dataset issues before they derail your ML pipeline, explains the problems, and suggests context-aware fixes.  
If you want, HashPrep can even apply those fixes for you automatically.


---

## Features

Key features include:

- **Intelligent Profiling**: Detect missing values, skewed distributions, outliers, and data type inconsistencies.
- **ML-Specific Checks**: Identify data leakage, dataset drift, class imbalance, and high-cardinality features.
- **Automated Preparation**: Get suggestions for encoding, imputation, scaling, and transformations.
- **Rich Reporting**: Generate statistical summaries and exportable reports (HTML/PDF/Markdown/JSON) with embedded visualizations.
- **Production-Ready Pipelines**: Output reproducible cleaning and preprocessing code (`fixes.py`) that integrates seamlessly with ML workflows.
- **Modern Themes**: Choose between "Minimal" (professional) and "Neubrutalism" (bold) report styles.

---

## Installation

### Using pip
```bash
pip install hashprep
```

### Using uv (recommended)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install hashprep
uv pip install hashprep

# Or for development from source
git clone https://github.com/cachevector/hashprep.git
cd hashprep
uv sync
```

After installation, the `hashprep` command will be available directly in your terminal.

---

## Usage

HashPrep can be used both as a **command-line tool** and as a **Python library**.

### CLI Usage

#### 1. Quick Scan
Get a quick summary of critical issues in your terminal.
```bash
hashprep scan dataset.csv
```

**Options:**
- `--critical-only`: Show only critical issues
- `--quiet`: Minimal output (counts only)
- `--json`: Output in JSON format
- `--target COLUMN`: Specify target column for ML-specific checks
- `--checks CHECKS`: Run specific checks (comma-separated)
- `--sample-size N`: Limit analysis to N rows
- `--no-sample`: Disable automatic sampling

**Example:**
```bash
# Scan with target column and specific checks
hashprep scan train.csv --target Survived --checks outliers,high_missing_values,class_imbalance

# Quick scan with JSON output
hashprep scan dataset.csv --json --quiet
```

#### 2. Detailed Analysis
Get comprehensive details about all detected issues.
```bash
hashprep details dataset.csv
```

**Options:** Same as `scan` command

**Example:**
```bash
hashprep details train.csv --target Survived
```

#### 3. Generate Reports
Generate comprehensive reports in multiple formats with visualizations.
```bash
hashprep report dataset.csv --format html --theme minimal
```

**Options:**
- `--format {md,json,html,pdf}`: Report format (default: md)
- `--theme {minimal,neubrutalism}`: HTML report theme (default: minimal)
- `--with-code`: Generate Python scripts for fixes and pipelines
- `--full` / `--no-full`: Include/exclude full summaries (default: True)
- `--visualizations` / `--no-visualizations`: Include/exclude plots (default: True)
- `--target COLUMN`: Specify target column
- `--checks CHECKS`: Run specific checks
- `--comparison FILE`: Compare with another dataset for drift detection
- `--sample-size N`: Limit analysis to N rows
- `--no-sample`: Disable automatic sampling

**Examples:**
```bash
# Generate HTML report with minimal theme
hashprep report dataset.csv --format html --theme minimal --full

# Generate PDF report without visualizations (faster)
hashprep report dataset.csv --format pdf --no-visualizations

# Generate report with automatic fix scripts
hashprep report dataset.csv --with-code

# This creates:
# - dataset_hashprep_report.md (or .html/.pdf/.json)
# - dataset_hashprep_report_fixes.py (pandas script)
# - dataset_hashprep_report_pipeline.py (sklearn pipeline)

# Compare two datasets for drift detection
hashprep report train.csv --comparison test.csv --format html
```

#### 4. Version
Check HashPrep version.
```bash
hashprep version
```

#### Available Checks
- `outliers` - Detect outliers using IQR method
- `duplicates` - Find duplicate rows
- `high_missing_values` - Columns with >50% missing data
- `dataset_missingness` - Overall missing data patterns
- `high_cardinality` - Categorical columns with too many unique values
- `single_value_columns` - Constant columns with no variance
- `class_imbalance` - Imbalanced target variable (requires --target)
- `feature_correlation` - Highly correlated features
- `target_leakage` - Features that may leak target information
- `dataset_drift` - Distribution drift between datasets (requires --comparison)
- `uniform_distribution` - Uniformly distributed numeric columns
- `unique_values` - Columns where >95% values are unique
- `many_zeros` - Columns with excessive zero values

---

### Python Library Usage

#### Basic Analysis
```python
import pandas as pd
from hashprep import DatasetAnalyzer

# Load your dataset
df = pd.read_csv("dataset.csv")

# Create analyzer
analyzer = DatasetAnalyzer(df)

# Run analysis
summary = analyzer.analyze()

# Access results
print(f"Critical issues: {summary['critical_count']}")
print(f"Warnings: {summary['warning_count']}")

# Iterate through issues
for issue in summary['issues']:
    print(f"{issue['severity']}: {issue['description']}")
```

#### Analysis with Target Column
```python
# Specify target for ML-specific checks
analyzer = DatasetAnalyzer(
    df,
    target_col='target_column'
)
summary = analyzer.analyze()
```

#### Run Specific Checks
```python
# Only run specific checks
analyzer = DatasetAnalyzer(
    df,
    selected_checks=['outliers', 'high_missing_values', 'class_imbalance']
)
summary = analyzer.analyze()
```

#### Include Visualizations
```python
# Generate analysis with plots
analyzer = DatasetAnalyzer(df, include_plots=True)
summary = analyzer.analyze()

# Plots are stored in summary['summaries']['plots']
```

#### Drift Detection
```python
# Compare two datasets
train_df = pd.read_csv("train.csv")
test_df = pd.read_csv("test.csv")

analyzer = DatasetAnalyzer(
    train_df,
    comparison_df=test_df,
    selected_checks=['dataset_drift']
)
summary = analyzer.analyze()
```

#### Generate Reports Programmatically
```python
from hashprep.reports import generate_report

# Analyze dataset
analyzer = DatasetAnalyzer(df, include_plots=True)
summary = analyzer.analyze()

# Generate HTML report
generate_report(
    summary,
    format='html',
    full=True,
    output_file='report.html',
    theme='minimal'
)

# Generate PDF report
generate_report(
    summary,
    format='pdf',
    full=True,
    output_file='report.pdf'
)

# Generate JSON report
generate_report(
    summary,
    format='json',
    full=True,
    output_file='report.json'
)

# Generate Markdown report
generate_report(
    summary,
    format='md',
    full=True,
    output_file='report.md'
)
```

#### Generate Fix Scripts
```python
from hashprep.checks.core import Issue
from hashprep.preparers.codegen import CodeGenerator
from hashprep.preparers.pipeline_builder import PipelineBuilder
from hashprep.preparers.suggestions import SuggestionProvider

# After running analysis
analyzer = DatasetAnalyzer(df, target_col='target')
summary = analyzer.analyze()

# Convert issues to proper format
issues = [Issue(**i) for i in summary['issues']]
column_types = summary.get('column_types', {})

# Get suggestions
provider = SuggestionProvider(
    issues=issues,
    column_types=column_types,
    target_col='target'
)
suggestions = provider.get_suggestions()

# Generate pandas fix script
codegen = CodeGenerator(suggestions)
fixes_code = codegen.generate_pandas_script()
with open('fixes.py', 'w') as f:
    f.write(fixes_code)

# Generate sklearn pipeline
builder = PipelineBuilder(suggestions)
pipeline_code = builder.generate_pipeline_code()
with open('pipeline.py', 'w') as f:
    f.write(pipeline_code)
```

#### Custom Sampling
```python
from hashprep.utils.sampling import SamplingConfig

# Configure sampling for large datasets
sampling_config = SamplingConfig(max_rows=10000)

analyzer = DatasetAnalyzer(
    df,
    sampling_config=sampling_config,
    auto_sample=True
)
summary = analyzer.analyze()

# Check if sampling occurred
if 'sampling_info' in summary:
    info = summary['sampling_info']
    print(f"Sampled: {info['sample_fraction']*100:.1f}%")
```

---

## License

This project is licensed under the [**MIT License**](./LICENSE).

---

## Contributing

We welcome contributions from the community to make HashPrep better!

Before you get started, please:

- Review our [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines and setup instructions
- Write clean, well-documented code
- Follow best practices for the stack or component you’re working on
- Open a pull request (PR) with a clear description of your changes and motivation
