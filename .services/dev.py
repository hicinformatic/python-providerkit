#!/usr/bin/env python3
"""Development helper script for Python projects.

This is a template script that provides common development tasks.
"""

from __future__ import annotations

import sys
from typing import Sequence

from . import utils
from .dev import build, clean, env, help, lib

# Import utility functions for error handling
print_info = utils.print_info
print_error = utils.print_error
print_warning = utils.print_warning

# Import task functions from modules
task_help = help.task_help
task_venv = env.task_venv
task_install = env.task_install
task_install_dev = env.task_install_dev
task_venv_clean = env.task_venv_clean
task_clean = clean.task_clean
task_clean_build = clean.task_clean_build
task_clean_pyc = clean.task_clean_pyc
task_clean_test = clean.task_clean_test
task_build = build.task_build
task_update_lib = lib.task_update_lib
task_update_additional_libs = lib.task_update_additional_libs


COMMANDS = {
    "help": task_help,
    "venv": task_venv,
    "install": task_install,
    "install-dev": task_install_dev,
    "venv-clean": task_venv_clean,
    "clean": task_clean,
    "clean-build": task_clean_build,
    "clean-pyc": task_clean_pyc,
    "clean-test": task_clean_test,
    "build": task_build,
    "update-lib": task_update_lib,
    "update-additional-libs": task_update_additional_libs,
}


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point."""
    args = list(argv if argv is not None else sys.argv[1:])

    if not args:
        task_help()
        return 0

    command = args[0]
    if command not in COMMANDS:
        print_error(f"Unknown command: {command}")
        print_info("Run `python dev.py help` to list available commands.")
        return 1

    try:
        success = COMMANDS[command]()
        return 0 if success else 1
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user.")
        return 130
    except Exception as exc:
        print_error(f"Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

