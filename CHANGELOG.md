# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-22

### Added
- First official stable release.
- Comprehensive dataset profiling and health checks.
- Support for multiple report formats: Markdown, JSON, HTML, and PDF.
- Two HTML report themes: `minimal` and `neubrutalism`.
- Automatic suggestion provider for data quality issues.
- Code generation for pandas fix scripts.
- Sklearn preprocessing pipeline generation.
- CLI commands: `scan`, `details`, `report`, `checks`, and `version`.
- Robust error handling for invalid files, empty datasets, and malformed configurations.
- Configuration support via YAML, TOML, and JSON.
- Intelligent sampling for large datasets.
- Dataset drift detection.
- Mutual information and statistical checks.

### Changed
- Refactored report generators for robust lazy loading.
- Improved CLI output with better error messages and color-coded statuses.
- Updated documentation and website for stable release.

### Fixed
- Fixed crash when generating reports for single-row datasets.
- Fixed dependency issues in report generation when optional libraries are missing.
- Fixed non-deterministic order in generated fix scripts.

## [0.1.0b3] - 2026-04-15
- Initial beta release with core features.
