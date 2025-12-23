"""Spanish alphabet provider."""

from __future__ import annotations

from .. import AlphabetProvider


class SpainAlphabetProvider(AlphabetProvider):
    """Provider for retrieving the Spanish alphabet."""

    name = "spain_alphabet"
    display_name = "Spain Alphabet Provider"
    description = "Provider for Spanish alphabet (Latin with Ñ)"
    services = ["get_alphabet"]
    config_keys = ["SPAIN_API_KEY", "SPAIN_REGION", "SPAIN_ENCODING"]
    required_packages = ["spanish-alphabet", "spanish-char-utils"]
    site_url = "https://www.lamoncloa.gob.es"
    documentation_url = "https://www.lamoncloa.gob.es/Paginas/index.aspx"
    status_url = "https://www.lamoncloa.gob.es/Paginas/actividad.aspx"
    country_code = "ES"
    continent = "europe"
    country = "Spain"

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize the Spanish alphabet provider."""
        super().__init__(**kwargs)

    def get_alphabet(self) -> list[str]:
        """Get the Spanish alphabet.

        Returns:
            List of Spanish alphabet characters including Ñ.
        """
        base = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
        special = ["Ñ", "ñ"]
        diacritics = ["Á", "É", "Í", "Ó", "Ú", "Ü", "á", "é", "í", "ó", "ú", "ü"]
        lowercase = [c.lower() for c in base if c not in special]
        return sorted(set(base + special + diacritics + lowercase))

