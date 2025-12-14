#!/usr/bin/env python3
"""Utility functions for service scripts.

Contains common functions for printing, command execution, and result formatting.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

# Load .env file if it exists
PROJECT_ROOT = Path(__file__).resolve().parent.parent
_env_file = PROJECT_ROOT / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass


# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
NC = "\033[0m"  # No color

if platform.system() == "Windows" and not os.environ.get("ANSICON"):
    BLUE = GREEN = RED = YELLOW = CYAN = MAGENTA = NC = ""


def print_info(message: str) -> None:
    """Print an info message in blue."""
    print(f"{BLUE}{message}{NC}")


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"{GREEN}{message}{NC}")


def print_error(message: str) -> None:
    """Print an error message in red to stderr."""
    print(f"{RED}{message}{NC}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(f"{YELLOW}{message}{NC}")


def print_header(message: str) -> None:
    """Print a header message in cyan."""
    print(f"{CYAN}{message}{NC}")


def print_separator(char: str = "=", length: int = 70) -> None:
    """Print a separator line."""
    print(char * length)


def _resolve_venv_dir() -> Path:
    """Find the virtual env directory, preferring .venv over venv."""
    preferred_names = [".venv", "venv"]
    for name in preferred_names:
        candidate = PROJECT_ROOT / name
        if candidate.exists():
            return candidate
    return PROJECT_ROOT / preferred_names[0]


VENV_DIR = _resolve_venv_dir()
VENV_BIN = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin")
PYTHON = VENV_BIN / ("python.exe" if platform.system() == "Windows" else "python")
PIP = VENV_BIN / ("pip.exe" if platform.system() == "Windows" else "pip")


def venv_exists() -> bool:
    """Check if virtual environment exists."""
    return VENV_DIR.exists() and PYTHON.exists()


def run_command(
    cmd: Sequence[str],
    check: bool = True,
    capture_output: bool = False,
    **kwargs: Any,
) -> tuple[bool, str | None]:
    """Run a command and return (success, output).

    Args:
        cmd: Command to run
        check: If True, raise exception on non-zero exit
        capture_output: If True, capture and return stdout/stderr
        **kwargs: Additional arguments for subprocess.run

    Returns:
        Tuple of (success: bool, output: str | None)
    """
    printable = " ".join(cmd)
    print_info(f"Running: {printable}")

    try:
        result = subprocess.run(
            cmd,
            check=check,
            cwd=PROJECT_ROOT,
            capture_output=capture_output,
            text=True if capture_output else None,
            **kwargs,
        )
        output = result.stdout if capture_output else None
        return (result.returncode == 0, output)
    except subprocess.CalledProcessError as exc:
        print_error(f"Command exited with code {exc.returncode}")
        output = exc.stdout if capture_output else None
        return (False, output)
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        return (False, None)


def get_code_directories() -> list[str]:
    """Get list of code directories to check."""
    code_dirs = []
    for potential_dir in ["src", "."]:
        path = PROJECT_ROOT / potential_dir
        if path.exists():
            # Find Python packages
            for item in path.iterdir():
                if (
                    item.is_dir()
                    and not item.name.startswith(".")
                    and not item.name.startswith("_")
                ):
                    init_file = item / "__init__.py"
                    if init_file.exists():
                        code_dirs.append(str(item))
            # If no packages found, use the directory itself if it has Python files
            if not code_dirs and path != PROJECT_ROOT:
                if any(path.glob("*.py")):
                    code_dirs.append(str(path))

    # Fallback to current directory if nothing found
    if not code_dirs:
        code_dirs = ["."]

    return code_dirs


def format_results_table(
    results: dict[str, bool | dict[str, Any]],
    title: str | None = None,
    show_status: bool = True,
) -> str:
    """Format results as a table.

    Args:
        results: Dictionary of tool names to success status or detailed info
        title: Optional title for the table
        show_status: Whether to show status column

    Returns:
        Formatted table as string
    """
    lines = []
    if title:
        lines.append(f"\n{title}")
        lines.append("=" * 70)

    # Determine column widths
    tool_width = max(len(str(k)) for k in results.keys()) + 2
    if tool_width < 20:
        tool_width = 20

    status_width = 10 if show_status else 0
    details_width = 50

    # Header
    header = f"{'Tool':<{tool_width}}"
    if show_status:
        header += f" {'Status':<{status_width}}"
    header += f" {'Details':<{details_width}}"
    lines.append(header)
    lines.append("-" * 70)

    # Rows
    for tool, result in results.items():
        if isinstance(result, dict):
            status = result.get("status", False)
            details = result.get("details", "")
            errors = result.get("errors", 0)
            warnings = result.get("warnings", 0)
            if errors or warnings:
                details = f"Errors: {errors}, Warnings: {warnings}"
        else:
            status = bool(result)
            details = ""

        row = f"{tool:<{tool_width}}"
        if show_status:
            status_str = f"{GREEN}✓ PASS{NC}" if status else f"{RED}✗ FAIL{NC}"
            row += f" {status_str:<{status_width + 9}}"  # +9 for ANSI codes
        row += f" {details:<{details_width}}"
        lines.append(row)

    return "\n".join(lines)


def format_results_json(results: dict[str, bool | dict[str, Any]]) -> str:
    """Format results as JSON.

    Args:
        results: Dictionary of tool names to success status or detailed info

    Returns:
        Formatted JSON string
    """
    # Convert results to JSON-serializable format
    json_results = {}
    for tool, result in results.items():
        if isinstance(result, dict):
            json_results[tool] = result
        else:
            json_results[tool] = {"status": bool(result)}

    return json.dumps(json_results, indent=2)


def print_results(
    results: dict[str, bool | dict[str, Any]],
    title: str | None = None,
    format: str = "table",
    show_status: bool = True,
) -> None:
    """Print results in the specified format.

    Args:
        results: Dictionary of tool names to success status or detailed info
        title: Optional title for the output
        format: Output format ('table' or 'json')
        show_status: Whether to show status column (table format only)
    """
    if format.lower() == "json":
        output = format_results_json(results)
        print(output)
    else:
        output = format_results_table(results, title=title, show_status=show_status)
        print(output)


def summarize_results(results: dict[str, bool | dict[str, Any]]) -> dict[str, Any]:
    """Summarize results into statistics.

    Args:
        results: Dictionary of tool names to success status or detailed info

    Returns:
        Dictionary with summary statistics
    """
    total = len(results)
    passed = 0
    failed = 0
    total_errors = 0
    total_warnings = 0

    for tool, result in results.items():
        if isinstance(result, dict):
            status = result.get("status", False)
            total_errors += result.get("errors", 0)
            total_warnings += result.get("warnings", 0)
        else:
            status = bool(result)

        if status:
            passed += 1
        else:
            failed += 1

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": (passed / total * 100) if total > 0 else 0,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
    }


def print_summary(summary: dict[str, Any]) -> None:
    """Print a summary of results.

    Args:
        summary: Summary dictionary from summarize_results()
    """
    print_separator()
    print_header("Summary")
    print_separator()
    print(f"Total tools: {summary['total']}")
    print(f"{GREEN}Passed: {summary['passed']}{NC}")
    print(f"{RED}Failed: {summary['failed']}{NC}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    if summary.get("total_errors", 0) > 0:
        print(f"{RED}Total errors: {summary['total_errors']}{NC}")
    if summary.get("total_warnings", 0) > 0:
        print(f"{YELLOW}Total warnings: {summary['total_warnings']}{NC}")
    print_separator()

