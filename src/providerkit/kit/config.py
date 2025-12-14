"""Configuration management mixin for providers."""

from __future__ import annotations

import os
from typing import Any


class ConfigMixin:
    """Mixin for managing provider configuration.

    This mixin adds functionality to:
    - Define required configuration keys
    - Initialize configuration from dict or environment variables
    - Access configuration values with automatic fallback to environment
    """

    config_keys: list[str] = []
    config_prefix: str = ""

    def _init_config(self, config: dict[str, Any] | None = None) -> None:
        """Initialize configuration.

        Args:
            config: Configuration dictionary. If None, uses empty dict.
        """
        if not hasattr(self, "_config"):
            self._config: dict[str, Any] = {}
        if config is not None:
            self._config = self._filter_config(config)
            self.clear_config_cache()

    def _filter_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Extract the subset of config keys declared by the provider.

        Args:
            config: Raw configuration dictionary.

        Returns:
            Filtered configuration dictionary with only declared keys.
        """
        if not self.config_keys:
            return dict(config)
        return {key: config[key] for key in self.config_keys if key in config}

    def _get_config_or_env(self, key: str, default: Any = None) -> Any:
        """Get config value from config dict or environment variable.

        Priority order:
        1. Config dict (highest priority)
        2. Environment variable with prefix format: {PREFIX}_{PROVIDER_NAME}_{KEY}
        3. Default parameter (lowest priority)

        Args:
            key: Configuration key name.
            default: Default value if not found in config or env.

        Returns:
            Configuration value from config, env, or default.
        """
        config = getattr(self, "_config", {})
        value = config.get(key)
        if value is not None:
            return value

        if not self.config_prefix:
            return default

        provider_name = getattr(self, "name", "").upper().replace("-", "_")
        env_key = f"{self.config_prefix}_{provider_name}_{key.upper()}"
        return os.getenv(env_key, default)

    def configure(self, config: dict[str, Any], *, replace: bool = False) -> Any:
        """Update provider configuration.

        Args:
            config: Configuration dictionary to merge or replace.
            replace: If True, replace existing config. If False, merge with existing.

        Returns:
            Self for method chaining.
        """
        if not hasattr(self, "_config"):
            self._config: dict[str, Any] = {}
        if replace:
            self._config = self._filter_config(config)
        else:
            self._config.update(self._filter_config(config))
        self.clear_config_cache()
        return self

    @property
    def config(self) -> dict[str, Any]:
        """Access configuration values."""
        if not hasattr(self, "_config"):
            self._config: dict[str, Any] = {}
        return self._config

    def check_config_keys(self, config: dict[str, Any] | None = None) -> dict[str, bool]:
        """Check if all required configuration keys are present.

        Args:
            config: Optional config dict to check. If None, uses current config.

        Returns:
            Dictionary mapping config keys to their presence status.
        """
        if config is not None:
            return {key: key in config for key in self.config_keys}

        if hasattr(self, "_config_keys_cache"):
            return self._config_keys_cache

        config_to_check = getattr(self, "_config", {})
        status = {key: key in config_to_check for key in self.config_keys}
        self._config_keys_cache = status
        return status

    def clear_config_cache(self) -> None:
        """Clear the cached config keys check results.

        Call this method if configuration is modified.
        """
        if hasattr(self, "_config_keys_cache"):
            delattr(self, "_config_keys_cache")

    def is_config_ready(self, config: dict[str, Any] | None = None) -> bool:
        """Check if all required configuration keys are present.

        Args:
            config: Optional config dict to check. If None, uses current config.

        Returns:
            True if all required config keys are present, False otherwise.
        """
        status = self.check_config_keys(config)
        return all(status.values())

    def get_missing_config_keys(self, config: dict[str, Any] | None = None) -> list[str]:
        """Get list of required configuration keys that are missing.

        Args:
            config: Optional config dict to check. If None, uses current config.

        Returns:
            List of missing configuration keys.
        """
        status = self.check_config_keys(config)
        return [key for key, present in status.items() if not present]

