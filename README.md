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

> [!WARNING]  
> This repository is under active development and may not be stable.

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

## Usage

### 1. Quick Scan
Get a quick summary of critical issues in your terminal.
```bash
hashprep scan dataset.csv
```

### 2. Generate Report
Generate a comprehensive HTML report with visualizations.
```bash
hashprep report dataset.csv --format html --theme minimal
```

**Options:**
- `--theme`: `minimal` (default) or `neubrutalism`
- `--format`: `html`, `pdf`, `md`, or `json`
- `--no-visualizations`: Disable plot generation for faster performance.

### 3. Generate Fixes
Automatically generate a Python script (`dataset_fixes.py`) to apply suggested fixes.
```bash
hashprep report dataset.csv --with-code
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
