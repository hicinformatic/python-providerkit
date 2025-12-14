"""Linting checks module."""

from __future__ import annotations

import platform
from pathlib import Path

from .. import utils

PROJECT_ROOT = utils.PROJECT_ROOT
VENV_BIN = utils.VENV_BIN

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning
print_header = utils.print_header
print_separator = utils.print_separator
venv_exists = utils.venv_exists
get_code_directories = utils.get_code_directories
run_command = utils.run_command
print_results = utils.print_results
summarize_results = utils.summarize_results
print_summary = utils.print_summary


def task_lint() -> bool:
    """Run linting checks."""
    if not venv_exists():
        print_error("Virtual environment not found. Please create one first.")
        return False

    print_separator()
    print_header("LINTING CHECKS")
    print_separator()

    ruff = VENV_BIN / ("ruff.exe" if platform.system() == "Windows" else "ruff")
    mypy = VENV_BIN / ("mypy.exe" if platform.system() == "Windows" else "mypy")
    semgrep = VENV_BIN / ("semgrep.exe" if platform.system() == "Windows" else "semgrep")
    pylint = VENV_BIN / ("pylint.exe" if platform.system() == "Windows" else "pylint")
    targets = get_code_directories()

    results = {}

    # Ruff check
    print("\n" + "-" * 70)
    print_info("1/4 - Running Ruff")
    print("-" * 70)
    success, _ = run_command([str(ruff), "check", *targets], check=False, capture_output=True)
    if success:
        print_success("✓ Ruff: No issues found")
        results["ruff"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ Ruff: Issues found")
        results["ruff"] = {"status": False, "errors": 1, "warnings": 0}

    # MyPy type checking
    print("\n" + "-" * 70)
    print_info("2/4 - Running MyPy")
    print("-" * 70)
    success, _ = run_command([str(mypy), *targets], check=False, capture_output=True)
    if success:
        print_success("✓ MyPy: No type issues found")
        results["mypy"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ MyPy: Type issues found")
        results["mypy"] = {"status": False, "errors": 1, "warnings": 0}

    # Pylint - Code quality and duplicate code detection
    print("\n" + "-" * 70)
    print_info("3/4 - Running Pylint (Code Quality & Duplicate Code)")
    print("-" * 70)
    success, _ = run_command(
        [str(pylint), "--disable=all", "--enable=duplicate-code", *targets],
        check=False,
        capture_output=True,
    )
    if success:
        print_success("✓ Pylint: No duplicate code or quality issues found")
        results["pylint"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ Pylint: Duplicate code or quality issues found")
        results["pylint"] = {"status": False, "errors": 1, "warnings": 0}

    # Semgrep - Code quality and security patterns
    print("\n" + "-" * 70)
    print_info("4/4 - Running Semgrep (Code Quality & Security Patterns)")
    print("-" * 70)
    semgrep_cmd = [str(semgrep), "scan"]
    semgrep_configs = []
    local_semgrep = PROJECT_ROOT / ".semgrep.yaml"
    if local_semgrep.exists():
        semgrep_configs.append(str(local_semgrep))
    else:
        semgrep_configs.append("p/default")
    semgrep_configs.extend(["p/python", "p/supply-chain"])
    for config in semgrep_configs:
        semgrep_cmd += ["--config", config]
    semgrep_cmd += targets
    success, _ = run_command(semgrep_cmd, check=False, capture_output=True)
    if success:
        print_success("✓ Semgrep: No issues found")
        results["semgrep"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ Semgrep: Issues found")
        results["semgrep"] = {"status": False, "errors": 1, "warnings": 0}

    # Print results summary
    print_results(results, title="Linting Results", format="table")
    summary = summarize_results(results)
    print_summary(summary)

    return all(r.get("status", False) for r in results.values())

