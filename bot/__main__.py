"""
Telegram bot entry point.

Render Start Command:
    python -m bot

Important:
Do NOT use asyncio.run() here because python-telegram-bot's
run_polling() manages the asyncio event loop itself.
"""

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from .config import BOT_TOKEN, LOG_LEVEL
from .app import (
    start,
    help_cmd,
    profile,
    premium,
    cancel,
    admin,
    users,
    stats,
    givepremium,
    removepremium,
    block,
    unblock,
    broadcast,
    callbacks,
    handle_link,
)


logging.basicConfig(
    level=getattr(LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

log = logging.getLogger("downloader")


def build_application() -> Application:
    """Create and configure the Telegram application."""

    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN is missing. "
            "Please add BOT_TOKEN in Render Environment Variables."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    # User commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("premium", premium))
    application.add_handler(CommandHandler("cancel", cancel))

    # Admin commands
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("givepremium", givepremium))
    application.add_handler(CommandHandler("removepremium", removepremium))
    application.add_handler(CommandHandler("block", block))
    application.add_handler(CommandHandler("unblock", unblock))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Inline keyboard buttons
    application.add_handler(
        CallbackQueryHandler(callbacks)
    )

    # Normal text / download links
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link,
        )
    )

    return application


def main() -> None:
    """
    Start the Telegram bot.

    Do NOT use asyncio.run() here.
    Application.run_polling() manages the event loop.
    """

    application = build_application()

    log.info("Starting bot")

    application.run_polling(
        close_loop=True,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()