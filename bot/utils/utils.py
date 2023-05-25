from bot import Bot, bot
from pyrogram import enums
from pyrogram.types import Message

from ..config import Config
from ..database import usersDB
from .broadcastHelper import send_broadcast_to_user
from .logger import LOGGER

LOG_TEXT_USER = "#USER\n**New User**\n\nName: [{}](tg://user?id={})\nUser_ID: <code>{}</code>"


LOG = LOGGER(__name__)


async def check_user(message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        name = message.from_user.first_name
    elif message.chat.type in [enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
        name = message.chat.title
    else:
        name = ""
    is_new = await usersDB.handle_user(message.chat.id, name)
    if is_new:
        await bot.send_message(
            Config.LOG_CHANNEL, LOG_TEXT_USER.format(name, message.chat.id, message.chat.id)
        )
        LOG.info(f"newUser - {message.from_user.first_name}  ----- {message.from_user.id}")
    else:
        user = await usersDB.col.find_one({"_id": message.chat.id})  # type: ignore
        if user.get("blocked"):
            pending = user.get("pending_broadcast")
            if pending:
                msg = await bot.get_messages(Config.LOG_CHANNEL, pending)
                if msg:
                    settings = user.get("broadcast_info", {})
                    is_copy = settings.get("is_copy", True)
                    is_pin = settings.get("is_pin", False)

                    await message.reply(
                        "Nice to see you again.\nYou missed an update from developer because you blocked me for a while :(\nHere is it"
                    )
                    _, msg_id = await send_broadcast_to_user(message.chat.id, msg, is_copy, is_pin)  # type: ignore
                    await usersDB.broadcast_id(message.chat.id, pending)
                    await usersDB.update_broadcast_msg(message.chat.id, msg_id)
                await usersDB.update_blocked(message.chat.id, False)
                await usersDB.remove_pending(message.chat.id)
