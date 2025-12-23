"""Test helper functions for loading alphabet providers.

This test module tests all helper functions from providerkit.helpers
using the alphabet providers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from providerkit import (
    autodiscover_providers,
    get_providers,
    load_providers_from_config,
    load_providers_from_json,
)


def test_load_providers_from_json_with_lib_name() -> None:
    """Test load_providers_from_json with lib_name parameter."""
    providers = load_providers_from_json(lib_name="alphabet")

    assert len(providers) == 6, f"Expected 6 providers, got {len(providers)}"
    assert "china_alphabet" in providers
    assert "japan_alphabet" in providers
    assert "france_alphabet" in providers
    assert "spain_alphabet" in providers
    assert "arabic_alphabet" in providers
    assert "swahili_alphabet" in providers


def test_load_providers_from_json_with_explicit_path() -> None:
    """Test load_providers_from_json with explicit json_path."""
    json_path = Path(".alphabet.json")
    if not json_path.exists():
        pytest.skip(".alphabet.json file not found")

    providers = load_providers_from_json(json_path=json_path)

    assert len(providers) == 6
    for provider_name in ["china_alphabet", "japan_alphabet", "france_alphabet", "spain_alphabet", "arabic_alphabet", "swahili_alphabet"]:
        assert provider_name in providers


def test_load_providers_from_json_with_search_paths() -> None:
    """Test load_providers_from_json with custom search_paths."""
    search_paths = [Path(".alphabet.json"), Path("alphabet.json")]

    providers = load_providers_from_json(search_paths=search_paths)

    assert len(providers) >= 0


def test_load_providers_from_config() -> None:
    """Test load_providers_from_config with Python configuration."""
    config = [
        {
            "class": "tests.test_providers_alphabet.asia.china.ChinaAlphabetProvider",
            "config": {
                "CHINA_API_KEY": "test_key",
                "CHINA_API_SECRET": "test_secret",
                "CHINA_ENCODING": "UTF-8",
            },
        },
        {
            "class": "tests.test_providers_alphabet.asia.japan.JapanAlphabetProvider",
            "config": {
                "JAPAN_API_KEY": "test_key",
                "JAPAN_API_TOKEN": "test_token",
                "JAPAN_CHARSET": "UTF-8",
            },
        },
        {
            "class": "tests.test_providers_alphabet.europe.france.FranceAlphabetProvider",
            "config": {
                "FRANCE_API_KEY": "test_key",
                "FRANCE_LOCALE": "fr_FR",
                "FRANCE_DIACRITICS": "true",
            },
        },
    ]

    providers = load_providers_from_config(config)

    assert len(providers) == 3
    assert "china_alphabet" in providers
    assert "japan_alphabet" in providers
    assert "france_alphabet" in providers

    china_provider = providers["china_alphabet"]
    assert china_provider.config["CHINA_API_KEY"] == "test_key"
    assert china_provider.config["CHINA_ENCODING"] == "UTF-8"


def test_load_providers_from_config_with_kwargs() -> None:
    """Test load_providers_from_config with kwargs in provider config."""
    config = [
        {
            "class": "tests.test_providers_alphabet.africa.arabic.ArabicAlphabetProvider",
            "config": {
                "ARABIC_API_KEY": "test_key",
            },
            "kwargs": {
                "description": "Test Arabic provider",
            },
        },
    ]

    providers = load_providers_from_config(config)

    assert len(providers) == 1
    assert "arabic_alphabet" in providers
    arabic_provider = providers["arabic_alphabet"]
    assert arabic_provider.config["ARABIC_API_KEY"] == "test_key"
    assert arabic_provider.description == "Test Arabic provider"


def test_autodiscover_providers() -> None:
    """Test autodiscover_providers to discover alphabet providers."""
    provider_classes = autodiscover_providers(
        "tests/test_providers_alphabet",
        base_module="tests.test_providers_alphabet",
    )

    assert len(provider_classes) == 6
    assert "china_alphabet" in provider_classes
    assert "japan_alphabet" in provider_classes
    assert "france_alphabet" in provider_classes
    assert "spain_alphabet" in provider_classes
    assert "arabic_alphabet" in provider_classes
    assert "swahili_alphabet" in provider_classes

    for name, provider_class in provider_classes.items():
        assert provider_class is not None
        assert hasattr(provider_class, "name")


def test_autodiscover_providers_with_exclude_files() -> None:
    """Test autodiscover_providers with exclude_files parameter."""
    provider_classes = autodiscover_providers(
        "tests/test_providers_alphabet",
        base_module="tests.test_providers_alphabet",
        exclude_files=["__init__.py"],
    )

    assert len(provider_classes) == 6


def test_autodiscover_providers_instantiate() -> None:
    """Test that autodiscovered providers can be instantiated."""
    provider_classes = autodiscover_providers(
        "tests/test_providers_alphabet",
        base_module="tests.test_providers_alphabet",
    )

    china_class = provider_classes.get("china_alphabet")
    assert china_class is not None

    china_provider = china_class()
    assert china_provider.name == "china_alphabet"
    assert len(china_provider.get_alphabet()) > 0


def test_get_providers_with_lib_name() -> None:
    """Test get_providers with lib_name parameter."""
    providers = get_providers(lib_name="alphabet")

    assert len(providers) == 6
    assert "china_alphabet" in providers
    assert "japan_alphabet" in providers


def test_get_providers_with_json_path() -> None:
    """Test get_providers with explicit json path."""
    json_path = Path(".alphabet.json")
    if not json_path.exists():
        pytest.skip(".alphabet.json file not found")

    providers = get_providers(json=json_path)

    assert len(providers) == 6


def test_get_providers_with_config() -> None:
    """Test get_providers with Python config."""
    config = [
        {
            "class": "tests.test_providers_alphabet.europe.spain.SpainAlphabetProvider",
            "config": {
                "SPAIN_API_KEY": "test_key",
                "SPAIN_REGION": "es",
                "SPAIN_ENCODING": "UTF-8",
            },
        },
        {
            "class": "tests.test_providers_alphabet.africa.swahili.SwahiliAlphabetProvider",
            "config": {
                "SWAHILI_API_KEY": "test_key",
                "SWAHILI_COUNTRY": "tanzania",
                "SWAHILI_DIALECT": "standard",
            },
        },
    ]

    providers = get_providers(config=config)

    assert len(providers) == 2
    assert "spain_alphabet" in providers
    assert "swahili_alphabet" in providers


def test_get_providers_with_dir_path() -> None:
    """Test get_providers with dir_path for autodiscovery."""
    providers = get_providers(
        dir_path="tests/test_providers_alphabet",
        base_module="tests.test_providers_alphabet",
    )

    assert len(providers) == 6
    for provider_name in ["china_alphabet", "japan_alphabet", "france_alphabet", "spain_alphabet", "arabic_alphabet", "swahili_alphabet"]:
        assert provider_name in providers


def test_load_providers_from_json_empty_when_file_not_found() -> None:
    """Test that load_providers_from_json returns empty dict when file not found."""
    providers = load_providers_from_json(json_path="nonexistent.json")

    assert isinstance(providers, dict)
    assert len(providers) == 0


def test_load_providers_from_config_empty_when_invalid_class() -> None:
    """Test that load_providers_from_config handles invalid class paths."""
    config = [
        {
            "class": "nonexistent.module.InvalidProvider",
            "config": {},
        },
    ]

    providers = load_providers_from_config(config)

    assert isinstance(providers, dict)
    assert len(providers) == 0


def test_load_providers_from_config_empty_when_missing_class() -> None:
    """Test that load_providers_from_config handles missing class field."""
    config = [
        {
            "config": {"SOME_KEY": "value"},
        },
    ]

    providers = load_providers_from_config(config)

    assert isinstance(providers, dict)
    assert len(providers) == 0


def test_all_providers_have_alphabet() -> None:
    """Test that all loaded providers can return alphabet."""
    providers = load_providers_from_json(lib_name="alphabet")

    for name, provider in providers.items():
        alphabet = provider.get_alphabet()
        assert isinstance(alphabet, list), f"Provider {name} alphabet is not a list"
        assert len(alphabet) > 0, f"Provider {name} alphabet is empty"


def test_all_providers_inherit_from_provider_base() -> None:
    """Test that all loaded providers inherit from ProviderBase."""
    from providerkit import ProviderBase

    providers = load_providers_from_json(lib_name="alphabet")

    for name, provider in providers.items():
        assert isinstance(provider, ProviderBase), f"Provider {name} does not inherit from ProviderBase"


def test_load_providers_from_config_with_full_alphabet_json() -> None:
    """Test loading providers using the actual alphabet.json content."""
    json_path = Path(".alphabet.json")
    if not json_path.exists():
        pytest.skip(".alphabet.json file not found")

    with open(json_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    providers = load_providers_from_config(config_data)

    assert len(providers) == 6
    for provider_name in ["china_alphabet", "japan_alphabet", "france_alphabet", "spain_alphabet", "arabic_alphabet", "swahili_alphabet"]:
        assert provider_name in providers


def test_providers_configuration_persistence() -> None:
    """Test that provider configuration is properly persisted."""
    config = [
        {
            "class": "tests.test_providers_alphabet.asia.china.ChinaAlphabetProvider",
            "config": {
                "CHINA_API_KEY": "persisted_key",
                "CHINA_API_SECRET": "persisted_secret",
                "CHINA_ENCODING": "UTF-8",
            },
        },
    ]

    providers = load_providers_from_config(config)
    china_provider = providers["china_alphabet"]

    assert china_provider.config["CHINA_API_KEY"] == "persisted_key"
    assert china_provider.config["CHINA_API_SECRET"] == "persisted_secret"
    assert china_provider.is_config_ready()

