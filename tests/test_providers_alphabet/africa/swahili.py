"""Swahili alphabet provider."""

from __future__ import annotations

from .. import AlphabetProvider


class SwahiliAlphabetProvider(AlphabetProvider):
    """Provider for retrieving the Swahili alphabet."""

    name = "swahili_alphabet"
    display_name = "Swahili Alphabet Provider"
    description = "Provider for Swahili alphabet (Latin-based)"
    services = ["get_alphabet"]
    config_keys = ["SWAHILI_API_KEY", "SWAHILI_COUNTRY", "SWAHILI_DIALECT"]
    required_packages = ["swahili-alphabet", "swahili-lang"]
    site_url = "https://www.tanzania.go.tz"
    documentation_url = "https://www.tanzania.go.tz/about"
    status_url = "https://www.tanzania.go.tz/news"
    country_code = "TZ"
    continent = "africa"
    country = "Tanzania"

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize the Swahili alphabet provider."""
        super().__init__(**kwargs)

    def get_alphabet(self) -> list[str]:
        """Get the Swahili alphabet.

        Returns:
            List of Swahili alphabet characters (Latin without Q and X).
        """
        base = [chr(i) for i in range(ord("A"), ord("Z") + 1) if chr(i) not in ["Q", "X"]]
        lowercase = [c.lower() for c in base]
        return sorted(set(base + lowercase))

