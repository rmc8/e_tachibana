from __future__ import annotations

import os
from typing import Final

import httpx

TACHIBANA_API_VERSION_ENV: Final[str] = "TACHIBANA_API_VERSION"
TACHIBANA_USER_ID_ENV: Final[str] = "TACHIBANA_USER_ID"
TACHIBANA_PASSWORD_ENV: Final[str] = "TACHIBANA_PASSWORD"
DEFAULT_API_VERSION: Final[str] = "v4r7"

PRODUCTION_BASE_URLS: Final[dict[str, str]] = {
    "v4r7": "https://kabuka.e-shiten.jp/e_api_v4r7/",
    "v4r8": "https://kabuka.e-shiten.jp/e_api_v4r8/",
}

DEVELOPMENT_BASE_URLS: Final[dict[str, str]] = {
    "v4r7": "https://demo-kabuka.e-shiten.jp/e_api_v4r7/",
    "v4r8": "https://demo-kabuka.e-shiten.jp/e_api_v4r8/",
}


def _get_api_version(explicit_version: str | None) -> str:
    """Resolve the API version to use based on the explicit value or environment."""
    raw_version: str = str(
        explicit_version
        or os.getenv(TACHIBANA_API_VERSION_ENV, "")
        or DEFAULT_API_VERSION
    )
    version = raw_version.lower()
    if version not in PRODUCTION_BASE_URLS:
        raise ValueError(
            f"Unsupported API version '{version}'. Supported: {', '.join(PRODUCTION_BASE_URLS)}."
        )
    return version


def _get_base_url(version: str, dev_mode: bool) -> str:
    """Return the base URL for either production or development."""
    url_map = DEVELOPMENT_BASE_URLS if dev_mode else PRODUCTION_BASE_URLS
    try:
        return url_map[version]
    except KeyError as exc:  # pragma: no cover - version is validated earlier
        raise ValueError(f"Missing base URL for version '{version}'.") from exc


class ETachibana:
    """Thin convenience wrapper around the Tachibana e-branch HTTP API."""

    def __init__(
        self,
        user_id: str | None = None,
        password: str | None = None,
        *,
        dev_mode: bool = False,
        api_version: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        """
        Initialize the client and point it to either the demo or production environment.

        Parameters
        ----------
        user_id:
            Tachibana e-branch user ID. Falls back to the `TACHIBANA_USER_ID` env var.
        password:
            Tachibana e-branch password. Falls back to the `TACHIBANA_PASSWORD` env var.
        dev_mode:
            When True the client talks to the demo (development) endpoints so we can
            develop and test against the sandbox.
        api_version:
            API version such as `v4r7`. Defaults to the `TACHIBANA_API_VERSION` env var
            or `v4r7`.
        timeout:
            Default timeout applied to every HTTP request (seconds).
        """
        resolved_user_id = user_id or os.getenv(TACHIBANA_USER_ID_ENV, "")
        resolved_password = password or os.getenv(TACHIBANA_PASSWORD_ENV, "")
        if not resolved_user_id or not resolved_password:
            raise ValueError(
                "User ID and password must be provided to initialize ETachibana."
            )

        version = _get_api_version(api_version)
        self.base_url = _get_base_url(version, dev_mode)
        self.user_id = resolved_user_id
        self.password = resolved_password
        self.dev_mode = dev_mode
        self.api_version = version
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()
