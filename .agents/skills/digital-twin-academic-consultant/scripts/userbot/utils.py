"""Utility functions for Telethon Userbot package."""

from typing import Optional


def is_valid_telegram_button_url(url: Optional[str]) -> bool:
    """Check if URL is valid for Telegram Button.url (must be external http/https or tg://, not localhost)."""
    if not url or not isinstance(url, str):
        return False
    u = url.strip().lower()
    if "localhost" in u or "127.0.0.1" in u:
        return False
    return u.startswith("https://") or u.startswith("http://") or u.startswith("tg://")
