from bot import Bot
from ..config import Config
from pyrogram import Client, filters
from pyrogram.types import Message

from ..database import a_filter

media_filter = filters.document | filters.video | filters.audio | filters.photo


channel_filter = filters.chat(Config.CHANNELS_KP1) | \
                 filters.chat(Config.CHANNELS_KP2) | \
                 filters.chat(Config.CHANNELS_KP3) | \
                 filters.chat(Config.CHANNELS_KP4) | \
                 filters.chat(Config.CHANNELS_KP5) | \
                 filters.chat(Config.CHANNELS_KP6) | \
                 filters.chat(Config.CHANNELS_SE) | \
                 filters.chat(Config.CHANNELS_KPCT) | \
                 filters.chat(Config.CHANNELS_KSCPR) | \
                 filters.chat(Config.CHANNELS_MCPR) 

@Client.on_message(channel_filter & media_filter)
async def media_handler(bot: Bot, message: Message):
    """Media Handler"""
    for file_type in ("document", "video", "audio", "photo"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    if file_type == "photo":
        media.file_name = message.caption
        media.mime_type = "image/jpg"
    media.caption = message.caption
    media.chat_id = message.chat.id
    media.message_id = message.id
    await a_filter.save_file(media)
