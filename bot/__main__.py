import asyncio

from .database import usersDB

from bot import bot
from .utils.cache import Cache
from .utils.idle import idle
from .utils.initialization import check_pending
from .utils.logger import LOGGER
from bot.plugins.clone import clone_start, clone_stop

async def main():
    await bot.start()
    Cache.BANNED = await usersDB.get_banned_users()
    bot.loop.create_task(check_pending(bot))
    LOGGER(__name__).info(f"Banned Users list updated {Cache.BANNED}")
    LOGGER(__name__).info("Listening for updates from API..")    
    await clone_start()
    await idle()
    await bot.stop()
    await clone_stop()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
