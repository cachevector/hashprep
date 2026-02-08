"""
Comprehensive tests for HashPrep CLI commands.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def titanic_csv():
    """Path to titanic dataset."""
    return str(Path(__file__).parent.parent / "datasets" / "train.csv")


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def run_cli(args, cwd=None):
    """Helper to run CLI commands."""
    cmd = ['uv', 'run', 'hashprep'] + args
    if cwd is None:
        cwd = Path(__file__).parent.parent
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result


class TestCLIScan:
    """Test 'hashprep scan' command."""

    def test_scan_basic(self, titanic_csv):
        """Test basic scan command."""
        result = run_cli(['scan', titanic_csv])

        assert result.returncode == 0
        assert 'Dataset Health Check' in result.stdout
        assert 'Critical Issues:' in result.stdout
        assert 'Warnings:' in result.stdout

    def test_scan_critical_only(self, titanic_csv):
        """Test scan with --critical-only flag."""
        result = run_cli(['scan', titanic_csv, '--critical-only'])

        assert result.returncode == 0
        assert 'Critical Issues:' in result.stdout

    def test_scan_quiet(self, titanic_csv):
        """Test scan with --quiet flag."""
        result = run_cli(['scan', titanic_csv, '--quiet'])

        assert result.returncode == 0
        # Should only show counts
        assert 'critical' in result.stdout.lower()

    def test_scan_json_output(self, titanic_csv):
        """Test scan with --json flag."""
        result = run_cli(['scan', titanic_csv, '--json'])

        assert result.returncode == 0
        # Should be valid JSON
        data = json.loads(result.stdout)
        assert 'critical_issues' in data or 'critical_count' in data
        assert 'warnings' in data or 'warning_count' in data
        assert 'issues' in data

    def test_scan_with_target(self, titanic_csv):
        """Test scan with target column."""
        result = run_cli(['scan', titanic_csv, '--target', 'Survived'])

        assert result.returncode == 0
        assert 'Dataset Health Check' in result.stdout

    def test_scan_specific_checks(self, titanic_csv):
        """Test scan with specific checks."""
        result = run_cli([
            'scan', titanic_csv,
            '--checks', 'outliers,duplicates,high_missing_values'
        ])

        assert result.returncode == 0
        assert 'Dataset Health Check' in result.stdout

    def test_scan_with_sampling(self, titanic_csv):
        """Test scan with custom sample size."""
        result = run_cli(['scan', titanic_csv, '--sample-size', '500'])

        assert result.returncode == 0
        if 'sample' in result.stdout.lower():
            assert '56.1%' in result.stdout  # 500/891


class TestCLIDetails:
    """Test 'hashprep details' command."""

    def test_details_basic(self, titanic_csv):
        """Test basic details command."""
        result = run_cli(['details', titanic_csv])

        assert result.returncode == 0
        assert 'Detailed Analysis' in result.stdout
        assert 'Critical Issues:' in result.stdout
        assert 'Warnings:' in result.stdout
        assert 'Dataset Summary:' in result.stdout

    def test_details_with_target(self, titanic_csv):
        """Test details with target column."""
        result = run_cli(['details', titanic_csv, '--target', 'Survived'])

        assert result.returncode == 0
        assert 'Detailed Analysis' in result.stdout

    def test_details_specific_checks(self, titanic_csv):
        """Test details with specific checks."""
        result = run_cli([
            'details', titanic_csv,
            '--checks', 'high_missing_values,outliers'
        ])

        assert result.returncode == 0


class TestCLIReport:
    """Test 'hashprep report' command."""

    def test_report_markdown(self, titanic_csv, temp_output_dir):
        """Test Markdown report generation."""
        result = run_cli(['report', titanic_csv, '--format', 'md'], cwd=temp_output_dir)

        assert result.returncode == 0
        assert 'Report saved to:' in result.stdout
        assert 'train_hashprep_report.md' in result.stdout

        # Check file was created
        report_file = os.path.join(temp_output_dir, 'train_hashprep_report.md')
        assert os.path.exists(report_file)

    def test_report_json(self, titanic_csv, temp_output_dir):
        """Test JSON report generation."""
        result = run_cli(['report', titanic_csv, '--format', 'json'], cwd=temp_output_dir)

        assert result.returncode == 0
        assert 'train_hashprep_report.json' in result.stdout

        # Verify JSON is valid
        report_file = os.path.join(temp_output_dir, 'train_hashprep_report.json')
        assert os.path.exists(report_file)
        with open(report_file) as f:
            data = json.load(f)
            assert 'metadata' in data
            assert 'dataset_overview' in data

    def test_report_html_minimal(self, titanic_csv, temp_output_dir):
        """Test HTML report with minimal theme."""
        result = run_cli([
            'report', titanic_csv,
            '--format', 'html',
            '--theme', 'minimal',
            '--full'
        ], cwd=temp_output_dir)

        assert result.returncode == 0
        assert 'train_hashprep_report.html' in result.stdout

        report_file = os.path.join(temp_output_dir, 'train_hashprep_report.html')
        assert os.path.exists(report_file)

    def test_report_html_neubrutalism(self, titanic_csv, temp_output_dir):
        """Test HTML report with neubrutalism theme."""
        result = run_cli([
            'report', titanic_csv,
            '--format', 'html',
            '--theme', 'neubrutalism',
            '--full'
        ], cwd=temp_output_dir)

        assert result.returncode == 0
        assert 'train_hashprep_report.html' in result.stdout

    def test_report_pdf(self, titanic_csv, temp_output_dir):
        """Test PDF report generation."""
        result = run_cli(['report', titanic_csv, '--format', 'pdf', '--full'], cwd=temp_output_dir)

        assert result.returncode == 0
        assert 'train_hashprep_report.pdf' in result.stdout

        report_file = os.path.join(temp_output_dir, 'train_hashprep_report.pdf')
        assert os.path.exists(report_file)
        # Check PDF magic number
        with open(report_file, 'rb') as f:
            assert f.read(4) == b'%PDF'

    def test_report_with_code_generation(self, titanic_csv, temp_output_dir):
        """Test report with code generation."""
        result = run_cli(['report', titanic_csv, '--with-code'], cwd=temp_output_dir)

        assert result.returncode == 0
        assert 'fixes script saved' in result.stdout
        assert 'pipeline script saved' in result.stdout

        # Check files were created
        assert os.path.exists(os.path.join(temp_output_dir, 'train_hashprep_report_fixes.py'))
        assert os.path.exists(os.path.join(temp_output_dir, 'train_hashprep_report_pipeline.py'))

    def test_report_no_visualizations(self, titanic_csv, temp_output_dir):
        """Test report without visualizations."""
        result = run_cli([
            'report', titanic_csv,
            '--format', 'html',
            '--no-visualizations'
        ], cwd=temp_output_dir)

        assert result.returncode == 0

    def test_report_no_full(self, titanic_csv, temp_output_dir):
        """Test summary-only report."""
        result = run_cli([
            'report', titanic_csv,
            '--format', 'md',
            '--no-full'
        ], cwd=temp_output_dir)

        assert result.returncode == 0

    def test_report_with_target(self, titanic_csv, temp_output_dir):
        """Test report with target column."""
        result = run_cli([
            'report', titanic_csv,
            '--target', 'Survived',
            '--format', 'json'
        ], cwd=temp_output_dir)

        assert result.returncode == 0

    def test_report_specific_checks(self, titanic_csv, temp_output_dir):
        """Test report with specific checks."""
        result = run_cli([
            'report', titanic_csv,
            '--checks', 'outliers,high_missing_values,duplicates',
            '--format', 'md'
        ], cwd=temp_output_dir)

        assert result.returncode == 0


class TestCLIVersion:
    """Test 'hashprep version' command."""

    def test_version(self):
        """Test version command."""
        result = run_cli(['version'])

        assert result.returncode == 0
        assert 'hashprep' in result.stdout.lower()
        # Should show version number
        assert any(char.isdigit() for char in result.stdout)


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_file(self):
        """Test with non-existent file."""
        result = run_cli(['scan', 'nonexistent.csv'])

        assert result.returncode != 0

    def test_invalid_format(self, titanic_csv):
        """Test with invalid report format."""
        result = run_cli(['report', titanic_csv, '--format', 'invalid'])

        # Should handle gracefully or error
        assert result.returncode != 0 or 'error' in result.stderr.lower()

    def test_invalid_check_name(self, titanic_csv):
        """Test with invalid check name."""
        result = run_cli([
            'report', titanic_csv,
            '--checks', 'invalid_check_name'
        ])

        assert result.returncode == 0
        assert 'Warning: Invalid checks ignored' in result.stdout
        # Fuzzy suggestion feature (if merged)
        # assert 'Did you mean' in result.stdout


class TestCLIIntegration:
    """Integration tests for complete workflows."""

    def test_full_workflow(self, titanic_csv, temp_output_dir):
        """Test complete workflow: scan -> details -> report."""
        # Step 1: Scan
        result = run_cli(['scan', titanic_csv])
        assert result.returncode == 0

        # Step 2: Details
        result = run_cli(['details', titanic_csv])
        assert result.returncode == 0

        # Step 3: Generate all report formats
        for fmt in ['md', 'json', 'html', 'pdf']:
            result = run_cli([
                'report', titanic_csv,
                '--format', fmt,
                '--full'
            ], cwd=temp_output_dir)
            assert result.returncode == 0

        # Step 4: Generate code
        result = run_cli(['report', titanic_csv, '--with-code'], cwd=temp_output_dir)
        assert result.returncode == 0

    def test_ml_workflow_with_target(self, titanic_csv, temp_output_dir):
        """Test ML-focused workflow with target column."""
        # Generate report with target and code
        result = run_cli([
            'report', titanic_csv,
            '--target', 'Survived',
            '--with-code',
            '--format', 'html',
            '--theme', 'minimal',
            '--full'
        ], cwd=temp_output_dir)

        assert result.returncode == 0
        assert os.path.exists(os.path.join(temp_output_dir, 'train_hashprep_report.html'))
        assert os.path.exists(os.path.join(temp_output_dir, 'train_hashprep_report_fixes.py'))
        assert os.path.exists(os.path.join(temp_output_dir, 'train_hashprep_report_pipeline.py'))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
