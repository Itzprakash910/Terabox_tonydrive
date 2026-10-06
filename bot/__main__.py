"""
Telegram bot entry point.

Render Start Command:
    python -m bot

IMPORTANT:
Do not use asyncio.run() here.
The application.run_polling() function manages the event loop.
"""

from .app import main


if __name__ == "__main__":
    main()