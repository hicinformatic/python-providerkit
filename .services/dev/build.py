"""Build and packaging tasks."""

from __future__ import annotations

from .. import utils
from .env import install_build_dependencies

VENV_BIN = utils.VENV_BIN
PYTHON = utils.PYTHON

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
venv_exists = utils.venv_exists
run_command = utils.run_command


def task_build() -> bool:
    """Build sdist and wheel."""
    if not venv_exists():
        print_error("Virtual environment not found. Run `python dev.py install-dev` first.")
        return False

    print_info("Building package...")
    if not install_build_dependencies():
        return False

    success, _ = run_command([str(PYTHON), "-m", "build"], check=False)
    if not success:
        return False

    print_success("Build complete. Artifacts in dist/")
    return True

