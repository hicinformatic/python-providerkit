"""Chinese alphabet provider."""

from __future__ import annotations

from .. import AlphabetProvider


class ChinaAlphabetProvider(AlphabetProvider):
    """Provider for retrieving the Chinese alphabet."""

    name = "china_alphabet"
    display_name = "China Alphabet Provider"
    description = "Provider for Chinese alphabet (Hanzi characters)"
    services = ["get_alphabet"]
    config_keys = ["CHINA_API_KEY", "CHINA_API_SECRET", "CHINA_ENCODING"]
    required_packages = ["chinese-alphabet", "hanzi-utils"]
    site_url = "https://www.gov.cn"
    documentation_url = "https://www.gov.cn/zhengce/zhengceku"
    status_url = "https://www.gov.cn/xinwen"
    country_code = "CN"
    continent = "asia"
    country = "China"

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize the Chinese alphabet provider."""
        super().__init__(**kwargs)

    def get_alphabet(self) -> list[str]:
        """Get the Chinese alphabet.

        Returns:
            List of Chinese characters (common Hanzi).
        """
        return [
            "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
            "人", "大", "小", "中", "国", "水", "火", "木", "金", "土",
            "天", "地", "日", "月", "山", "川", "田", "口", "手", "目"
        ]

