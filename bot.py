import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
import json
from datetime import datetime
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Update
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
LOGGER = logging.getLogger

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # https://luffy-auto-post.onrender.com


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="CosmicBotz",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.uptime = datetime.now()
        self.set_parse_mode(ParseMode.HTML)
        LOGGER(__name__).info(f"✅ Bot started as @{self.username}")

        for admin_id in ADMIN_IDS:
            try:
                await self.send_message(
                    chat_id=admin_id,
                    text="<b><blockquote>🤖 CosmicBotz Started ✅</blockquote></b>",
                )
            except Exception as e:
                LOGGER(__name__).warning(f"Could not notify admin {admin_id}: {e}")

    async def stop(self, *args):
        await super().stop()
        LOGGER(__name__).info("⛔ Bot stopped.")


app = Bot()


@app.on_message(filters.command("start"))
async def cmd_start(client, message):
    LOGGER(__name__).info(f"✅ /start from {message.from_user.id}")
    await message.reply("👋 <b>Hello! CosmicBotz is working!</b>")


@app.on_message(filters.command("ping"))
async def cmd_ping(client, message):
    LOGGER(__name__).info(f"✅ /ping from {message.from_user.id}")
    await message.reply("🏓 <b>Pong!</b>")


# ── Webhook handler ───────────────────────────────────────────────────────────
async def handle_update(request):
    try:
        data = await request.json()
        LOGGER(__name__).info(f"📩 Update: {json.dumps(data)[:200]}")
        await app.handle_update(data)
    except Exception as e:
        LOGGER(__name__).error(f"Update error: {e}")
    return web.Response(text="OK")


async def set_webhook():
    import aiohttp as http
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook = f"{WEBHOOK_URL}/webhook"
    async with http.ClientSession() as session:
        async with session.post(url, json={"url": webhook, "drop_pending_updates": True}) as r:
            result = await r.json()
            LOGGER(__name__).info(f"setWebhook → {result}")


async def main():
    # Start web server first so Render health check passes immediately
    web_application = web.Application()
    web_application.router.add_get("/", lambda r: web.Response(text="CosmicBotz Running!"))
    web_application.router.add_get("/health", lambda r: web.Response(text="OK"))
    web_application.router.add_post("/webhook", handle_update)

    runner = web.AppRunner(web_application)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    LOGGER(__name__).info(f"🌐 Web server on port {PORT}")

    # Start bot
    await app.start()

    # Register webhook with Telegram
    await set_webhook()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
