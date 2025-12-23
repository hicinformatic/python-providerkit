from __future__ import annotations

from providerkit import ProviderBase


class AlphabetProvider(ProviderBase):
    services = ["get_alphabet", "calculate_letters"]

    def calculate_format_count(self, letters: list[str]) -> int:
        """Calculate count format: number of elements in the list.

        Args:
            letters: List of letters/characters.

        Returns:
            Count of elements.
        """
        return len(letters)

    def calculate_format_len(self, letters: list[str]) -> int:
        """Calculate len format: sum of length of each element.

        Args:
            letters: List of letters/characters.

        Returns:
            Sum of lengths of all elements.
        """
        return sum(len(letter) for letter in letters)

    def calculate_format_bytes(self, letters: list[str]) -> int:
        """Calculate bytes format: total size in bytes.

        Args:
            letters: List of letters/characters.

        Returns:
            Total size in bytes of all elements.
        """
        return sum(len(letter.encode("utf-8")) for letter in letters)

    def calculate_letters(self, format: str = "count") -> int:
        """Calculate letters statistics based on format.

        Args:
            format: Calculation format. Options: "count", "len", "bytes" (or "poid").

        Returns:
            Calculated value based on format.
        """
        letters = self.get_alphabet()

        if format == "count":
            return self.calculate_format_count(letters)
        elif format == "len":
            return self.calculate_format_len(letters)
        elif format in ("bytes", "poid"):
            return self.calculate_format_bytes(letters)
        else:
            raise ValueError(
                f"Invalid format '{format}'. Must be 'count', 'len', or 'bytes'."
            )


__all__ = ["AlphabetProvider"]