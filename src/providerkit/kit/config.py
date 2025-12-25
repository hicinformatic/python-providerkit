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
            filtered = self._filter_config(config)
            self._config = filtered
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
        3. Environment variable without prefix: {PROVIDER_NAME}_{KEY}
        4. Environment variable without prefix: {KEY}
        5. Default parameter (lowest priority)

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

        provider_name = getattr(self, "name", "").upper().replace("-", "_")
        key_upper = key.upper()

        if self.config_prefix:
            env_key_with_prefix = f"{self.config_prefix}_{provider_name}_{key_upper}"
            value = os.getenv(env_key_with_prefix)
            if value is not None:
                return value

        env_key_provider = f"{provider_name}_{key_upper}"
        value = os.getenv(env_key_provider)
        if value is not None:
            return value

        value = os.getenv(key_upper)
        if value is not None:
            return value

        return default

    def configure(self, config: dict[str, Any], *, replace: bool = False) -> Any:
        """Update provider configuration.

        Args:
            config: Configuration dictionary to merge or replace.
            replace: If True, replace existing config. If False, merge with existing.

        Returns:
            Self for method chaining.
        """
        if not hasattr(self, "_config"):
            self._config = {}
        filtered = self._filter_config(config)
        if replace:
            self._config = filtered
        else:
            self._config.update(filtered)
        self.clear_config_cache()
        return self

    @property
    def config(self) -> dict[str, Any]:
        """Access configuration values."""
        if not hasattr(self, "_config"):
            self._config = {}
        return self._config

    def check_config_keys(self, config: dict[str, Any] | None = None) -> dict[str, bool]:
        """Check if all required configuration keys are present.

        A key is considered present if:
        - It's in the config dict, OR
        - It has a default value in config_defaults, OR
        - It can be retrieved from environment variables

        Args:
            config: Optional config dict to check. If None, uses current config.

        Returns:
            Dictionary mapping config keys to their presence status.
        """
        config_defaults = getattr(self, "config_defaults", {})
        
        if config is not None:
            status: dict[str, bool] = {}
            for key in self.config_keys:
                present = key in config
                if not present:
                    present = key in config_defaults
                if not present:
                    value = self._get_config_or_env(key)
                    present = value is not None
                status[key] = present
            return status

        if hasattr(self, "_config_keys_cache"):
            cache: dict[str, bool] = getattr(self, "_config_keys_cache", {})
            return cache

        config_to_check = getattr(self, "_config", {})
        status: dict[str, bool] = {}
        for key in self.config_keys:
            present = key in config_to_check
            if not present:
                present = key in config_defaults
            if not present:
                value = self._get_config_or_env(key)
                present = value is not None
            status[key] = present
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

    @property
    def missing_config_keys(self) -> list[str]:
        """Get list of required configuration keys that are missing.

        Returns:
            List of missing configuration keys.
        """
        return self.get_missing_config_keys()