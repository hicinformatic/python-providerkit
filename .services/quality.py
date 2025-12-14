#!/usr/bin/env python3
"""Quality checks script for Python projects.

Provides commands for linting, security checks, and testing.
"""

from __future__ import annotations

import sys

from . import utils
from .quality import cleanup, complexity, lint, security, test

# Import utility functions for error handling
print_error = utils.print_error

# Import task functions from modules
task_lint = lint.task_lint
task_security = security.task_security
task_test = test.task_test
task_complexity = complexity.task_complexity
task_cleanup = cleanup.task_cleanup


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python quality.py <command>")
        print("\nCommands:")
        print("  lint      Run linting checks (ruff, mypy, pylint, semgrep)")
        print("  security  Run security checks (bandit, safety, pip-audit, semgrep)")
        print("  test      Run tests (pytest)")
        print("  complexity  Analyze code complexity (radon)")
        print("  cleanup   Detect unused code, imports, and redundancies (vulture, autoflake, pylint)")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "lint":
        success = task_lint()
    elif command == "security":
        success = task_security()
    elif command == "test":
        success = task_test()
    elif command == "complexity":
        success = task_complexity()
    elif command == "cleanup":
        success = task_cleanup()
    else:
        print_error(f"Unknown command: {command}")
        print("Available commands: lint, security, test, complexity, cleanup")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

