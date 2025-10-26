"""Tests for the top-level e_tachibana package."""

from e_tachibana import ETachibana


def test_dev_mode_uses_demo_base_url() -> None:
    """ETachibana should point to the demo endpoint when dev_mode=True."""
    client = ETachibana(
        user_id="dummy",
        password="dummy",
        dev_mode=True,
        api_version="v4r7",
    )
    try:
        assert client.base_url == "https://demo-kabuka.e-shiten.jp/e_api_v4r7/"
    finally:
        client.close()

