"""Cleaning tasks."""

from __future__ import annotations

import shutil

from .. import utils

PROJECT_ROOT = utils.PROJECT_ROOT

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success


def task_clean_build() -> bool:
    """Remove build artifacts."""
    print_info("Removing build artifacts...")
    for directory in ["build", "dist", ".eggs"]:
        path = PROJECT_ROOT / directory
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
            print(f"  Removed {directory}/")

    for egg_info in PROJECT_ROOT.glob("**/*.egg-info"):
        shutil.rmtree(egg_info, ignore_errors=True)
        print(f"  Removed {egg_info}")

    return True


def task_clean_pyc() -> bool:
    """Remove Python bytecode artifacts."""
    print_info("Removing Python bytecode artifacts...")

    for pycache in PROJECT_ROOT.glob("**/__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
        print(f"  Removed {pycache}")

    for pattern in ["**/*.pyc", "**/*.pyo", "**/*~"]:
        for file in PROJECT_ROOT.glob(pattern):
            file.unlink(missing_ok=True)

    return True


def task_clean_test() -> bool:
    """Remove test artifacts."""
    print_info("Removing test artifacts...")
    artifacts = [".pytest_cache", ".coverage", "htmlcov", ".mypy_cache", ".ruff_cache"]

    for artifact in artifacts:
        path = PROJECT_ROOT / artifact
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
            print(f"  Removed {artifact}")

    print_success("Test artifacts removed.")
    return True


def task_clean() -> bool:
    """Remove all build, bytecode, and test artifacts."""
    task_clean_build()
    task_clean_pyc()
    task_clean_test()
    print_success("Workspace clean.")
    return True

