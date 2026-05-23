# HashPrep Official Release TODO

## Release Scope

- [x] Decide the official version target, likely `0.1.0` unless the release should signal `1.0.0`.
- [ ] Freeze public API expectations for `DatasetAnalyzer`.
- [ ] Freeze public API expectations for `HashPrepConfig`.
- [ ] Freeze public API expectations for `load_config`.
- [ ] Freeze public API expectations for `generate_report`.
- [x] Freeze CLI behavior for `scan`, `details`, `report`, and `version`.
- [ ] Define what is stable versus experimental, especially auto-fixes, generated pipelines, report themes, and statistical checks.

## Code Readiness

- [ ] Run the full test suite across Python `3.10`, `3.11`, and `3.12`.
- [ ] Run lint checks.
- [ ] Run format checks.
- [x] Add or verify tests for CLI error handling.
- [ ] Add or verify tests for invalid check names.
- [x] Add or verify tests for report generation in `md`, `json`, `html`, and `pdf`.
- [x] Add or verify tests for generated `fixes.py` code.
- [x] Add or verify tests for generated sklearn pipeline code.
- [x] Add or verify tests for config loading from YAML, TOML, and JSON.
- [ ] Add or verify tests for large dataset sampling behavior.
- [ ] Verify empty CSV behavior.
- [ ] Verify duplicate column behavior.
- [ ] Verify missing target column behavior.
- [ ] Verify non-numeric target behavior for mutual information and statistical checks.
- [ ] Verify datasets with infinities, all-null columns, and mixed types.
- [ ] Verify reports do not crash when plots are disabled.
- [ ] Verify reports do not crash when optional summary data is missing.

## Functionality Readiness

### Must Improve Before Stable

- [x] Improve CLI error handling for invalid files.
- [x] Improve CLI error handling for empty CSVs.
- [x] Improve CLI error handling for bad target columns.
- [x] Improve CLI error handling for bad config files.
- [x] Improve CLI error handling for unsupported report formats.
- [x] Improve CLI error handling for failed PDF generation.
- [x] Ensure CLI failures produce clear user-facing messages.
- [ ] Ensure HTML reports work when no issues are found.
- [ ] Ensure PDF reports work when no issues are found.
- [ ] Ensure Markdown reports work when no issues are found.
- [ ] Ensure JSON reports work when no issues are found.
- [ ] Ensure all report formats work when plots are disabled.
- [ ] Ensure all report formats work for tiny datasets.
- [ ] Ensure all report formats work for mostly missing datasets.
- [ ] Ensure all report formats work when optional summaries are absent.
- [x] Verify generated fix scripts are deterministic.
- [x] Verify generated fix scripts are valid Python.
- [x] Verify generated sklearn pipeline code is deterministic.
- [x] Verify generated sklearn pipeline code is valid Python.
- [x] Add tests that execute generated fix scripts where practical.
- [x] Add tests that execute generated sklearn pipeline code where practical.
- [ ] Clearly label generated fixes as suggestions if they are heuristic or incomplete.
- [x] Add config validation for unknown keys.
- [x] Add config validation for wrong value types.
- [x] Add clear errors for malformed YAML, TOML, and JSON config files.
- [ ] Confirm threshold behavior is predictable and documented.
- [ ] Decide whether summary dictionary shapes are part of the stable public API.
- [ ] Document stable summary keys if summary dictionaries are part of the public API.

### Strongly Recommended

- [x] Add an `--output` option to `hashprep report`.
- [x] Allow `hashprep report data.csv --format html --output reports/data.html`.
- [ ] Add machine-readable JSON output for `hashprep details`.
- [x] Add check discovery through a command such as `hashprep checks`.
- [x] Alternatively add check discovery through an option such as `hashprep scan --list-checks`.
- [ ] Document why issues are classified as `critical` versus `warning`.
- [ ] Review whether PDF/reporting dependencies should move to optional extras in a future release.
- [ ] Document any dependency-extra plan if it is deferred.

### Not For This Stable Release

- [ ] Avoid adding major new check families before the first stable release unless they fix a release blocker.
- [ ] Avoid adding model integrations before the first stable release.
- [ ] Avoid adding dashboard features before the first stable release.
- [ ] Avoid expanding automatic dataset repair workflows before the first stable release.
- [ ] Keep the first stable release focused on hardening existing behavior.

## Packaging

- [x] Update `hashprep/__init__.py` from `0.1.0b3` to the official release version.
- [x] Update the beta note in `README.md`.
- [x] Update the beta support table in `SECURITY.md`.
- [x] Add or verify PyPI classifiers in `pyproject.toml`.
- [x] Add or verify package keywords in `pyproject.toml`.
- [x] Add or verify project URLs in `pyproject.toml`.
- [x] Add or verify Python version classifiers in `pyproject.toml`.
- [x] Add or verify license metadata in `pyproject.toml`.
- [ ] Build source distribution.
- [ ] Build wheel distribution.
- [ ] Inspect built package artifacts.
- [ ] Install the built wheel in a clean environment.
- [ ] Smoke test `import hashprep` from the built wheel.
- [ ] Smoke test `hashprep version` from the built wheel.
- [ ] Smoke test `hashprep scan datasets/train.csv` from the built wheel.
- [ ] Smoke test `hashprep report datasets/train.csv --format html` from the built wheel.
- [ ] Confirm `MANIFEST.in` excludes dev/demo files intentionally.
- [ ] Confirm `MANIFEST.in` includes all runtime files needed by reports and templates.

## Documentation

- [x] Replace beta references in `README.md`.
- [x] Replace beta references in `SECURITY.md`.
- [x] Replace beta references in `web/src/lib/components/Hero.svelte`.
- [x] Add `CHANGELOG.md`.
- [ ] Add first official release notes.
- [ ] Document available checks in release notes.
- [ ] Document CLI commands in release notes.
- [ ] Document report formats in release notes.
- [ ] Document known limitations in release notes.
- [ ] Document upgrade notes from beta.
- [ ] Verify README examples run exactly as written.
- [ ] Update the documentation URL in `pyproject.toml` if a dedicated docs page is available.
- [ ] Refresh generated example reports under `examples/reports/` if needed.

## CI/CD

- [x] Add package build validation to CI.
- [x] Add `twine check` or equivalent artifact validation to CI.
- [ ] Add built-wheel install smoke test to CI.
- [ ] Add CLI smoke test against the built wheel to CI.
- [x] Add website build check for `web/`.
- [x] Add or verify release workflow triggered by version tags.
- [ ] Configure PyPI publishing, preferably with trusted publishing.
- [x] Configure GitHub release creation.
- [ ] Consider adding dependency and security scanning for Python dependencies.
- [ ] Consider adding dependency and security scanning for web dependencies.

## Security And Dependencies

- [ ] Review pinned and minimum Python dependency versions.
- [ ] Review pinned and minimum web dependency versions.
- [ ] Confirm heavy dependencies are intentional, especially `weasyprint`, `matplotlib`, `seaborn`, and `scikit-learn`.
- [ ] Decide whether PDF/report dependencies should remain core dependencies or move to optional extras in a future release.
- [ ] Run vulnerability checks for Python dependencies.
- [ ] Run vulnerability checks for web dependencies.
- [x] Update `SECURITY.md` to describe stable release support.

## Website

- [x] Update website beta badges.
- [ ] Update website install examples.
- [ ] Confirm the docs page matches the current README and API.
- [x] Build the static site successfully.
- [ ] Verify PyPI link.
- [ ] Verify GitHub link.
- [ ] Verify docs link.
- [ ] Verify license link.
- [ ] Verify issue tracker link.
- [ ] Decide deployment target for the docs site.
- [ ] Decide release timing for the docs site.

## Release Process

- [ ] Create a release branch.
- [ ] Make version, docs, and changelog updates.
- [ ] Run full validation locally.
- [ ] Merge after CI passes.
- [ ] Tag the release, for example `v0.1.0`.
- [ ] Publish to PyPI.
- [ ] Create GitHub release with release notes.
- [ ] Verify public install with `pip install hashprep`.
- [ ] Verify public CLI with `hashprep version`.
- [ ] Announce the release as the first stable release after alpha and beta.

## Known Immediate Gaps

- [x] Version is still `0.1.0b3`.
- [x] `README.md` still says beta.
- [x] Website hero still says beta and shows `hashprep-0.1.0b3`.
- [x] `SECURITY.md` only describes beta support.
- [x] `CHANGELOG.md` is not present.
- [x] CI does not currently build or check publish artifacts.
- [x] CI does not currently build the Svelte website.
- [x] No release or publish workflow is present.
