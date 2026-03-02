# config.py MUST be imported first — it sets os.chdir and sys.path
from config import (
    API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, PORT
)

import asyncio
import logging
from datetime import datetime
from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
LOGGER = logging.getLogger


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="CosmicBotz",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
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

        # Web server for Render keep-alive
        try:
            web_app = web.Application()
            web_app.router.add_get("/", lambda r: web.Response(text="CosmicBotz Running!"))
            web_app.router.add_get("/health", lambda r: web.Response(text="OK"))
            runner = web.AppRunner(web_app)
            await runner.setup()
            await web.TCPSite(runner, "0.0.0.0", PORT).start()
            LOGGER(__name__).info(f"🌐 Web server on port {PORT}")
        except Exception as e:
            LOGGER(__name__).error(f"Web server failed: {e}")

    async def stop(self, *args):
        await super().stop()
        LOGGER(__name__).info("⛔ Bot stopped.")


if __name__ == "__main__":
    Bot().run()
