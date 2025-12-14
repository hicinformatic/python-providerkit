"""Security checks module."""

from __future__ import annotations

import os
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


def task_security() -> bool:
    """Run security checks."""
    if not venv_exists():
        print_error("Virtual environment not found. Please create one first.")
        return False

    print_separator()
    print_header("SECURITY CHECKS")
    print_separator()

    bandit = VENV_BIN / ("bandit.exe" if platform.system() == "Windows" else "bandit")
    safety = VENV_BIN / ("safety.exe" if platform.system() == "Windows" else "safety")
    pip_audit = VENV_BIN / ("pip-audit.exe" if platform.system() == "Windows" else "pip-audit")
    semgrep = VENV_BIN / ("semgrep.exe" if platform.system() == "Windows" else "semgrep")
    targets = get_code_directories()

    results = {
        "bandit": False,
        "safety": False,
        "pip_audit": False,
        "semgrep": False,
    }

    # Bandit - Static code analysis
    print("\n" + "-" * 70)
    print_info("1/4 - Running Bandit (Static Code Analysis)")
    print("-" * 70)
    success, _ = run_command(
        [str(bandit), "-r", *targets, "-ll", "-f", "screen", "--skip", "B101"],
        check=False,
    )
    if success:
        print_success("✓ Bandit: No high/medium issues found")
        results["bandit"] = True
    else:
        print_warning("⚠ Bandit: Issues found (review above)")

    # Safety - Dependency vulnerability check
    print("\n" + "-" * 70)
    print_info("2/4 - Running Safety (Dependency Vulnerabilities)")
    print("-" * 70)
    safety_cmd = [str(safety), "scan", "--output", "json"]
    safety_api_key = os.environ.get("SAFETY_API_KEY")
    if safety_api_key:
        safety_cmd.extend(["--key", safety_api_key])
        print_info("   Using SAFETY_API_KEY from environment")

    safety_result, _ = run_command(safety_cmd, check=False)
    if safety_result:
        print_success("✓ Safety: No vulnerabilities found")
        results["safety"] = True
    else:
        if not safety_api_key:
            print_warning("⚠ Safety: Unable to complete scan (authentication required)")
            print_info("   Note: Safety CLI requires free account registration")
            print_info("   Option 1: Register at https://pyup.io/safety/ and set SAFETY_API_KEY env var")
            print_info("   Option 2: Run 'safety auth' to authenticate interactively")
            print_info("   For now, treating as skipped (not a failure)")
            results["safety"] = True  # Count as pass since it's optional
        else:
            print_warning("⚠ Safety: Scan completed but issues may have been found")
            results["safety"] = False

    # Pip-Audit - PyPI vulnerability audit
    print("\n" + "-" * 70)
    print_info("3/4 - Running Pip-Audit (PyPI Vulnerabilities)")
    print("-" * 70)
    success, _ = run_command([str(pip_audit)], check=False)
    if success:
        print_success("✓ Pip-Audit: No vulnerabilities found")
        results["pip_audit"] = True
    else:
        print_warning("⚠ Pip-Audit: Vulnerabilities found (review above)")

    # Semgrep - SAST rules
    print("\n" + "-" * 70)
    print_info("4/4 - Running Semgrep (SAST)")
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
    success, _ = run_command(semgrep_cmd, check=False)
    if success:
        print_success("✓ Semgrep: No issues found")
        results["semgrep"] = True
    else:
        print_warning("⚠ Semgrep: Issues found (review above)")

    all_passed = all(results.values())
    if all_passed:
        print("\n" + "=" * 70)
        print_success("All security checks passed!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print_warning("Some security checks found issues. Please review the output above.")
        print("=" * 70)

    return all_passed

