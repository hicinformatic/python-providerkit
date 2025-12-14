"""URL management mixin for providers."""

from __future__ import annotations


class UrlsMixin:
    """Mixin for managing provider URLs.

    This mixin adds functionality to store and access:
    - Documentation URL
    - Provider website URL
    - Status page URL
    """

    documentation_url: str | None = None
    site_url: str | None = None
    status_url: str | None = None

    def get_documentation_url(self) -> str | None:
        """Get the documentation URL for this provider.

        Returns:
            Documentation URL or None if not set.
        """
        return getattr(self, "documentation_url", None)

    def get_site_url(self) -> str | None:
        """Get the website URL for this provider.

        Returns:
            Website URL or None if not set.
        """
        return getattr(self, "site_url", None)

    def get_status_url(self) -> str | None:
        """Get the status page URL for this provider.

        Returns:
            Status page URL or None if not set.
        """
        return getattr(self, "status_url", None)

    def get_urls(self) -> dict[str, str | None]:
        """Get all URLs for this provider.

        Returns:
            Dictionary mapping URL types to their values.
        """
        return {
            "documentation": self.get_documentation_url(),
            "site": self.get_site_url(),
            "status": self.get_status_url(),
        }

