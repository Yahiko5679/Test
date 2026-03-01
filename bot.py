import asyncio
import logging
import os
from aiohttp import web
from pyrogram import Client, filters

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

API_ID    = int(os.environ.get("API_ID", "0"))
API_HASH  = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PORT      = int(os.environ.get("PORT", "8080"))

app = Client(
    name="CosmicBotz",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,       # no session file — always fresh
)


@app.on_message(filters.command("start"))
async def start(client, message):
    logger.info(f"✅ /start from {message.from_user.id}")
    await message.reply("👋 Hello! Bot is working!")


@app.on_message(filters.command("ping"))
async def ping(client, message):
    logger.info(f"✅ /ping from {message.from_user.id}")
    await message.reply("🏓 Pong!")


async def health_server():
    web_app = web.Application()
    web_app.router.add_get("/", lambda r: web.Response(text="OK"))
    web_app.router.add_get("/health", lambda r: web.Response(text="OK"))
    runner = web.AppRunner(web_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    logger.info(f"Health server on port {PORT}")


async def main():
    await health_server()
    await app.start()
    me = await app.get_me()
    logger.info(f"✅ Bot started as @{me.username}")
    logger.info("Waiting for messages...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
