

from pyrogram import Client
from bot.utils.logger import LOGGER
from bot.config.config import Config

class User(Client):
    def __init__(self):
        super().__init__(
            "userbot",
            api_hash=Config.API_HASH,
            api_id=Config.API_ID,
            workers=20
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        return (self, usr_bot_me.id)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped. Bye.")
