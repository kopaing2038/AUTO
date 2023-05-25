from pyrogram.types import Message

from bot import Bot
from ..database import usersDB
from .cache import Cache
from .utils import check_user


def is_banned(func):
    """decorator for banned users"""

    async def checker(bot: Bot, msg: Message):
        chat = msg.chat.id
        if chat in Cache.BANNED:
            reason = await usersDB.get_ban_status(msg.from_user.id)
            b_reason = reason.get("ban_reason")
            await msg.reply(f"You are banned to use me.\nReason - {b_reason}")
            await check_user(msg)
            msg.stop_propagation()
        else:
            await check_user(msg)
            return await func(bot, msg)

    return checker
