import asyncio
import logging
from datetime import datetime
from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode
from Plugins import web_server
from config import (
    API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, PORT
)

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
            plugins={"root": "Plugins"},
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.uptime = datetime.now()
        self.set_parse_mode(ParseMode.HTML)

        LOGGER(__name__).info(f"✅ Bot started as @{self.username}")

        # Notify owner
        for admin_id in ADMIN_IDS:
            try:
                await self.send_message(
                    chat_id=admin_id,
                    text="<b><blockquote>🤖 CosmicBotz Started ✅</blockquote></b>",
                )
            except Exception as e:
                LOGGER(__name__).warning(f"Could not notify admin {admin_id}: {e}")

        # Start web server
        try:
            runner = web.AppRunner(await web_server())
            await runner.setup()
            await web.TCPSite(runner, "0.0.0.0", PORT).start()
            LOGGER(__name__).info(f"🌐 Web server running on port {PORT}")
        except Exception as e:
            LOGGER(__name__).error(f"Web server failed: {e}")

    async def stop(self, *args):
        await super().stop()
        LOGGER(__name__).info("⛔ Bot stopped.")


if __name__ == "__main__":
    Bot().run()
