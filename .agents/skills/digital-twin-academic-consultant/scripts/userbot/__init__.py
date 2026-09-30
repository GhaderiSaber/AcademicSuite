"""Userbot modular subpackage for SaberTelethonUserbot.

Exports:
    - AdminCommandDispatcher: Handles commands from Academic Desk and admin chats.
    - CallbackQueryDispatcher: Handles inline button callbacks.
    - InlineQueryDispatcher: Handles inline query searches and quotes.
    - setup_inbound_listeners: Sets up private DM burst buffers and listeners.
    - is_valid_telegram_button_url: URL validation helper for Telegram inline buttons.
"""

from userbot.admin_dispatcher import AdminCommandDispatcher
from userbot.callback_dispatcher import CallbackQueryDispatcher
from userbot.inline_dispatcher import InlineQueryDispatcher
from userbot.inbound_listener import setup_inbound_listeners
from userbot.utils import is_valid_telegram_button_url

__all__ = [
    "AdminCommandDispatcher",
    "CallbackQueryDispatcher",
    "InlineQueryDispatcher",
    "setup_inbound_listeners",
    "is_valid_telegram_button_url",
]
