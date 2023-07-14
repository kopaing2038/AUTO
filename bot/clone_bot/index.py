import asyncio
import re
from typing import AsyncGenerator, Optional, Union
from pyrogram import Client, filters, types, enums
from pyrogram.errors import (ChannelInvalid, UsernameInvalid,
                             UsernameNotModified)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import Bot
from bot.config.config import Config
from bot.clone_bot.autofilter import a_filter
from bot.utils.cache import Cache
from bot.utils.logger import LOGGER

logger = LOGGER("INDEX")
lock = asyncio.Lock()
_REGEX = r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"


@Bot.on_message(filters.command("index") & filters.user(Config.ADMINS))
async def clone_send_for_index_command(bot: Bot, message: types.Message):
    if len(message.command) != 2:
        return await message.reply("Invalid command format. Usage: `/index [channel_link] [last_message_id]`")
    channel_link = message.command[1]

    regex = re.compile(_REGEX)
    match = regex.match(channel_link)

    if not match:
        return await message.reply("Invalid channel link format")

    chat_id = match.group(4)
    if chat_id.isnumeric():
        chat_id = int("-100" + chat_id)

    try:
        await bot.get_chat(chat_id)
    except tg_exceptions.ChannelInvalid:
        return await message.reply("This may be a private channel/group. Make me an admin over there to index the files.")
    except (tg_exceptions.UsernameInvalid, tg_exceptions.UsernameNotModified):
        return await message.reply("Invalid Link specified.")
    except Exception as e:
        logger.exception(e)
        return await message.reply(f"Errors - {e}")

    if len(match.groups()) >= 5:
        last_msg_id = int(match.group(5))
        try:
            k = await bot.get_messages(chat_id, last_msg_id)
        except tg_exceptions.Unauthorized:
            return await message.reply("Make sure that I am an admin in the channel, if the channel is private.")
        except Exception as e:
            return await message.reply(f"Error occurred - {e}")

        if k is None:
            return await message.reply("This may be a group, and I am not an admin of the group.")

        if message.from_user.id in Config.ADMINS:
            buttons = [
                [
                    InlineKeyboardButton(
                        "MOVIE DB",
                        callback_data=f"clone_index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}",
                    )
                ],
                [
                    InlineKeyboardButton("Close", callback_data="close_data"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            return await message.reply(
                f"Do you want to index this channel/group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>",
                reply_markup=reply_markup,
            )
    else:
        return await message.reply("Invalid command format. Usage: `/index [channel_link] [last_message_id]`")



@Bot.on_message(filters.command("index_gp") & filters.user(Config.ADMINS))
async def clone_send_for_index_command_gp(bot: Bot, message: types.Message):
    if len(message.command) != 3:
        return await message.reply("Invalid command format. Usage: `/index [channel_link] [last_message_id]`")
    
    channel_link = message.command[1]
    last_message_id = message.command[2]
    
    regex = re.compile(_REGEX)
    match = regex.match(channel_link)
    
    if not match:
        return await message.reply("Invalid channel link format")
    
    chat_id = match.group(4)
    if chat_id.isnumeric():
        chat_id = int("-100" + chat_id)
    
    try:
        chat = await bot.get_chat(chat_id)
        if not chat.type == "group":
            return await message.reply("This command is only applicable to groups.")
    except ChannelInvalid:
        return await message.reply("This may be a private channel/group. Make me an admin over there to index the files.")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("Invalid Link specified.")
    except Exception as e:
        logger.exception(e)
        return await message.reply(f"Error - {e}")
    
    if len(match.groups()) >= 5:
        try:
            last_msg_id = int(last_message_id)
            await bot.get_messages(chat_id, last_msg_id)
        except (ChannelInvalid, UsernameInvalid):
            return await message.reply("Make sure that I am an admin in the channel, if the channel is private.")
        except Exception as e:
            return await message.reply(f"Error occurred - {e}")
        
        buttons = [
            [
                InlineKeyboardButton(
                    "MOVIE DB",
                    callback_data=f"clone_index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}",
                )
            ],
            [
                InlineKeyboardButton("Close", callback_data="close_data"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f"Do you want to index this group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>",
            reply_markup=reply_markup,
        )
    else:
        return await message.reply("Invalid command format. Usage: `/index [channel_link] [last_message_id]`")

@Bot.on_message(((filters.forwarded & ~filters.text) | (filters.regex(_REGEX)) & filters.text) & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def clone_send_for_index(bot: Bot, message: types.Message):
    if message.text:
        regex = re.compile(_REGEX)
        match = regex.match(message.text)
        if not match:
            return await message.reply("Invalid link")
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply("This may be a private channel/group. Make me an admin over there to index the files.")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("Invalid Link specified.")
    except Exception as e:
        logger.exception(e)
        return await message.reply(f"Error - {e}")
    
    try:
        await bot.get_messages(chat_id, last_msg_id)
    except (ChannelInvalid, UsernameInvalid):
        return await message.reply("Make sure that I am an admin in the channel, if the channel is private.")
    except Exception as e:
        return await message.reply(f"Error occurred - {e}")
    
    buttons = [
        [
            InlineKeyboardButton(
                "MOVIE DB",
                callback_data=f"clone_index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}",
            )
        ],
        [
            InlineKeyboardButton("close", callback_data="close_data"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    return await message.reply(
        f"Do you want to index this channel/group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>",
        reply_markup=reply_markup,
    )


@Bot.on_callback_query(filters.regex(r"^clone_index"))  # type: ignore
async def clone_index_files(bot: Bot, query: types.CallbackQuery):
    if query.data.startswith("index_cancel"):  # type: ignore
        Cache.CANCEL = True  # type: ignore
        return await query.answer("Cancelling Indexing")
    _, sts, chat, lst_msg_id, from_user = query.data.split("#")  # type: ignore
    if sts == "reject":
        await query.message.delete()
        await bot.send_message(
            int(from_user),
            f"Your Submission for indexing {chat} has been declined by our moderators.",
            reply_to_message_id=int(lst_msg_id),
        )
        return

    if lock.locked():
        return await query.answer("Wait until the previous process completes.", show_alert=True)
    msg = query.message

    await query.answer("Processing...⏳", show_alert=True)

    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
        ),
    )
    try:
        chat = int(chat)
    except ValueError:
        chat = chat
    await clone_index_files_to_db(int(lst_msg_id), chat, msg, bot)  # type: ignore


async def iter_messages(
    client: Client,
    chat_id: Union[int, str],
    limit: int,
    offset: int = 0,
) -> Optional[AsyncGenerator["types.Message", None]]:
    """Iterate through a chat sequentially.
    This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
    you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
    single call.
    Parameters:
        client (:obj:`~pyrogram.Client`): The Pyrogram client instance.
        chat_id (``int`` | ``str``):
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages) you can simply use "me" or "self".
            For a contact that exists in your Telegram address book, you can use his phone number (str).

        limit (``int``):
            Identifier of the last message to be returned.

        offset (``int``, *optional*):
            Identifier of the first message to be returned.
            Defaults to 0.
    Returns:
        ``AsyncGenerator``: An asynchronous generator yielding :obj:`~pyrogram.types.Message` objects.
    Example:
        .. code-block:: python
            async for message in iter_messages(app, "pyrogram", 1, 15000):
                print(message.text)
    """
    current = offset

    while True:
        new_diff = min(200, limit - current)
        if new_diff <= 0:
            return
        messages = await client.get_messages(
            chat_id, list(range(current, current + new_diff + 1))
        )
        for message in messages:
            yield message
            current += 1
        await asyncio.sleep(10)


@Bot.on_message(((filters.forwarded & ~filters.text) | (filters.regex(_REGEX)) & filters.text) & filters.private & filters.incoming & filters.user(Config.ADMINS))  # type: ignore
async def clone_send_for_index_channel(bot: Bot, message: types.Message):
    if message.text:
        regex = re.compile(_REGEX)
        match = regex.match(message.text)
        if not match:
            return await message.reply("Invalid link")
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    elif message.forward_from_chat.type == types.enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply(
            "This may be a private channel/group. Make me an admin over there to index the files."
        )
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("Invalid Link specified.")
    except Exception as e:
        logger.exception(e)
        return await message.reply(f"Errors - {e}")
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply(
            "Make sure that I am an admin in the channel, if the channel is private."
        )
    if k.empty:  # type: ignore
        return await message.reply("This may be a group, and I am not an admin of the group.")

    if message.from_user.id in Config.ADMINS:
        buttons = [
            [
                InlineKeyboardButton(
                    "MOVIE DB",
                    callback_data=f"clone_index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}",
                )
            ],
            [
                InlineKeyboardButton("Close", callback_data="close_data"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f"Do you want to index this channel/group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>",
            reply_markup=reply_markup,
        )


@Bot.on_message(filters.command("setskip") & filters.user(Config.ADMINS))  # type: ignore
async def clone_set_skip_number(bot: Bot, message: types.Message):
    if " " in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except ValueError:
            return await message.reply("Skip number should be an integer.")
        await message.reply(f"Successfully set SKIP number as {skip}")
        Cache.CURRENT = int(skip)  # type: ignore
    else:
        await message.reply("Give me a skip number")


async def clone_index_files_to_db(lst_msg_id: int, chat: int, msg: types.Message, bot: Bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    async with lock:
        try:
            current = Cache.CURRENT
            Cache.CANCEL = False
            async for message in iter_messages(bot, chat, lst_msg_id, Cache.CURRENT):
                if Cache.CANCEL:
                    inserted, errored = await a_filter.insert_pending()
                    if inserted:
                        total_files += inserted
                    if errored:
                        duplicate += errored
                    await msg.edit(
                        f"Successfully Cancelled!!\n\nSaved <code>{total_files} / {current}</code> files to database!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}`)\nErrors Occurred: <code>{errors}</code>"
                    )
                    break
                current += 1
                if current % 200 == 0:
                    can = [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
                    reply = InlineKeyboardMarkup(can)
                    await msg.edit_text(
                        text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}`)\nErrors Occurred: <code>{errors}</code>",
                        reply_markup=reply,
                    )
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [
                    enums.MessageMediaType.VIDEO,
                    enums.MessageMediaType.AUDIO,
                    enums.MessageMediaType.DOCUMENT,
                    enums.MessageMediaType.PHOTO
                ]:

                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                if media.file_type == "photo":
                    media.file_name = message.caption.split('\n')[0] if message.caption else ""
                    media.mime_type = "image/jpg"
                elif media.file_type == "document" and message.document is not None:
                    media.file_name = message.document.file_name if message.document.file_name else ""
                    media.mime_type = message.document.mime_type if message.document.mime_type else ""
                media.caption = message.caption if message.caption else ""
                media.caption = message.caption
                media.chat_id = message.chat.id
                media.channel_name = message.chat.username or message.chat.title
                media.message_id = message.id
                inserted, errored = await a_filter.insert_many(media)
                if inserted:
                    total_files += inserted
                if errored:
                    duplicate += errored

        except Exception as e:
            logger.exception(e)
            await msg.edit(f"Error: {e}")
        else:
            inserted, errored = await a_filter.insert_pending()
            if inserted:
                total_files += inserted
            if errored:
                duplicate += errored
            await msg.edit(
                f"Successfully saved <code>{total_files} / {current}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>"
            )
