import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from .config import *
from .storage import JSONRepository
from .providers import detect_link, fetch_permitted_download
from .keyboards import main_menu

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
log = logging.getLogger("downloader")
repo = JSONRepository()

def is_admin(uid):
    return uid in ADMIN_IDS

def limits(user):
    return (PREMIUM_DAILY_LIMIT, PREMIUM_MAX_MB) if user.is_premium() else (FREE_DAILY_LIMIT, FREE_MAX_MB)

async def start(update, context):
    u = update.effective_user
    repo.get(u.id, username=u.username, first_name=u.first_name)
    await update.message.reply_text(
        "👋 Welcome!\n\nSend a TeraBox/NotyDrive share link.\n"
        "Use /profile for limits and /premium for membership.",
        reply_markup=main_menu())

async def help_cmd(update, context):
    await update.message.reply_text(
        "/start - Start\n/profile - Profile\n/premium - Premium\n/cancel - Cancel\n"
        "/admin - Admin help\n\nSend a supported share link.")

async def profile(update, context):
    u = repo.get(update.effective_user.id, username=update.effective_user.username,
                 first_name=update.effective_user.first_name)
    daily, max_mb = limits(u)
    status = f"Premium until {u.premium_until}" if u.is_premium() else "Free"
    await update.message.reply_text(
        f"👤 {u.first_name or 'User'}\n🆔 {u.user_id}\n⭐ {status}\n"
        f"📊 Today: {u.downloads_today}/{daily}\n📦 Max: {max_mb} MB\n"
        f"📥 Total: {u.total_downloads}")

async def premium(update, context):
    await update.message.reply_text(
        f"💎 PREMIUM\n\nPlan: {PREMIUM_DEFAULT_DAYS} days\n"
        f"Daily limit: {PREMIUM_DAILY_LIMIT}\nMax file: {PREMIUM_MAX_MB} MB\n\n"
        "Payment gateway is intentionally not hard-coded. Admin can activate with /givepremium.")

async def cancel(update, context):
    await update.message.reply_text("⏹️ No active task in this starter build.")

async def handle_link(update, context):
    u = update.effective_user
    user = repo.get(u.id, username=u.username, first_name=u.first_name)
    if user.blocked:
        return await update.message.reply_text("🚫 Your account is blocked.")
    info = detect_link(update.message.text or "")
    if not info:
        return
    daily, max_mb = limits(user)
    if user.downloads_today >= daily:
        return await update.message.reply_text("⚠️ Daily limit reached. Upgrade to Premium.")
    await update.message.reply_text(f"🔎 {info.provider.title()} link detected. Resolving...")
    try:
        direct_url, filename, size = await fetch_permitted_download(info.url, info.provider)
        if size and size > max_mb * 1024 * 1024:
            return await update.message.reply_text(f"📦 File exceeds your {max_mb} MB limit.")
        await update.message.reply_text(
            "✅ A permitted direct URL was resolved. Add the Telegram upload step "
            "after configuring the provider adapter for your deployment.")
        user.downloads_today += 1
        user.total_downloads += 1
        repo.put(user)
    except NotImplementedError:
        await update.message.reply_text(
            "⚠️ This provider adapter is not configured.\n\n"
            "The bot will not bypass CAPTCHA/DRM/anti-bot protections. "
            "Configure an official/permitted API or direct-download method.")
    except Exception:
        log.exception("provider error")
        await update.message.reply_text("❌ Download failed. Try again later.")

async def admin(update, context):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔ Admin only.")
    await update.message.reply_text(
        "/users\n/stats\n/givepremium USER_ID DAYS\n/removepremium USER_ID\n"
        "/block USER_ID\n/unblock USER_ID\n/broadcast MESSAGE")

async def users(update, context):
    if is_admin(update.effective_user.id):
        us = repo.all()
        await update.message.reply_text(f"👥 Users: {len(us)}\n💎 Premium: {sum(x.is_premium() for x in us)}")

async def stats(update, context):
    if is_admin(update.effective_user.id):
        us = repo.all()
        await update.message.reply_text(f"📊 Users: {len(us)}\n📥 Downloads: {sum(x.total_downloads for x in us)}")

async def givepremium(update, context):
    if not is_admin(update.effective_user.id): return
    if len(context.args) != 2:
        return await update.message.reply_text("Usage: /givepremium USER_ID DAYS")
    u = repo.set_premium(int(context.args[0]), int(context.args[1]))
    await update.message.reply_text(f"💎 Premium active until {u.premium_until}")

async def removepremium(update, context):
    if not is_admin(update.effective_user.id): return
    repo.remove_premium(int(context.args[0]))
    await update.message.reply_text("✅ Premium removed.")

async def block(update, context):
    if not is_admin(update.effective_user.id): return
    u = repo.get(int(context.args[0])); u.blocked = True; repo.put(u)
    await update.message.reply_text("🚫 Blocked.")

async def unblock(update, context):
    if not is_admin(update.effective_user.id): return
    u = repo.get(int(context.args[0])); u.blocked = False; repo.put(u)
    await update.message.reply_text("✅ Unblocked.")

async def broadcast(update, context):
    if not is_admin(update.effective_user.id): return
    text = " ".join(context.args).strip()
    if not text: return await update.message.reply_text("Usage: /broadcast MESSAGE")
    sent = 0
    for u in repo.all():
        if u.blocked: continue
        try:
            await context.bot.send_message(u.user_id, text)
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"📣 Sent: {sent}")

async def callbacks(update, context):
    q = update.callback_query
    await q.answer()
    if q.data == "premium":
        await q.message.reply_text(f"💎 Premium {PREMIUM_DEFAULT_DAYS} days / {PREMIUM_DAILY_LIMIT} daily")
    elif q.data == "profile":
        await q.message.reply_text("Use /profile")
    elif q.data == "help":
        await q.message.reply_text("Send a supported share link.")
    else:
        await q.message.reply_text("Send a TeraBox or NotyDrive share link.")

def main():
    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN missing. Add BOT_TOKEN in Render Environment Variables."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    for cmd, fn in [
        ("start", start),
        ("help", help_cmd),
        ("profile", profile),
        ("premium", premium),
        ("cancel", cancel),
        ("admin", admin),
        ("users", users),
        ("stats", stats),
        ("givepremium", givepremium),
        ("removepremium", removepremium),
        ("block", block),
        ("unblock", unblock),
        ("broadcast", broadcast),
    ]:
        app.add_handler(CommandHandler(cmd, fn))

    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link,
        )
    )

    log.info("Starting bot")

    app.run_polling(
        close_loop=True,
        drop_pending_updates=True,
    )