"""Test execution module."""

from __future__ import annotations

import platform

from .. import utils

VENV_BIN = utils.VENV_BIN

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_separator = utils.print_separator
venv_exists = utils.venv_exists
run_command = utils.run_command


def task_test() -> bool:
    """Run tests."""
    if not venv_exists():
        print_error("Virtual environment not found. Please create one first.")
        return False

    print_separator()
    print_info("RUNNING TESTS")
    print_separator()

    pytest = VENV_BIN / ("pytest.exe" if platform.system() == "Windows" else "pytest")

    success, _ = run_command([str(pytest)], check=False)
    if success:
        print("\n" + "=" * 70)
        print_success("All tests passed!")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print_error("Tests failed. Please review the output above.")
        print("=" * 70)
        return False

