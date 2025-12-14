"""Package dependency management mixin for providers."""

from __future__ import annotations

import importlib.util


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
            return self._packages_cache

        packages = self.get_required_packages()
        status = {pkg: self.is_package_installed(pkg) for pkg in packages}
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

