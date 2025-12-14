"""Base classes for provider management."""

from __future__ import annotations

from .package import PackageMixin
from .urls import UrlsMixin
from .config import ConfigMixin
from .service import ServiceMixin

class ProviderBase(PackageMixin, UrlsMixin, ConfigMixin, ServiceMixin):
    """Base class for providers with basic identification information."""

    name: str
    display_name: str
    description: str | None
    mandatory_base_fields: list[str] = ["name", "display_name"]

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize a provider with required identification.

        Args:
            **kwargs: Provider attributes:
                - name: Unique identifier for the provider (required).
                - display_name: Human-readable name for the provider (defaults to name if not provided).
                - description: Optional description of the provider.

        Raises:
            ValueError: If name or display_name is empty or not provided.
        """
        for field in self.mandatory_base_fields:
            setattr(self, field, kwargs.get(field, getattr(self, field)))
            if not getattr(self, field):
                raise ValueError(f"{field} is required and cannot be empty")

        self.description = kwargs.get("description", self.description)
