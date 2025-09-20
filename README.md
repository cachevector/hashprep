<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/hashprep-wobg.svg" width="100">
    <img alt="HashPrep Logo" src="docs/assets/hashprep-dark.svg" width="100">
  </picture>

  <h1>HashPrep</h1>
  <p>
    <b> Dataset Profiler & Debugger for Machine Learning </b>
  </p>

  <p align="center">
    <!-- Distribution -->
    <!-- <img src="https://img.shields.io/pypi/v/hashprep?color=blue&label=PyPI" /> -->
    <img src="https://img.shields.io/badge/PyPI-Coming%20Soon-blue" />
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
- **Automated Preparation**: Get suggestions for encoding, imputation, scaling, and transformations, and optionally apply them automatically.
- **Rich Reporting**: Generate statistical summaries and exportable reports for collaboration.
- **Production-Ready Pipelines**: Output reproducible cleaning and preprocessing code that integrates seamlessly with ML workflows.

HashPrep turns dataset debugging into a guided, automated process - saving time, improving model reliability, and standardizing best practices across teams.

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
