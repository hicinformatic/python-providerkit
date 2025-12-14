"""Helper functions for provider discovery and loading."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
from pathlib import Path
from typing import Any

from .kit import ProviderBase


def load_providers_from_json(
    json_path: str | Path | None = None,
    *,
    lib_name: str = "providerkit",
    search_paths: list[str | Path] | None = None,
) -> dict[str, ProviderBase]:
    """Load providers from a JSON configuration file.

    Args:
        json_path: Path to JSON file. If None, searches in default locations.
        lib_name: Library name used to generate search paths (default: "providerkit").
            Example: "geoaddress" -> searches for ".geoaddress.json", "geoaddress.json", "~/.geoaddress.json".
        search_paths: Optional list of paths to search for JSON file.
            If provided, takes precedence over lib_name.

    Returns:
        Dictionary mapping provider names to provider instances.

    Example JSON format:
        [
            {
                "class": "mypackage.providers.geoapify.GeoapifyProvider",
                "config": {"GEOAPIFY_API_KEY": "key123"}
            }
        ]

    Example usage:
        # Default: searches for .providerkit.json, providerkit.json, ~/.providerkit.json
        providers = load_providers_from_json()

        # With lib_name (searches for .geoaddress.json, geoaddress.json, ~/.geoaddress.json)
        providers = load_providers_from_json(lib_name="geoaddress")

        # With explicit path
        providers = load_providers_from_json(json_path=".geoaddress.json")
    """
    if json_path is None:
        if search_paths is None:
            search_paths = [
                f".{lib_name}.json",
                f"{lib_name}.json",
                Path.home() / f".{lib_name}.json",
            ]
        else:
            search_paths = list(search_paths)

        for path in search_paths:
            path_obj = Path(path)
            if path_obj.exists():
                json_path = path_obj
                break
        else:
            return {}

    if json_path is None:
        return {}

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    return _load_providers_from_config(config)


def load_providers_from_config(config: list[dict[str, Any]]) -> dict[str, ProviderBase]:
    """Load providers from a Python configuration list.

    Args:
        config: List of provider configurations, each with 'class' and optional 'config'.

    Returns:
        Dictionary mapping provider names to provider instances.

    Example:
        config = [
            {
                "class": "mypackage.providers.geoapify.GeoapifyProvider",
                "config": {"GEOAPIFY_API_KEY": "key123"}
            }
        ]
    """
    return _load_providers_from_config(config)


def _load_providers_from_config(config: list[dict[str, Any]]) -> dict[str, ProviderBase]:
    """Internal function to load providers from configuration."""
    providers: dict[str, ProviderBase] = {}

    for provider_config in config:
        class_path = provider_config.get("class", "")
        if not class_path:
            continue

        try:
            parts = class_path.split(".")
            module_path = ".".join(parts[:-1])
            class_name = parts[-1]
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)

            if not issubclass(provider_class, ProviderBase):
                continue

            config_dict = provider_config.get("config", {})
            provider_instance = provider_class(
                config=config_dict, **provider_config.get("kwargs", {})
            )

            provider_name = getattr(provider_instance, "name", "").lower()
            if provider_name:
                providers[provider_name] = provider_instance
        except (ImportError, AttributeError, TypeError):
            continue

    return providers


def autodiscover_providers(
    dir_path: str | Path,
    *,
    base_module: str | None = None,
    exclude_files: list[str] | None = None,
) -> dict[str, type[ProviderBase]]:
    """Discover provider classes by scanning a directory structure.

    Args:
        dir_path: Root directory to scan for provider classes.
        base_module: Base module path for imports (e.g., "mypackage.providers").
            If None, attempts to infer from directory structure.
        exclude_files: List of filenames to exclude (default: ["__init__.py", "base.py"]).

    Returns:
        Dictionary mapping provider names to provider classes.

    Example:
        # Discover from backends/europe/france/*.py
        providers = autodiscover_providers("backends", base_module="mypackage.backends")
    """
    if exclude_files is None:
        exclude_files = ["__init__.py", "base.py"]

    dir_path_obj = Path(dir_path)
    if not dir_path_obj.exists() or not dir_path_obj.is_dir():
        return {}

    providers: dict[str, type[ProviderBase]] = {}

    for py_file in dir_path_obj.rglob("*.py"):
        if py_file.name in exclude_files or py_file.name.startswith("_"):
            continue

        try:
            if base_module:
                if dir_path_obj.is_absolute():
                    relative_path = py_file.relative_to(dir_path_obj)
                else:
                    cwd = Path.cwd()
                    abs_dir = (cwd / dir_path_obj).resolve()
                    abs_file = py_file.resolve()
                    relative_path = abs_file.relative_to(abs_dir)

                module_parts = list(relative_path.parts[:-1]) + [py_file.stem]
                module_path = f"{base_module}.{'.'.join(module_parts)}"
            else:
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module_path = module.__name__

            module = importlib.import_module(module_path)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    obj is not ProviderBase
                    and issubclass(obj, ProviderBase)
                    and obj.__module__ == module_path
                ):
                    provider_name = getattr(obj, "name", "").lower()
                    if provider_name:
                        providers[provider_name] = obj
        except (ImportError, AttributeError, TypeError, ValueError):
            continue

    return providers


def get_providers(
    *,
    json: str | Path | None = None,
    lib_name: str = "providerkit",
    config: list[dict[str, Any]] | None = None,
    dir_path: str | Path | None = None,
    base_module: str | None = None,
) -> dict[str, ProviderBase]:
    """Generic function to load providers from various sources.

    Args:
        json: Path to JSON configuration file.
        lib_name: Library name for JSON search (default: "providerkit").
            Example: "geoaddress" -> searches for ".geoaddress.json", "geoaddress.json", "~/.geoaddress.json".
            Only used if json is None.
        config: Python list of provider configurations.
        dir_path: Directory path for autodiscovery.
        base_module: Base module path for autodiscovery.

    Returns:
        Dictionary mapping provider names to provider instances.

    Priority:
        1. json parameter (explicit path)
        2. lib_name parameter (generates search paths, default: "providerkit")
        3. config parameter
        4. dir_path parameter (autodiscovery)

    Example:
        # Default: searches for .providerkit.json, providerkit.json, ~/.providerkit.json
        providers = get_providers()

        # From JSON with explicit path
        providers = get_providers(json=".geoaddress.json")

        # From JSON with lib_name (searches for .geoaddress.json, geoaddress.json, ~/.geoaddress.json)
        providers = get_providers(lib_name="geoaddress")

        # From Python config
        providers = get_providers(config=[{"class": "...", "config": {...}}])

        # From directory
        providers = get_providers(dir_path="backends", base_module="mypackage.backends")
    """
    if json is not None:
        return load_providers_from_json(json)
    else:
        return load_providers_from_json(lib_name=lib_name)

    if config is not None:
        return load_providers_from_config(config)

    if dir_path is not None:
        provider_classes = autodiscover_providers(dir_path, base_module=base_module)
        providers: dict[str, ProviderBase] = {}
        for name, provider_class in provider_classes.items():
            try:
                providers[name] = provider_class()
            except (TypeError, ValueError):
                continue
        return providers

    return {}
