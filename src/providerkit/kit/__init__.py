"""Base classes for provider management."""

from __future__ import annotations

from .config import ConfigMixin
from .package import PackageMixin
from .service import ServiceMixin
from .urls import UrlsMixin


class ProviderBase(PackageMixin, UrlsMixin, ConfigMixin, ServiceMixin):
    """Base class for providers with basic identification information."""

    name: str
    display_name: str
    description: str | None
    mandatory_base_fields: list[str] = ["name", "display_name"]
    path: str | None = None

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
            setattr(self, field, kwargs.pop(field, getattr(self, field)))
            if not getattr(self, field):
                raise ValueError(f"{field} is required and cannot be empty")

        config = kwargs.pop("config", None)
        if config is not None:
            if isinstance(config, dict):
                self._init_config(config)
            else:
                self._init_config(None)

        for field, value in kwargs.items():
            setattr(self, field, value)

