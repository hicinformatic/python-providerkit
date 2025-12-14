"""Environment management tasks."""

from __future__ import annotations

import platform
import shutil

from .. import utils

PROJECT_ROOT = utils.PROJECT_ROOT
VENV_BIN = utils.VENV_BIN
VENV_DIR = utils.VENV_DIR
PIP = utils.PIP

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning
venv_exists = utils.venv_exists
run_command = utils.run_command


def install_build_dependencies() -> bool:
    """Install build dependencies."""
    success, _ = run_command([str(PIP), "install", "--upgrade", "pip", "setuptools", "wheel"])
    return success


def task_venv() -> bool:
    """Create a virtual environment."""
    if venv_exists():
        print_warning("Virtual environment already exists.")
        return True

    python_cmd = "python3" if platform.system() != "Windows" else "python"
    print_info("Creating virtual environment...")
    success, _ = run_command([python_cmd, "-m", "venv", str(VENV_DIR)], check=False)
    if not success:
        return False

    print_success(f"Virtual environment created at {VENV_DIR}")
    activation = (
        f"{VENV_DIR}\\Scripts\\activate"
        if platform.system() == "Windows"
        else f"source {VENV_DIR}/bin/activate"
    )
    print_info(f"Activate it with: {activation}")
    return True


def task_venv_clean() -> bool:
    """Recreate the virtual environment."""
    if venv_exists():
        print_info("Removing existing virtual environment...")
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        print_success("Virtual environment removed.")
    return task_venv()


def task_install() -> bool:
    """Install the package in production mode."""
    if not venv_exists() and not task_venv():
        return False

    print_info("Installing package (production)...")
    if not install_build_dependencies():
        return False

    success, _ = run_command([str(PIP), "install", "."], check=False)
    if not success:
        return False

    print_success("Installation complete.")
    return True


def task_install_dev() -> bool:
    """Install the package in editable mode with dev dependencies."""
    if not venv_exists() and not task_venv():
        return False

    print_info("Installing package (development)...")
    if not install_build_dependencies():
        return False

    success, _ = run_command([str(PIP), "install", "-e", "."], check=False)
    if not success:
        return False

    # Install development dependencies from requirements-dev.txt (preferred)
    requirements_dev = PROJECT_ROOT / "requirements-dev.txt"
    if requirements_dev.exists():
        print_info("Installing development dependencies from requirements-dev.txt...")
        success, _ = run_command([str(PIP), "install", "-r", str(requirements_dev)], check=False)
        if success:
            print_success("Development installation complete.")
            return True
        else:
            print_warning("Failed to install from requirements-dev.txt, trying fallback methods...")

    # Fallback: Install optional dependencies from pyproject.toml
    print_info("Installing development dependencies from pyproject.toml...")
    deps = ["lint", "security", "test", "quality"]
    for dep_group in deps:
        success, _ = run_command([str(PIP), "install", "-e", f".[{dep_group}]"], check=False)
        if not success:
            print_warning(f"Failed to install {dep_group} dependencies")

    # Also try individual requirements files if they exist
    requirements_files = [
        "requirements-lint.txt",
        "requirements-security.txt",
        "requirements-test.txt",
        "requirements-quality.txt",
    ]
    for req_file in requirements_files:
        req_path = PROJECT_ROOT / req_file
        if req_path.exists():
            print_info(f"Installing dependencies from {req_file}...")
            run_command([str(PIP), "install", "-r", str(req_path)], check=False)

    print_success("Development installation complete.")
    return True

