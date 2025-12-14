"""Service implementation mixin for providers."""

from __future__ import annotations


class ServiceMixin:
    """Mixin for managing required service methods.

    This mixin adds functionality to:
    - Define required service methods
    - Check if service methods are implemented
    - Validate service implementation completeness
    """

    services: list[str] = []

    def get_required_services(self) -> list[str]:
        """Get the list of required service methods for this provider.

        Returns:
            List of service method names that must be implemented.
        """
        return getattr(self, "services", [])

    def is_service_implemented(self, service_name: str) -> bool:
        """Check if a specific service method is implemented.

        Args:
            service_name: Name of the service method to check.

        Returns:
            True if the service method exists and is callable, False otherwise.
        """
        method = getattr(self, service_name, None)
        return callable(method) and not isinstance(method, type)

    def check_services(self) -> dict[str, bool]:
        """Check implementation status of all required services.

        Returns:
            Dictionary mapping service names to their implementation status.
        """
        if hasattr(self, "_services_cache"):
            return self._services_cache

        services = self.get_required_services()
        status = {service: self.is_service_implemented(service) for service in services}
        self._services_cache = status
        return status

    def clear_services_cache(self) -> None:
        """Clear the cached service check results.

        Call this method if services are dynamically added or modified.
        """
        if hasattr(self, "_services_cache"):
            delattr(self, "_services_cache")

    def are_services_implemented(self) -> bool:
        """Check if all required services are implemented.

        Returns:
            True if all required services are implemented, False otherwise.
        """
        status = self.check_services()
        return all(status.values())

    def get_missing_services(self) -> list[str]:
        """Get list of required services that are not implemented.

        Returns:
            List of service names that are required but not implemented.
        """
        status = self.check_services()
        return [service for service, implemented in status.items() if not implemented]

