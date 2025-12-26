"""Cost management mixin for providers."""

from __future__ import annotations

from typing import Any


class CostMixin:
    """Mixin for managing service costs.

    This mixin adds functionality to:
    - Get cost for a service
    - Check if cost method is implemented
    - Calculate cost from data when applicable
    """

    def is_cost_implemented(self, service_name: str) -> bool:
        """Check if cost property for a service is implemented.

        Args:
            service_name: Name of the service method.

        Returns:
            True if cost property exists, False otherwise.
        """
        cost_property = f"cost_{service_name}"
        return hasattr(self, cost_property)

    def get_cost(self, service_name: str) -> Any:
        """Get cost for a service.

        Args:
            service_name: Name of the service method.

        Returns:
            Cost property value, "free" if cost is "free" or 0.
        """
        cost_property = f"cost_{service_name}"
        cost = getattr(self, cost_property)
        if cost in ("free", 0):
            return "free"
        return cost

    def calculate_cost(self, service_name: str, **data: Any) -> Any:
        """Calculate cost for a service from data.

        Args:
            service_name: Name of the service method.
            **data: Data required for cost calculation.

        Returns:
            Calculated cost value, "free" if cost is "free" or 0.
        """
        calculate_method = f"calculate_cost_{service_name}"
        method = getattr(self, calculate_method)
        cost = method(**data)
        if cost in ("free", 0):
            return "free"
        return cost

    def get_costs(self) -> dict[str, Any]:
        """Get costs for all services.

        Returns:
            Dictionary mapping service names to their costs.
        """
        services = getattr(self, "services", [])
        return {service: self.get_cost(service) for service in services}

