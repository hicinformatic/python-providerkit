"""Japanese alphabet provider."""

from __future__ import annotations

from .. import AlphabetProvider


class JapanAlphabetProvider(AlphabetProvider):
    """Provider for retrieving the Japanese alphabet."""

    name = "japan_alphabet"
    display_name = "Japan Alphabet Provider"
    description = "Provider for Japanese alphabet (Hiragana)"
    services = ["get_alphabet"]
    config_keys = ["JAPAN_API_KEY", "JAPAN_API_TOKEN", "JAPAN_CHARSET"]
    required_packages = ["japanese-alphabet", "hiragana-parser"]
    site_url = "https://www.gov-online.go.jp"
    documentation_url = "https://www.gov-online.go.jp/useful"
    status_url = "https://www.gov-online.go.jp/eng/publicity"
    country_code = "JP"
    continent = "asia"
    country = "Japan"

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize the Japanese alphabet provider."""
        super().__init__(**kwargs)

    def get_alphabet(self) -> list[str]:
        """Get the Japanese alphabet.

        Returns:
            List of Hiragana characters.
        """
        return [
            "あ", "い", "う", "え", "お",
            "か", "き", "く", "け", "こ",
            "さ", "し", "す", "せ", "そ",
            "た", "ち", "つ", "て", "と",
            "な", "に", "ぬ", "ね", "の",
            "は", "ひ", "ふ", "へ", "ほ",
            "ま", "み", "む", "め", "も",
            "や", "ゆ", "よ",
            "ら", "り", "る", "れ", "ろ",
            "わ", "を", "ん"
        ]

