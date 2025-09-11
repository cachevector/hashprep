<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/hashprep-wobg.svg" width="100">
    <img alt="Shows an illustrated sun in light color mode and a moon with stars in dark color mode." src="docs/hashprep-dark.svg" width="100">
  </picture>

  <h1>HashPrep</h1>
  <p>
    <b> Dataset Debugging Playground </b>
  </p>

  <p align="center">
    <!-- Deployment -->
    <img src="https://img.shields.io/badge/Web%20Version-Self%20Hosted-0A66C2" />
    <img src="https://img.shields.io/badge/CLI-Supported-orange" />
    <!-- Stack -->
    <img src="https://img.shields.io/badge/UI-Svelte-ff3e00?logo=svelte" />
    <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi" />
    <img src="https://img.shields.io/badge/DB-Postgres-336791?logo=postgresql" />
    <!-- License -->
    <img src="https://img.shields.io/badge/License-MIT-green" />
    <!-- Features -->
    <img src="https://img.shields.io/badge/Feature-Dataset%20Quality%20Assurance-critical" />
    <img src="https://img.shields.io/badge/Feature-Preprocessing%20%2B%20Profiling-blueviolet" />
    <img src="https://img.shields.io/badge/Feature-Report%20Generation-3f4f75" />
    <img src="https://img.shields.io/badge/Feature-AutoML%20Integration-success" />
  </p>
</div>

> [!WARNING]  
> This repository is under active development and may not be stable.

## Overview

**HashPrep** is an intelligent dataset debugging and preparation platform that acts as a comprehensive pre-training quality assurance tool for machine learning projects. Think of it as **"Pandas Profiling + ESLint + AutoML"** specifically designed for ML datasets.

The platform catches critical dataset issues before they derail your ML pipeline, automatically suggests fixes, and generates production-ready cleaning code - saving hours of manual data debugging and preparation work.

---

## Features

Key features include:

- **Intelligent Profiling**: Detect missing values, skewed distributions, outliers, and data type inconsistencies.
- **ML-Specific Checks**: Identify data leakage, dataset drift, class imbalance, and high-cardinality features.
- **Automated Preparation**: Get context-aware suggestions for encoding, imputation, scaling, and transformations.
- **Rich Reporting**: Generate interactive dashboards, statistical summaries, and exportable reports for collaboration.
- **Production-Ready Pipelines**: Automatically create reproducible cleaning and preprocessing code that integrates seamlessly with ML workflows.

HashPrep turns data debugging into a guided, automated process - saving time, improving model reliability, and standardizing best practices across teams.

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
