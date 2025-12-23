"""French alphabet provider."""

from __future__ import annotations

from .. import AlphabetProvider


class FranceAlphabetProvider(AlphabetProvider):
    """Provider for retrieving the French alphabet."""

    name = "france_alphabet"
    display_name = "France Alphabet Provider"
    description = "Provider for French alphabet (Latin with diacritics)"
    services = ["get_alphabet"]
    config_keys = ["FRANCE_API_KEY", "FRANCE_LOCALE", "FRANCE_DIACRITICS"]
    required_packages = ["french-alphabet", "diacritics-handler"]
    site_url = "https://www.gouvernement.fr"
    documentation_url = "https://www.gouvernement.fr/qui-est-membre-du-gouvernement"
    status_url = "https://www.gouvernement.fr/actualites"
    country_code = "FR"
    continent = "europe"
    country = "France"

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize the French alphabet provider."""
        super().__init__(**kwargs)

    def get_alphabet(self) -> list[str]:
        """Get the French alphabet.

        Returns:
            List of French alphabet characters including diacritics.
        """
        base = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
        diacritics = ["À", "Â", "Ä", "È", "É", "Ê", "Ë", "Î", "Ï", "Ô", "Ö", "Ù", "Û", "Ü", "Ÿ"]
        lowercase = [c.lower() for c in base + diacritics]
        return sorted(set(base + diacritics + lowercase))

