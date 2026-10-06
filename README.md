# TeraBox + NotyDrive Telegram Bot
Ready-to-run Telegram bot architecture with provider adapters, Free/Premium membership,
admin controls, local JSON persistence, and MongoDB-ready storage separation.

IMPORTANT: Provider adapters do not bypass CAPTCHA, DRM, authentication, anti-bot systems,
or other access controls. Configure only an official/permitted API or direct-download mechanism.

Setup:
1. Python 3.11+
2. pip install -r requirements.txt
3. Copy .env.example to .env
4. Set BOT_TOKEN and ADMIN_IDS
5. python -m bot

Commands:
/start /help /profile /premium /cancel
/admin /users /stats /givepremium /removepremium /block /unblock /broadcast

MongoDB is intentionally optional. Replace JSONRepository later with a MongoRepository
without changing the membership/business logic.
