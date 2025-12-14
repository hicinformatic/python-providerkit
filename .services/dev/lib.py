"""Library update tasks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .. import utils

PROJECT_ROOT = utils.PROJECT_ROOT
PIP = utils.PIP

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning
print_separator = utils.print_separator
venv_exists = utils.venv_exists
run_command = utils.run_command


def task_update_lib() -> bool:
    """Install or update a library from local directory in editable mode.
    
    Usage:
      python dev.py update-lib <path_to_library>
      ./service.py dev update-lib path/to/lib
    
    The library will be installed in editable mode (-e) so changes are
    immediately available without reinstalling.
    
    Args:
        Path to the library directory (must contain setup.py or pyproject.toml)
    """
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    # Get path from command line arguments
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if not args:
        print_error("No library path provided.")
        print_info("Usage: python dev.py update-lib <path_to_library>")
        print_info("       ./service.py dev update-lib path/to/lib")
        return False

    target_dir = Path(args[0]).resolve()
    
    # Handle relative paths
    if not target_dir.is_absolute():
        target_dir = (PROJECT_ROOT / args[0]).resolve()

    if not target_dir.exists():
        print_error(f"Library directory not found at {target_dir}")
        print_info("Provide a valid path: python dev.py update-lib /path/to/library")
        return False

    if not target_dir.is_dir():
        print_error(f"Path is not a directory: {target_dir}")
        return False

    # Check if it looks like a Python package
    has_setup = (target_dir / "setup.py").exists()
    has_pyproject = (target_dir / "pyproject.toml").exists()
    
    if not (has_setup or has_pyproject):
        print_warning(
            f"Warning: No setup.py or pyproject.toml found in {target_dir}. "
            "This might not be a Python package."
        )

    lib_name = target_dir.name
    print_info(f"Installing {lib_name} into the virtual environment...")
    print_info(f"Library path: {target_dir}")
    
    success, _ = run_command([str(PIP), "install", "-e", str(target_dir)], check=False)
    if success:
        print_success(f"{lib_name} installed/updated successfully.")
        return True

    print_error(f"Failed to install/update {lib_name}.")
    return False


def task_update_additional_libs() -> bool:
    """Install or update libraries listed in additionallib.json.
    
    Usage:
      python dev.py update-additional-libs
      ./service.py dev update-additional-libs
    
    Reads the additionallib.json file in the project root and installs
    all libraries listed there in editable mode.
    
    The JSON file should have the following structure:
    {
      "libraries": [
        {
          "name": "library-name",
          "path": "../path/to/library",
          "description": "Optional description"
        }
      ]
    }
    """
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    # Look for additionallib.json in project root
    config_file = PROJECT_ROOT / "additionallib.json"
    
    if not config_file.exists():
        print_error(f"Configuration file not found: {config_file}")
        print_info("Create additionallib.json in the project root.")
        print_info("You can copy additionallib.json.example as a template.")
        return False

    print_separator()
    print_info(f"Reading libraries from {config_file.name}")
    print_separator()

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in {config_file}: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading {config_file}: {e}")
        return False

    if "libraries" not in config:
        print_error(f"Missing 'libraries' key in {config_file}")
        return False

    libraries = config["libraries"]
    if not isinstance(libraries, list):
        print_error(f"'libraries' must be a list in {config_file}")
        return False

    if not libraries:
        print_warning("No libraries found in additionallib.json")
        return True

    print_info(f"Found {len(libraries)} library(ies) to install/update\n")

    results = {}
    for idx, lib_config in enumerate(libraries, 1):
        if not isinstance(lib_config, dict):
            print_warning(f"Library entry {idx} is not a dictionary, skipping")
            continue

        lib_name = lib_config.get("name", f"library-{idx}")
        lib_path = lib_config.get("path")
        lib_description = lib_config.get("description", "")

        if not lib_path:
            print_error(f"Library '{lib_name}' missing 'path' field, skipping")
            results[lib_name] = False
            continue

        print_info(f"[{idx}/{len(libraries)}] Processing {lib_name}")
        if lib_description:
            print_info(f"  Description: {lib_description}")
        print_info(f"  Path: {lib_path}")

        # Resolve path
        target_dir = Path(lib_path)
        if not target_dir.is_absolute():
            target_dir = (PROJECT_ROOT / lib_path).resolve()

        if not target_dir.exists():
            print_warning(f"  ⚠ Library directory not found at {target_dir}, skipping")
            results[lib_name] = False
            continue

        if not target_dir.is_dir():
            print_warning(f"  ⚠ Path is not a directory: {target_dir}, skipping")
            results[lib_name] = False
            continue

        # Install library
        print_info(f"  Installing {lib_name}...")
        success, _ = run_command([str(PIP), "install", "-e", str(target_dir)], check=False)
        
        if success:
            print_success(f"  ✓ {lib_name} installed/updated successfully")
            results[lib_name] = True
        else:
            print_error(f"  ✗ Failed to install/update {lib_name}")
            results[lib_name] = False

        print()  # Empty line between libraries

    # Summary
    print_separator()
    print_info("Installation Summary")
    print_separator()
    
    total = len(results)
    successful = sum(1 for success in results.values() if success)
    failed = total - successful

    for lib_name, success in results.items():
        status = f"{utils.GREEN}✓{utils.NC}" if success else f"{utils.RED}✗{utils.NC}"
        print(f"  {status} {lib_name}")

    print_separator()
    print_info(f"Total: {total} | Successful: {successful} | Failed: {failed}")
    print_separator()

    return failed == 0

