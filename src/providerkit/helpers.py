"""Helper functions for provider discovery and loading."""

from __future__ import annotations

import concurrent.futures
import importlib
import importlib.util
import inspect
import json
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from .kit import ProviderBase

try:
    from qualitybase.services.utils import format_table
except ImportError as e:
    raise ImportError(
        "qualitybase not found. "
        "Either install qualitybase as a dependency or ensure it's available in the development environment. "
        "Run: pip install -r requirements.txt"
    ) from e

F = TypeVar("F", bound=Callable[..., Any])


def helper(func: F) -> F:
    """Mark function as a helper function."""
    func._is_helper = True  # type: ignore[attr-defined]
    return func


def load_providers_from_json(
    json_path: str | Path | None = None,
    *,
    lib_name: str = "providerkit",
    search_paths: list[str | Path] | None = None,
) -> dict[str, ProviderBase]:
    """Load providers from JSON configuration file.

    If json_path is None, searches in: .{lib_name}.json, {lib_name}.json, ~/.{lib_name}.json.
    search_paths takes precedence over lib_name if provided.
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
        with open(json_path, encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    return _load_providers_from_config(config)


def load_providers_from_config(config: list[dict[str, Any]]) -> dict[str, ProviderBase]:
    """Load providers from Python configuration list.

    Each config dict must have 'class' and optional 'config' keys.
    """
    return _load_providers_from_config(config)


def _load_providers_from_config(config: list[dict[str, Any]]) -> dict[str, ProviderBase]:
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


def _build_module_path(
    py_file: Path,
    dir_path_obj: Path,
    base_module: str,
) -> str:
    """Build module path from file path and base module.

    Args:
        py_file: Python file path.
        dir_path_obj: Base directory path.
        base_module: Base module name.

    Returns:
        Full module path.
    """
    if dir_path_obj.is_absolute():
        relative_path = py_file.relative_to(dir_path_obj)
    else:
        cwd = Path.cwd()
        abs_dir = (cwd / dir_path_obj).resolve()
        abs_file = py_file.resolve()
        relative_path = abs_file.relative_to(abs_dir)

    module_parts = list(relative_path.parts[:-1]) + [py_file.stem]
    return f"{base_module}.{'.'.join(module_parts)}"


def _get_module_path_from_file(py_file: Path) -> str | None:
    """Get module path by loading file directly.

    Args:
        py_file: Python file path.

    Returns:
        Module path or None if loading fails.
    """
    spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__name__


def _extract_providers_from_module(
    module: Any,
    module_path: str,
) -> dict[str, type[ProviderBase]]:
    """Extract provider classes from a module.

    Args:
        module: Imported module.
        module_path: Module path string.

    Returns:
        Dictionary of provider name to provider class.
    """
    providers: dict[str, type[ProviderBase]] = {}
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if (
            obj is not ProviderBase
            and issubclass(obj, ProviderBase)
            and obj.__module__ == module_path
            and "Provider" in name
        ):
            provider_name = getattr(obj, "name", "").lower()
            if provider_name:
                providers[provider_name] = obj
    return providers


def autodiscover_providers(
    dir_path: str | Path,
    *,
    base_module: str | None = None,
    exclude_files: list[str] | None = None,
) -> dict[str, type[ProviderBase]]:
    """Discover provider classes by scanning directory structure.

    If base_module is None, infers module path from directory structure.
    """
    if exclude_files is None:
        exclude_files = ["__init__.py", "base.py"]

    dir_path_obj = Path(dir_path)
    if not dir_path_obj.exists() or not dir_path_obj.is_dir():
        return {}

    providers: dict[str, type[ProviderBase]] = {}

    if base_module is None:
        inferred_base = _infer_base_module(dir_path_obj)
        if inferred_base:
            base_module = inferred_base
            cwd = Path.cwd()
            if str(cwd) not in sys.path:
                sys.path.insert(0, str(cwd))

    for py_file in dir_path_obj.rglob("*.py"):
        if py_file.name in exclude_files or py_file.name.startswith("_"):
            continue

        try:
            if base_module:
                module_path = _build_module_path(py_file, dir_path_obj, base_module)
                module = importlib.import_module(module_path)
            else:
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module_path = module.__name__

            found_providers = _extract_providers_from_module(module, module_path)
            providers.update(found_providers)
        except (ImportError, AttributeError, TypeError, ValueError):
            continue

    return providers


def filter_providers(
    providers: dict[str, ProviderBase],
    query_string: str | None = None,
    *,
    search_fields: list[str] | None = None,
    additional_fields: list[str] | None = None,
) -> dict[str, ProviderBase]:
    """Filter providers by query string.

    search_fields defaults to ["name", "display_name", "description"].
    additional_fields are extra fields to search in addition to search_fields.
    """
    if not query_string:
        return providers

    if search_fields is None:
        search_fields = ["name", "display_name", "description"]

    all_fields = list(search_fields)
    if additional_fields:
        all_fields.extend(additional_fields)

    query_lower = query_string.lower()
    filtered: dict[str, ProviderBase] = {}

    for name, provider in providers.items():
        for field in all_fields:
            value = getattr(provider, field, None)
            if value and query_lower in str(value).lower():
                filtered[name] = provider
                break

    return filtered


def _format_services_status(provider: ProviderBase) -> str:
    """Format services status as X/Y format.
    
    Args:
        provider: Provider instance to check.
        
    Returns:
        Formatted string like "2/3" or "✓" if all implemented.
    """
    if not hasattr(provider, "get_required_services") or not hasattr(provider, "is_service_implemented"):
        if hasattr(provider, "are_services_implemented") and provider.are_services_implemented():
            return "✓"
        return "✗"
    
    services = provider.get_required_services()
    if not services:
        return "N/A"
    
    implemented_count = sum(1 for service in services if provider.is_service_implemented(service))
    total_count = len(services)
    
    if implemented_count == total_count:
        return "✓"
    return f"{implemented_count}/{total_count}"


def _format_table(providers: dict[str, ProviderBase]) -> str:
    """Format providers as a table."""
    columns = [
        {"header": "Name", "width": 20, "formatter": lambda _item, key: key},
        {
            "header": "Display Name",
            "width": 30,
            "formatter": lambda item, key: getattr(item, "display_name", key),
        },
        {
            "header": "Description",
            "width": 40,
            "formatter": lambda item, _key: getattr(item, "description", "") or "",
        },
        {
            "header": "Config",
            "width": 8,
            "formatter": lambda item, _key: "✓" if hasattr(item, "is_config_ready") and item.is_config_ready() else "✗",
        },
        {
            "header": "Package",
            "width": 8,
            "formatter": lambda item, _key: "✓" if hasattr(item, "are_packages_installed") and item.are_packages_installed() else "✗",
        },
        {
            "header": "Service",
            "width": 10,
            "formatter": lambda item, _key: _format_services_status(item),
        },
    ]

    result = format_table(
        providers,
        columns=columns,
        empty_message="No providers found.",
    )
    return str(result)


def _format_json(providers: dict[str, ProviderBase]) -> str:
    if not providers:
        return "No providers found."

    json_data = []
    for name, provider in sorted(providers.items()):
        provider_data = {
            "name": name,
            "display_name": getattr(provider, "display_name", name),
            "description": getattr(provider, "description", None),
            "class": provider.__class__.__name__,
            "class_path": f"{provider.__class__.__module__}.{provider.__class__.__name__}",
        }

        if hasattr(provider, "is_config_ready"):
            provider_data["config_ready"] = provider.is_config_ready()
            config_status = provider.check_config_keys()
            provider_data["config_valid"] = [key for key, present in config_status.items() if present]
            provider_data["config_invalid"] = provider.get_missing_config_keys()

        if hasattr(provider, "are_packages_installed"):
            provider_data["packages_installed"] = provider.are_packages_installed()
            packages_status = provider.check_packages()
            provider_data["packages_installed_list"] = [pkg for pkg, installed in packages_status.items() if installed]
            provider_data["packages_missing"] = provider.get_missing_packages()

        if hasattr(provider, "are_services_implemented"):
            services_status = provider.check_services()
            services = provider.get_required_services()
            implemented_count = sum(1 for service in services if provider.is_service_implemented(service)) if services else 0
            total_count = len(services) if services else 0
            provider_data["services_implemented"] = provider.are_services_implemented()
            provider_data["services_implemented_count"] = f"{implemented_count}/{total_count}"
            provider_data["services_implemented_list"] = [service for service, implemented in services_status.items() if implemented]
            provider_data["services_missing"] = provider.get_missing_services()

        json_data.append(provider_data)
    return json.dumps(json_data, indent=2, ensure_ascii=False)


def _add_xml_config_info(provider_elem: ET.Element, provider: ProviderBase) -> None:
    """Add configuration information to XML provider element."""
    if not hasattr(provider, "is_config_ready"):
        return
    ET.SubElement(provider_elem, "config_ready").text = str(provider.is_config_ready())
    config_status = provider.check_config_keys()
    config_valid_elem = ET.SubElement(provider_elem, "config_valid")
    for key in [key for key, present in config_status.items() if present]:
        ET.SubElement(config_valid_elem, "key").text = key
    config_invalid_elem = ET.SubElement(provider_elem, "config_invalid")
    for key in provider.get_missing_config_keys():
        ET.SubElement(config_invalid_elem, "key").text = key


def _add_xml_packages_info(provider_elem: ET.Element, provider: ProviderBase) -> None:
    """Add packages information to XML provider element."""
    if not hasattr(provider, "are_packages_installed"):
        return
    ET.SubElement(provider_elem, "packages_installed").text = str(provider.are_packages_installed())
    packages_status = provider.check_packages()
    packages_installed_elem = ET.SubElement(provider_elem, "packages_installed_list")
    for pkg in [pkg for pkg, installed in packages_status.items() if installed]:
        ET.SubElement(packages_installed_elem, "package").text = pkg
    packages_missing_elem = ET.SubElement(provider_elem, "packages_missing")
    for pkg in provider.get_missing_packages():
        ET.SubElement(packages_missing_elem, "package").text = pkg


def _add_xml_services_info(provider_elem: ET.Element, provider: ProviderBase) -> None:
    """Add services information to XML provider element."""
    if not hasattr(provider, "are_services_implemented"):
        return
    services_status = provider.check_services()
    services = provider.get_required_services()
    implemented_count = sum(1 for service in services if provider.is_service_implemented(service)) if services else 0
    total_count = len(services) if services else 0
    ET.SubElement(provider_elem, "services_implemented").text = str(provider.are_services_implemented())
    ET.SubElement(provider_elem, "services_implemented_count").text = f"{implemented_count}/{total_count}"
    services_implemented_elem = ET.SubElement(provider_elem, "services_implemented_list")
    for service in [service for service, implemented in services_status.items() if implemented]:
        ET.SubElement(services_implemented_elem, "service").text = service
    services_missing_elem = ET.SubElement(provider_elem, "services_missing")
    for service in provider.get_missing_services():
        ET.SubElement(services_missing_elem, "service").text = service


def _format_xml(providers: dict[str, ProviderBase]) -> str:
    if not providers:
        return "No providers found."

    root = ET.Element("providers")
    for name, provider in sorted(providers.items()):
        provider_elem = ET.SubElement(root, "provider")
        ET.SubElement(provider_elem, "name").text = name
        ET.SubElement(provider_elem, "display_name").text = getattr(
            provider, "display_name", name
        )
        description = getattr(provider, "description", None)
        if description:
            ET.SubElement(provider_elem, "description").text = description
        ET.SubElement(provider_elem, "class").text = provider.__class__.__name__
        ET.SubElement(provider_elem, "class_path").text = (
            f"{provider.__class__.__module__}.{provider.__class__.__name__}"
        )

        _add_xml_config_info(provider_elem, provider)
        _add_xml_packages_info(provider_elem, provider)
        _add_xml_services_info(provider_elem, provider)

    ET.indent(root)
    return ET.tostring(root, encoding="unicode")


def format_providers(
    providers: dict[str, ProviderBase], output_format: str = "table"
) -> str:
    """Format providers for display.

    Supported formats: 'table', 'json', 'xml'.
    """
    if output_format == "table":
        return _format_table(providers)
    if output_format == "json":
        return _format_json(providers)
    if output_format == "xml":
        return _format_xml(providers)

    raise ValueError(
        f"Invalid format '{output_format}'. Must be 'table', 'json', or 'xml'."
    )


def _format_results_table(results: dict[str, Any]) -> str:
    """Format command results as a table."""
    if not results:
        return "No results found."

    columns = [
        {"header": "Provider", "width": 30, "formatter": lambda _item, key: key},
        {"header": "Status", "width": 10, "formatter": lambda item, _key: "✓ Success" if "result" in item else "✗ Error"},
        {"header": "Result/Error", "width": 50, "formatter": lambda item, _key: str(item.get("result", item.get("error", "")))[:47] + "..." if len(str(item.get("result", item.get("error", "")))) > 47 else str(item.get("result", item.get("error", "")))},
    ]

    result = format_table(
        results,
        columns=columns,
        empty_message="No results found.",
    )
    return str(result)


def _format_results_json(results: dict[str, Any]) -> str:
    """Format command results as JSON."""
    if not results:
        return json.dumps([], indent=2)

    json_data = []
    for name, result_data in sorted(results.items()):
        item = {
            "provider": name,
            "provider_display": result_data.get("provider", name),
        }
        if "result" in result_data:
            item["status"] = "success"
            item["result"] = result_data["result"]
        elif "errors" in result_data:
            item["status"] = "error"
            item["errors"] = result_data["errors"]
        elif "error" in result_data:
            item["status"] = "error"
            item["error"] = result_data["error"]
        json_data.append(item)

    return json.dumps(json_data, indent=2, ensure_ascii=False)


def _format_results_xml(results: dict[str, Any]) -> str:
    """Format command results as XML."""
    if not results:
        return "<?xml version='1.0' encoding='UTF-8'?>\n<results></results>"

    root = ET.Element("results")
    for name, result_data in sorted(results.items()):
        provider_elem = ET.SubElement(root, "provider")
        ET.SubElement(provider_elem, "name").text = name
        ET.SubElement(provider_elem, "display_name").text = result_data.get("provider", name)

        if "result" in result_data:
            ET.SubElement(provider_elem, "status").text = "success"
            result_elem = ET.SubElement(provider_elem, "result")
            result_elem.text = str(result_data["result"])
        elif "error" in result_data:
            ET.SubElement(provider_elem, "status").text = "error"
            error_elem = ET.SubElement(provider_elem, "error")
            error_elem.text = str(result_data["error"])

    ET.indent(root)
    return ET.tostring(root, encoding="unicode")


def _format_results_raw(results: dict[str, Any]) -> str:
    """Format command results as raw output, printing each provider's result directly."""
    if not results:
        return "No results found."

    output_lines = []
    for name, result_data in sorted(results.items()):
        provider_display = result_data.get("provider", name)
        if "result" in result_data:
            result = result_data["result"]
            output_lines.append(f"=== {provider_display} ({name}) ===")
            output_lines.append(json.dumps(result, indent=2, ensure_ascii=False))
        elif "error" in result_data:
            output_lines.append(f"=== {provider_display} ({name}) - ERROR ===")
            output_lines.append(result_data["error"])
        output_lines.append("")

    return "\n".join(output_lines).rstrip()


def _format_results(results: dict[str, Any], output_format: str = "table") -> str:
    """Format command results for display.

    Args:
        results: Dictionary mapping provider names to their results
        output_format: Output format ('table', 'json', 'xml', or 'raw')

    Returns:
        Formatted string
    """
    if output_format == "table":
        return _format_results_table(results)
    if output_format == "json":
        return _format_results_json(results)
    if output_format == "xml":
        return _format_results_xml(results)
    if output_format == "raw":
        return _format_results_raw(results)

    raise ValueError(
        f"Invalid format '{output_format}'. Must be 'table', 'json', 'xml', or 'raw'."
    )


def _infer_base_module(dir_path_obj: Path) -> str | None:
    """Infer base module name from directory path.

    Args:
        dir_path_obj: Directory path object.

    Returns:
        Base module name or None.
    """
    if dir_path_obj.is_absolute():
        cwd = Path.cwd()
        try:
            relative_path = dir_path_obj.relative_to(cwd)
            return str(relative_path).replace("/", ".").replace("\\", ".")
        except ValueError:
            return None
    return str(dir_path_obj).replace("/", ".").replace("\\", ".")


def _load_providers_from_dir(
    dir_path: str | Path,
    base_module: str | None = None,
) -> dict[str, ProviderBase]:
    """Load providers from directory.

    Args:
        dir_path: Directory path to scan.
        base_module: Base module name. If None, autodiscover_providers will use
            _get_module_path_from_file() to load files directly.

    Returns:
        Dictionary of provider instances.
    """
    dir_path_obj = Path(dir_path).resolve()
    if not dir_path_obj.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    if not dir_path_obj.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")

    provider_classes = autodiscover_providers(dir_path, base_module=base_module)
    providers: dict[str, ProviderBase] = {}
    for name, provider_class in provider_classes.items():
        try:
            provider_file = Path(inspect.getfile(provider_class)).resolve()
            relative_path = provider_file.relative_to(dir_path_obj)
            provider_instance = provider_class(path=str(relative_path))
            provider_instance.class_name = provider_class.__name__  # type: ignore[attr-defined]
            provider_instance.class_path = provider_class.__module__  # type: ignore[attr-defined]
            providers[name] = provider_instance
        except (TypeError, ValueError):
            continue
    return providers


def _find_package_providers_dir(lib_name: str) -> Path | None:
    """Find providers directory in the package.

    Args:
        lib_name: Package name

    Returns:
        Path to providers directory if found, None otherwise
    """
    try:
        package_module = importlib.import_module(lib_name)
        if hasattr(package_module, "__file__") and package_module.__file__:
            package_dir = Path(package_module.__file__).parent
            providers_dir = package_dir / "providers"
            if providers_dir.exists() and providers_dir.is_dir():
                return providers_dir
    except (ImportError, AttributeError):
        pass
    return None


def _filter_providers_by_attributes(
    providers: dict[str, ProviderBase],
    attribute_search: dict[str, str],
) -> dict[str, ProviderBase]:
    """Filter providers by attribute search criteria.

    Args:
        providers: Dictionary of providers to filter.
        attribute_search: Dictionary mapping attribute names to search values (case-insensitive substring match).

    Returns:
        Filtered dictionary of providers.
    """
    if not attribute_search:
        return providers

    filtered: dict[str, ProviderBase] = {}
    for name, provider in providers.items():
        matches = True
        for attr_name, search_value in attribute_search.items():
            attr_value = getattr(provider, attr_name, None)
            if attr_value is None:
                matches = False
                break
            if callable(attr_value):
                attr_value = attr_value()
            search_lower = search_value.lower()
            if isinstance(attr_value, bool):
                search_bool = search_lower in ("true", "1", "yes", "on")
                if attr_value != search_bool:
                    matches = False
                    break
            else:
                if search_lower not in str(attr_value).lower():
                    matches = False
                    break
        if matches:
            filtered[name] = provider

    return filtered


def get_providers(
    *,
    json: str | Path | None = None,
    lib_name: str = "providerkit",
    config: list[dict[str, Any]] | None = None,
    dir_path: str | Path | None = None,
    base_module: str | None = None,
    query_string: str | None = None,
    search_fields: list[str] | None = None,
    attribute_search: dict[str, str] | None = None,
    format: str | None = None,
    **kwargs: Any,
) -> dict[str, ProviderBase] | str:
    """Load providers from various sources.

    Priority: json > config > dir_path > package providers directory.
    If format is provided, returns formatted string instead of dict.
    """
    additional_args = kwargs.get("additional_args", {})

    if config is not None:
        providers = load_providers_from_config(config, **additional_args)
    elif dir_path is not None:
        providers = _load_providers_from_dir(dir_path, base_module, **additional_args)
    elif json is not None:
        providers = load_providers_from_json(json_path=json, lib_name=lib_name, **additional_args)
    else:
        providers_dir = _find_package_providers_dir(lib_name)
        if providers_dir:
            if base_module is None:
                base_module = f"{lib_name}.providers"
            providers = _load_providers_from_dir(providers_dir, base_module, **additional_args)
        else:
            providers = {}

    if query_string:
        additional_fields = None
        if dir_path is not None:
            additional_fields = ["class_name", "class_path"]
        providers = filter_providers(
            providers, query_string, search_fields=search_fields, additional_fields=additional_fields
        )

    if attribute_search:
        providers = _filter_providers_by_attributes(providers, attribute_search)

    if format:
        return format_providers(providers, format)

    return providers


def try_providers(  # noqa: C901
    command: str,
    providers: dict[str, ProviderBase] | None = None,
    json: str | Path | None = None,
    lib_name: str = "providerkit",
    config: list[dict[str, Any]] | None = None,
    dir_path: str | Path | None = None,
    base_module: str | None = None,
    query_string: str | None = None,
    search_fields: list[str] | None = None,
    attribute_search: dict[str, str] | None = None,
    format: str | None = None,
    **kwargs: Any,
) -> dict[str, Any] | str:
    """Execute provider method on all providers and return all successful results.

    Args:
        command: Command/method name to execute on providers
        format: Optional output format ('table', 'json', or 'xml'). If None, returns raw dict.

    Returns:
        Dictionary mapping provider names to their results, or formatted string if format is specified.
    """
    if providers is None:
        providers_result = get_providers(
            json=json,
            lib_name=lib_name,
            config=config,
            dir_path=dir_path,
            base_module=base_module,
            query_string=query_string,
            search_fields=search_fields,
            attribute_search=attribute_search,
        )

        if isinstance(providers_result, str):
            raise RuntimeError("No providers available")
        providers = providers_result

    if not providers:
        raise RuntimeError("No providers available")

    results: dict[str, Any] = {}
    providers_without_method: list[str] = []
    for provider_name, provider in providers.items():
        if hasattr(provider, "provider_can_be_used") and provider.provider_can_be_used is False:
            continue
        
        errors: list[str] = []
        
        if not provider.are_packages_installed():
            missing_packages = provider.get_missing_packages()
            if missing_packages:
                errors.append(f"Packages missing: {', '.join(missing_packages)}")
            else:
                errors.append("package_missing")
        
        if not provider.is_config_ready():
            missing_config = provider.get_missing_config_keys()
            if missing_config:
                errors.append(f"Config missing: {', '.join(missing_config)}")
            else:
                errors.append("config_missing")
        
        if not provider.is_service_implemented(command):
            services = provider.get_required_services()
            if services:
                implemented_count = sum(1 for service in services if provider.is_service_implemented(service))
                total_count = len(services)
                errors.append(f"Service missing: {command} ({implemented_count}/{total_count} services implemented)")
            else:
                errors.append(f"Service missing: {command}")
        
        if errors:
            results[provider_name] = {"errors": errors, "provider": provider.display_name}
            continue
        
        try:
            method = getattr(provider, command, None)
            if method is None or not callable(method):
                providers_without_method.append(provider_name)
                continue
            result = method(**kwargs.get("additional_args", {}))
            results[provider_name] = {"result": result, "provider": provider.display_name}
        except Exception as e:
            results[provider_name] = {"error": str(e), "provider": provider.display_name}

    if not results and providers_without_method:
        error_msg = f"Method '{command}' not found in any provider."
        if len(providers_without_method) <= 5:
            error_msg += f" Checked providers: {', '.join(providers_without_method)}"
        else:
            error_msg += f" Checked {len(providers_without_method)} providers (none implement '{command}')"
        if format:
            return error_msg
        return {"error": error_msg}

    if format:
        return _format_results(results, format)

    return results


def try_providers_first(  # noqa: C901
    command: str,
    providers: dict[str, ProviderBase] | None = None,
    json: str | Path | None = None,
    lib_name: str = "providerkit",
    config: list[dict[str, Any]] | None = None,
    dir_path: str | Path | None = None,
    base_module: str | None = None,
    query_string: str | None = None,
    search_fields: list[str] | None = None,
    attribute_search: dict[str, str] | None = None,
    format: str | None = None,
    **kwargs: Any,
) -> Any:
    """Execute provider method on each provider until one succeeds.

    Args:
        command: Command/method name to execute on providers
        format: Optional output format ('table', 'json', or 'xml'). If None, returns raw result.

    Returns:
        First successful result from any provider, or formatted string if format is specified.
        If format is None and no provider succeeds, raises RuntimeError.
    """
    if providers is None:
        providers_result = get_providers(
            json=json,
            lib_name=lib_name,
            config=config,
            dir_path=dir_path,
            base_module=base_module,
            query_string=query_string,
            search_fields=search_fields,
            attribute_search=attribute_search,
        )

        if isinstance(providers_result, str):
            raise RuntimeError("No providers available")
        providers = providers_result

    if not providers:
        raise RuntimeError("No providers available")

    results: dict[str, Any] = {}
    providers_without_method: list[str] = []
    for provider_name, provider in providers.items():
        if hasattr(provider, "provider_can_be_used") and provider.provider_can_be_used is False:
            continue
        
        errors: list[str] = []
        
        if not provider.are_packages_installed():
            missing_packages = provider.get_missing_packages()
            if missing_packages:
                errors.append(f"Packages missing: {', '.join(missing_packages)}")
            else:
                errors.append("package_missing")
        
        if not provider.is_config_ready():
            missing_config = provider.get_missing_config_keys()
            if missing_config:
                errors.append(f"Config missing: {', '.join(missing_config)}")
            else:
                errors.append("config_missing")
        
        if not provider.are_services_implemented():
            services = provider.get_required_services()
            if services:
                implemented_count = sum(1 for service in services if provider.is_service_implemented(service))
                total_count = len(services)
                missing_services = provider.get_missing_services()
                if missing_services:
                    errors.append(f"Services missing: {', '.join(missing_services)} ({implemented_count}/{total_count} services implemented)")
                else:
                    errors.append(f"Services missing ({implemented_count}/{total_count} services implemented)")
            else:
                errors.append("service_missing")
        
        if errors:
            results[provider_name] = {"errors": errors, "provider": provider.display_name}
            continue
        
        try:
            method = getattr(provider, command, None)
            if method is None or not callable(method):
                providers_without_method.append(provider_name)
                continue
            result = method(**kwargs.get("additional_args", {}))
            result_data = {"result": result, "provider": provider.display_name}
            results[provider_name] = result_data

            if format:
                single_result = {provider_name: result_data}
                return _format_results(single_result, format)

            return result
        except Exception as e:
            results[provider_name] = {"error": str(e), "provider": provider.display_name}

    if not results and providers_without_method:
        error_msg = f"Method '{command}' not found in any provider."
        if len(providers_without_method) <= 5:
            error_msg += f" Checked providers: {', '.join(providers_without_method)}"
        else:
            error_msg += f" Checked {len(providers_without_method)} providers (none implement '{command}')"
        raise RuntimeError(error_msg)

    if format:
        return _format_results(results, format)

    raise RuntimeError(f"Command '{command}' failed on all providers")
