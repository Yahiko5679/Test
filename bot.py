import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from datetime import datetime
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
LOGGER = logging.getLogger


# ── Web server (starts FIRST so Render health check passes) ───────────────────
web_app = web.Application()
web_app.router.add_get("/", lambda r: web.Response(text="CosmicBotz Running!"))
web_app.router.add_get("/health", lambda r: web.Response(text="OK"))


async def start_web():
    runner = web.AppRunner(web_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    LOGGER(__name__).info(f"🌐 Web server running on port {PORT}")


# ── Bot ───────────────────────────────────────────────────────────────────────
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


# ── Entry point ───────────────────────────────────────────────────────────────
async def main():
    await start_web()        # web server first — Render health check passes
    await app.start()        # then connect to Telegram
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
