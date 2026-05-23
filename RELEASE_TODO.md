# HashPrep Official Release TODO

## Release Scope

- [x] Decide the official version target, likely `0.1.0` unless the release should signal `1.0.0`.
- [x] Freeze public API expectations for `DatasetAnalyzer`.
- [x] Freeze public API expectations for `HashPrepConfig`.
- [x] Freeze public API expectations for `load_config`.
- [x] Freeze public API expectations for `generate_report`.
- [x] Freeze CLI behavior for `scan`, `details`, `report`, and `version`.
- [x] Define what is stable versus experimental, especially auto-fixes, generated pipelines, report themes, and statistical checks.

## Code Readiness

- [x] Run the full test suite across Python `3.10`, `3.11`, and `3.12`.
- [x] Run lint checks.
- [x] Run format checks.
- [x] Add or verify tests for CLI error handling.
- [x] Add or verify tests for invalid check names.
- [x] Add or verify tests for report generation in `md`, `json`, `html`, and `pdf`.
- [x] Add or verify tests for generated `fixes.py` code.
- [x] Add or verify tests for generated sklearn pipeline code.
- [x] Add or verify tests for config loading from YAML, TOML, and JSON.
- [x] Add or verify tests for large dataset sampling behavior.
- [x] Verify empty CSV behavior.
- [x] Verify duplicate column behavior.
- [x] Verify missing target column behavior.
- [x] Verify non-numeric target behavior for mutual information and statistical checks.
- [x] Verify datasets with infinities, all-null columns, and mixed types.
- [x] Verify reports do not crash when plots are disabled.
- [x] Verify reports do not crash when optional summary data is missing.

## Functionality Readiness

### Must Improve Before Stable

- [x] Improve CLI error handling for invalid files.
- [x] Improve CLI error handling for empty CSVs.
- [x] Improve CLI error handling for bad target columns.
- [x] Improve CLI error handling for bad config files.
- [x] Improve CLI error handling for unsupported report formats.
- [x] Improve CLI error handling for failed PDF generation.
- [x] Ensure CLI failures produce clear user-facing messages.
- [x] Ensure HTML reports work when no issues are found.
- [x] Ensure PDF reports work when no issues are found.
- [x] Ensure Markdown reports work when no issues are found.
- [x] Ensure JSON reports work when no issues are found.
- [x] Ensure all report formats work when plots are disabled.
- [x] Ensure all report formats work for tiny datasets.
- [x] Ensure all report formats work for mostly missing datasets.
- [x] Ensure all report formats work when optional summaries are absent.
- [x] Verify generated fix scripts are deterministic.
- [x] Verify generated fix scripts are valid Python.
- [x] Verify generated sklearn pipeline code is deterministic.
- [x] Verify generated sklearn pipeline code is valid Python.
- [x] Add tests that execute generated fix scripts where practical.
- [x] Add tests that execute generated sklearn pipeline code where practical.
- [x] Clearly label generated fixes as suggestions if they are heuristic or incomplete.
- [x] Add config validation for unknown keys.
- [x] Add config validation for wrong value types.
- [x] Add clear errors for malformed YAML, TOML, and JSON config files.
- [x] Confirm threshold behavior is predictable and documented.
- [x] Decide whether summary dictionary shapes are part of the stable public API.
- [x] Document stable summary keys if summary dictionaries are part of the public API.

### Strongly Recommended

- [x] Add an `--output` option to `hashprep report`.
- [x] Allow `hashprep report data.csv --format html --output reports/data.html`.
- [x] Add machine-readable JSON output for `hashprep details`.
- [x] Add check discovery through a command such as `hashprep checks`.
- [x] Alternatively add check discovery through an option such as `hashprep scan --list-checks`.
- [x] Document why issues are classified as `critical` versus `warning`.
- [x] Review whether PDF/reporting dependencies should move to optional extras in a future release.
- [x] Document any dependency-extra plan if it is deferred.

### Not For This Stable Release

- [x] Avoid adding major new check families before the first stable release unless they fix a release blocker.
- [x] Avoid adding model integrations before the first stable release.
- [x] Avoid adding dashboard features before the first stable release.
- [x] Avoid expanding automatic dataset repair workflows before the first stable release.
- [x] Keep the first stable release focused on hardening existing behavior.

## Packaging

- [x] Update `hashprep/__init__.py` from `0.1.0b3` to the official release version.
- [x] Update the beta note in `README.md`.
- [x] Update the beta support table in `SECURITY.md`.
- [x] Add or verify PyPI classifiers in `pyproject.toml`.
- [x] Add or verify package keywords in `pyproject.toml`.
- [x] Add or verify project URLs in `pyproject.toml`.
- [x] Add or verify Python version classifiers in `pyproject.toml`.
- [x] Add or verify license metadata in `pyproject.toml`.
- [x] Build source distribution.
- [x] Build wheel distribution.
- [x] Inspect built package artifacts.
- [x] Install the built wheel in a clean environment.
- [x] Smoke test `import hashprep` from the built wheel.
- [x] Smoke test `hashprep version` from the built wheel.
- [x] Smoke test `hashprep scan datasets/train.csv` from the built wheel.
- [x] Smoke test `hashprep report datasets/train.csv --format html` from the built wheel.
- [x] Confirm `MANIFEST.in` excludes dev/demo files intentionally.
- [x] Confirm `MANIFEST.in` includes all runtime files needed by reports and templates.

## Documentation

- [x] Replace beta references in `README.md`.
- [x] Replace beta references in `SECURITY.md`.
- [x] Replace beta references in `web/src/lib/components/Hero.svelte`.
- [x] Add `CHANGELOG.md`.
- [x] Add first official release notes.
- [x] Document available checks in release notes.
- [x] Document CLI commands in release notes.
- [x] Document report formats in release notes.
- [x] Document known limitations in release notes.
- [x] Document upgrade notes from beta.
- [x] Verify README examples run exactly as written.
- [x] Update the documentation URL in `pyproject.toml` if a dedicated docs page is available.
- [x] Refresh generated example reports under `examples/reports/` if needed.

## CI/CD

- [x] Add package build validation to CI.
- [x] Add `twine check` or equivalent artifact validation to CI.
- [x] Add built-wheel install smoke test to CI.
- [x] Add CLI smoke test against the built wheel to CI.
- [x] Add website build check for `web/`.
- [x] Add or verify release workflow triggered by version tags.
- [x] Configure PyPI publishing, preferably with trusted publishing.
- [x] Configure GitHub release creation.
- [x] Consider adding dependency and security scanning for Python dependencies.
- [x] Consider adding dependency and security scanning for web dependencies.

## Security And Dependencies

- [x] Review pinned and minimum Python dependency versions.
- [x] Review pinned and minimum web dependency versions.
- [x] Confirm heavy dependencies are intentional, especially `weasyprint`, `matplotlib`, `seaborn`, and `scikit-learn`.
- [x] Decide whether PDF/report dependencies should remain core dependencies or move to optional extras in a future release.
- [x] Run vulnerability checks for Python dependencies.
- [x] Run vulnerability checks for web dependencies.
- [x] Update `SECURITY.md` to describe stable release support.

## Website

- [x] Update website beta badges.
- [x] Update website install examples.
- [x] Confirm the docs page matches the current README and API.
- [x] Build the static site successfully.
- [x] Verify PyPI link.
- [x] Verify GitHub link.
- [x] Verify docs link.
- [x] Verify license link.
- [x] Verify issue tracker link.
- [x] Decide deployment target for the docs site.
- [x] Decide release timing for the docs site.

## Release Process

- [x] Create a release branch.
- [x] Make version, docs, and changelog updates.
- [x] Run full validation locally.
- [x] Merge after CI passes.
- [x] Tag the release, for example `v0.1.0`.
- [x] Publish to PyPI.
- [x] Create GitHub release with release notes.
- [x] Verify public install with `pip install hashprep`.
- [x] Verify public CLI with `hashprep version`.
- [x] Announce the release as the first stable release after alpha and beta.

## Known Immediate Gaps

- [x] Version is still `0.1.0b3`.
- [x] `README.md` still says beta.
- [x] Website hero still says beta and shows `hashprep-0.1.0b3`.
- [x] `SECURITY.md` only describes beta support.
- [x] `CHANGELOG.md` is not present.
- [x] CI does not currently build or check publish artifacts.
- [x] CI does not currently build the Svelte website.
- [x] No release or publish workflow is present.
