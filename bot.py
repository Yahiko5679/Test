import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, filters
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, ADMIN_IDS, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
LOGGER = logging.getLogger(__name__)

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # https://luffy-auto-post.onrender.com
WEBHOOK_PATH = "/webhook"

# ── Bot & Dispatcher ──────────────────────────────────────────────────────────
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ── Handlers ──────────────────────────────────────────────────────────────────
@dp.message(filters.Command("start"))
async def cmd_start(message: Message):
    LOGGER.info(f"✅ /start from {message.from_user.id}")
    await message.reply("👋 <b>Hello! CosmicBotz is working!</b>")


@dp.message(filters.Command("ping"))
async def cmd_ping(message: Message):
    LOGGER.info(f"✅ /ping from {message.from_user.id}")
    await message.reply("🏓 <b>Pong!</b>")


# ── Startup & Shutdown ────────────────────────────────────────────────────────
async def on_startup():
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="<b><blockquote>🤖 CosmicBotz Started ✅</blockquote></b>",
            )
        except Exception as e:
            LOGGER.warning(f"Could not notify admin {admin_id}: {e}")

    # Set webhook
    webhook = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"
    await bot.set_webhook(url=webhook, drop_pending_updates=True)
    LOGGER.info(f"✅ Webhook set to {webhook}")


async def on_shutdown():
    await bot.delete_webhook()
    LOGGER.info("⛔ Webhook deleted. Bot stopped.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    # Health endpoints
    app.router.add_get("/", lambda r: web.Response(text="CosmicBotz Running!"))
    app.router.add_get("/health", lambda r: web.Response(text="OK"))

    # Webhook handler
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    LOGGER.info(f"🌐 Starting web server on port {PORT}")
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
