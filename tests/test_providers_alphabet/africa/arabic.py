"""Arabic alphabet provider."""

from __future__ import annotations

from .. import AlphabetProvider


class ArabicAlphabetProvider(AlphabetProvider):
    """Provider for retrieving the Arabic alphabet."""

    name = "arabic_alphabet"
    display_name = "Arabic Alphabet Provider"
    description = "Provider for Arabic alphabet (Abjad script)"
    services = ["get_alphabet"]
    config_keys = ["ARABIC_API_KEY", "ARABIC_DIRECTION", "ARABIC_SCRIPT"]
    required_packages = ["arabic-alphabet", "arabic-text-processor"]
    site_url = "https://www.un.org/ar"
    documentation_url = "https://www.un.org/ar/about-un"
    status_url = "https://www.un.org/ar/news"
    country_code = "SA"
    continent = "africa"
    country = "Saudi Arabia"

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize the Arabic alphabet provider."""
        super().__init__(**kwargs)

    def get_alphabet(self) -> list[str]:
        """Get the Arabic alphabet.

        Returns:
            List of Arabic alphabet characters.
        """
        return [
            "ا", "ب", "ت", "ث", "ج", "ح", "خ",
            "د", "ذ", "ر", "ز", "س", "ش", "ص",
            "ض", "ط", "ظ", "ع", "غ", "ف", "ق",
            "ك", "ل", "م", "ن", "ه", "و", "ي"
        ]

