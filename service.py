#!/usr/bin/env python3
"""Service router script for Python projects.

Routes commands to appropriate service scripts in .services/ directory.
Usage:
    ./service.py quality lint
    ./service.py dev install-dev
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SERVICES_DIR = PROJECT_ROOT / ".services"


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: ./service.py <service> <command> [args...]")
        print("\nServices:")
        print("  quality  Quality checks (lint, security, test, complexity, cleanup)")
        print("  dev      Development tasks (venv, install, install-dev, clean, build)")
        print("  django   Django management commands (runserver, makemigrations, migrate, etc.)")
        print("  publish  Publishing (releases, social media announcements)")
        print("\nExamples:")
        print("  ./service.py quality lint")
        print("  ./service.py quality security")
        print("  ./service.py dev install-dev")
        print("  ./service.py dev venv")
        print("  ./service.py django runserver")
        print("  ./service.py django makemigrations")
        print("  ./service.py publish release-full")
        print("  ./service.py publish social-all")
        return 1

    service = sys.argv[1].lower()
    command_args = sys.argv[2:]

    # Map service names to script files
    service_scripts = {
        "quality": SERVICES_DIR / "quality.py",
        "dev": SERVICES_DIR / "dev.py",
        "django": SERVICES_DIR / "django.py",
        "publish": SERVICES_DIR / "publish.py",
    }

    if service not in service_scripts:
        print(f"Error: Unknown service '{service}'")
        print("Available services: quality, dev, django, publish")
        return 1

    script_path = service_scripts[service]

    if not script_path.exists():
        print(f"Error: Service script not found: {script_path}")
        return 1

    # Execute the service script with remaining arguments
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)] + command_args,
            cwd=PROJECT_ROOT,
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130
    except Exception as exc:
        print(f"Error executing service: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

