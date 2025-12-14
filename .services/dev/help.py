"""Help and documentation tasks."""

from __future__ import annotations

from .. import utils

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success


def task_help() -> bool:
    """Display help message."""
    print_info("Python Project — available commands\n")

    print_success("Environment:")
    print("  venv              Create a local virtual environment")
    print("  install           Install the package in production mode")
    print("  install-dev       Install the package in editable mode with dev dependencies")
    print("  venv-clean        Recreate the virtual environment")
    print("")

    print_success("Cleaning:")
    print("  clean             Remove build, bytecode, and test artifacts")
    print("  clean-build       Remove build artifacts")
    print("  clean-pyc         Remove Python bytecode")
    print("  clean-test        Remove test artifacts")
    print("")

    print_success("Packaging:")
    print("  build             Build sdist and wheel")
    print("")
    
    print_success("Library Management:")
    print("  update-lib            Install or update a library from local directory (editable mode)")
    print("                        Usage: dev update-lib path/to/library")
    print("  update-additional-libs  Install or update libraries from additionallib.json")
    print("                        Usage: dev update-additional-libs")
    print("")

    print_success("Usage: python dev.py <command>")
    print_success("       ./service.py dev <command>")
    return True

