"""Package dependency management mixin for providers."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from types import ModuleType


class PackageMixin:
    """Mixin for managing required packages and checking their installation.

    This mixin adds functionality to:
    - Define required packages
    - Check if packages are installed
    - List all required packages
    """

    required_packages: list[str] = []

    def get_required_packages(self) -> list[str]:
        """Get the list of required packages for this provider.

        Returns:
            List of package names that are required for this provider.
        """
        return getattr(self, "required_packages", [])

    def is_package_installed(self, package_name: str) -> bool:
        """Check if a specific package is installed.

        Args:
            package_name: Name of the package to check.

        Returns:
            True if the package is installed, False otherwise.
        """
        normalized_name = package_name.replace("-", "_").replace(".", "_")

        try:
            spec = importlib.util.find_spec(normalized_name)
            if spec is None:
                spec = importlib.util.find_spec(package_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def check_packages(self) -> dict[str, bool]:
        """Check installation status of all required packages.

        Returns:
            Dictionary mapping package names to their installation status.
        """
        if hasattr(self, "_packages_cache"):
            cache: dict[str, bool] = getattr(self, "_packages_cache", {})
            return cache

        packages = self.get_required_packages()
        status: dict[str, bool] = {pkg: self.is_package_installed(pkg) for pkg in packages}
        self._packages_cache = status
        return status

    def clear_packages_cache(self) -> None:
        """Clear the cached package check results.

        Call this method if packages are dynamically added or modified.
        """
        if hasattr(self, "_packages_cache"):
            delattr(self, "_packages_cache")

    def are_packages_installed(self) -> bool:
        """Check if all required packages are installed.

        Returns:
            True if all required packages are installed, False otherwise.
        """
        status = self.check_packages()
        return all(status.values())

    def get_missing_packages(self) -> list[str]:
        """Get list of required packages that are not installed.

        Returns:
            List of package names that are required but not installed.
        """
        status = self.check_packages()
        return [pkg for pkg, installed in status.items() if not installed]

    @property
    def missing_packages(self) -> list[str]:
        """Get list of required packages that are not installed.

        Returns:
            List of package names that are required but not installed.
        """
        return self.get_missing_packages()

    @classmethod
    def safe_import_packages(cls, packages: list[str], globals_dict: dict[str, Any] | None = None) -> None:
        """Import packages safely at module level.

        This class method can be called at module level to import packages
        before the class is instantiated.

        Args:
            packages: List of package names to import.
            globals_dict: Dictionary (typically from globals()) to make
                imported modules available in the calling namespace.
        """
        for package_name in packages:
            normalized_name = package_name.replace("-", "_").replace(".", "_")

            try:
                module = importlib.import_module(normalized_name)
                sys.modules[package_name] = module
                if globals_dict is not None:
                    globals_dict[package_name] = module
                    globals_dict[normalized_name] = module
            except (ImportError, ModuleNotFoundError):
                try:
                    module = importlib.import_module(package_name)
                    sys.modules[normalized_name] = module
                    if globals_dict is not None:
                        globals_dict[package_name] = module
                        globals_dict[normalized_name] = module
                except (ImportError, ModuleNotFoundError):
                    continue

    def safe_import(self, globals_dict: dict[str, Any] | None = None) -> None:
        """Import required packages safely, skipping those that are not installed.

        This method loops through required_packages and imports only those that are
        available. Packages that are not installed are skipped and not imported.
        This is useful for provider discovery when packages may not be installed.

        The imported modules are registered in sys.modules and can be used
        throughout the code after calling this method.

        Args:
            globals_dict: Optional dictionary (typically from globals()) to make
                imported modules available in the calling namespace.
        """
        packages = self.get_required_packages()
        for package_name in packages:
            normalized_name = package_name.replace("-", "_").replace(".", "_")

            try:
                module = importlib.import_module(normalized_name)
                sys.modules[package_name] = module
                if globals_dict is not None:
                    globals_dict[package_name] = module
                    globals_dict[normalized_name] = module
            except (ImportError, ModuleNotFoundError):
                try:
                    module = importlib.import_module(package_name)
                    sys.modules[normalized_name] = module
                    if globals_dict is not None:
                        globals_dict[package_name] = module
                        globals_dict[normalized_name] = module
                except (ImportError, ModuleNotFoundError):
                    continue

