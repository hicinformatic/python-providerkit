#!/usr/bin/env python3
"""Django service for managing Django commands.

Usage:
    python django.py <command> [args...]
    ./service.py django <command> [args...]

Examples:
    ./service.py django runserver
    ./service.py django makemigrations
    ./service.py django migrate
    ./service.py django shell
    ./service.py django createsuperuser
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Callable

from . import utils

# Import utility functions
print_error = utils.print_error
print_info = utils.print_info
print_success = utils.print_success
print_warning = utils.print_warning
run_command = utils.run_command
venv_exists = utils.venv_exists

# Paths
PROJECT_ROOT = utils.PROJECT_ROOT
VENV_BIN = utils.VENV_BIN
PYTHON = utils.PYTHON

# Path to manage.py
MANAGE_PY = PROJECT_ROOT / ".services" / "django" / "manage.py"


def task_help() -> bool:
    """Display help message."""
    print_info("Django Management Commands\n")
    print_success("Available commands:")
    print("  runserver [port]     Start Django development server (default: 8000)")
    print("  makemigrations       Create new migrations")
    print("  migrate              Apply migrations")
    print("  shell                Start Django shell")
    print("  createsuperuser      Create a Django superuser")
    print("  resetdb              Reset database (drop + migrate)")
    print("  <command>            Any other Django management command")
    print("")
    print_success("Usage:")
    print("  python django.py <command> [args...]")
    print("  ./service.py django <command> [args...]")
    print("")
    print_success("Examples:")
    print("  ./service.py django runserver")
    print("  ./service.py django runserver 8080")
    print("  ./service.py django makemigrations")
    print("  ./service.py django migrate")
    print("  ./service.py django shell")
    return True


def task_runserver() -> bool:
    """Start Django development server."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not MANAGE_PY.exists():
        print_error(f"manage.py not found at {MANAGE_PY}")
        print_info("This command is only available for Django projects.")
        return False

    args = sys.argv[2:] if len(sys.argv) > 2 else []
    port = args[0] if args else "8000"

    return run_command([str(PYTHON), str(MANAGE_PY), "runserver", port], check=False)


def task_makemigrations() -> bool:
    """Create new migrations."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not MANAGE_PY.exists():
        print_error(f"manage.py not found at {MANAGE_PY}")
        print_info("This command is only available for Django projects.")
        return False

    args = sys.argv[2:] if len(sys.argv) > 2 else []
    cmd = [str(PYTHON), str(MANAGE_PY), "makemigrations"] + args
    return run_command(cmd, check=False)


def task_migrate() -> bool:
    """Apply migrations."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not MANAGE_PY.exists():
        print_error(f"manage.py not found at {MANAGE_PY}")
        print_info("This command is only available for Django projects.")
        return False

    args = sys.argv[2:] if len(sys.argv) > 2 else []
    cmd = [str(PYTHON), str(MANAGE_PY), "migrate"] + args
    return run_command(cmd, check=False)


def task_shell() -> bool:
    """Start Django shell."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not MANAGE_PY.exists():
        print_error(f"manage.py not found at {MANAGE_PY}")
        print_info("This command is only available for Django projects.")
        return False

    return run_command([str(PYTHON), str(MANAGE_PY), "shell"], check=False)


def task_createsuperuser() -> bool:
    """Create a Django superuser."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not MANAGE_PY.exists():
        print_error(f"manage.py not found at {MANAGE_PY}")
        print_info("This command is only available for Django projects.")
        return False

    return run_command([str(PYTHON), str(MANAGE_PY), "createsuperuser"], check=False)


def task_resetdb() -> bool:
    """Reset database (drop + migrate)."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not MANAGE_PY.exists():
        print_error(f"manage.py not found at {MANAGE_PY}")
        print_info("This command is only available for Django projects.")
        return False

    db_file = PROJECT_ROOT / "db.sqlite3"
    if db_file.exists():
        print_warning("Deleting existing database...")
        db_file.unlink()

    print_info("Creating new database...")
    return task_migrate()


def task_generic() -> bool:
    """Execute a generic Django management command."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not MANAGE_PY.exists():
        print_error(f"manage.py not found at {MANAGE_PY}")
        print_info("This command is only available for Django projects.")
        return False

    if len(sys.argv) < 2:
        print_error("No command specified.")
        task_help()
        return False

    # Get command and args
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    cmd = [str(PYTHON), str(MANAGE_PY), command] + args
    return run_command(cmd, check=False)


# Command mapping
COMMANDS: dict[str, Callable[[], bool]] = {
    "help": task_help,
    "runserver": task_runserver,
    "makemigrations": task_makemigrations,
    "migrate": task_migrate,
    "shell": task_shell,
    "createsuperuser": task_createsuperuser,
    "resetdb": task_resetdb,
}


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        task_help()
        return 0

    command = sys.argv[1].lower()

    # Check if it's a known command
    if command in COMMANDS:
        try:
            success = COMMANDS[command]()
            return 0 if success else 1
        except KeyboardInterrupt:
            print_warning("\nOperation cancelled by user.")
            return 130
        except Exception as exc:
            print_error(f"Error: {exc}")
            import traceback
            traceback.print_exc()
            return 1
    else:
        # Try as a generic Django command
        try:
            success = task_generic()
            return 0 if success else 1
        except KeyboardInterrupt:
            print_warning("\nOperation cancelled by user.")
            return 130
        except Exception as exc:
            print_error(f"Error: {exc}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    sys.exit(main())

