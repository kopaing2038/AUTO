import math
import re

from bot import Bot
from pyrogram import errors, filters, types

from ..config import Config
from bot.clone_plugins.database.autofilter import a_filter
from ..database import b_filter, usersDB
from bot.clone_plugins.botTools import (
    check_fsub,
    format_buttons,
    get_size,
    unpack_new_file_id,
    FORCE_TEXT,
)
from ..utils.cache import Cache
from ..utils.imdbHelpers import get_poster
from ..utils.logger import LOGGER
from ..utils.decorators import is_banned

log = LOGGER(__name__)

START_TEXT = """Hey {mention} 👋
Iam An Advanced AutoFilter Bot

**@Movie_Zone_KP**
"""

HELP_TEXT = START_TEXT


@Bot.on_message(filters.command("start") & filters.incoming)  # type: ignore
@is_banned
async def start_handler(bot: Bot, msg: types.Message):
    if len(msg.command) > 1:
        _, cmd = msg.command
        if cmd.startswith("filter"):
            #if not await check_fsub(bot, msg, cmd):
               # return
            key = cmd.replace("filter", "").strip()
            keyword = Cache.BUTTONS.get(key)
            filter_data = Cache.SEARCH_DATA.get(key)
            if not (keyword and filter_data):
                return await msg.reply("Search Expired\nPlease send movie name again.")
            files, offset, total_results, imdb, g_settings = filter_data

            settings = g_settings

            if settings["PM_IMDB"] and not g_settings["IMDB"]:
                imdb = await get_poster(keyword, file=(files[0])["file_name"])

            sts = await msg.reply("Please Wait...", quote=True)
            btn = await format_buttons(files, settings["CHANNEL"])
            if offset != "":
                req = msg.from_user.id if msg.from_user else 0
                btn.append(
                    [
                        types.InlineKeyboardButton(
                            text=f"🗓 1/{math.ceil(int(total_results) / 10)}",
                            callback_data="pages",
                        ),
                        types.InlineKeyboardButton(
                            text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}"
                        ),
                    ]
                )
            else:
                btn.append(
                    [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
                )
            if imdb:
                cap = Config.TEMPLATE.format(  # type: ignore
                    query=keyword,
                    **imdb,
                    **locals(),
                )

            else:
                cap = f"Here is what i found for your query {keyword}"
            if imdb and imdb.get("poster") and settings["PM_IMDB_POSTER"]:
                try:
                    await msg.reply_photo(
                        photo=imdb.get("poster"),  # type: ignore
                        caption=cap[:1024],
                        reply_markup=types.InlineKeyboardMarkup(btn),
                        quote=True,
                    )
                except (
                    errors.MediaEmpty,
                    errors.PhotoInvalidDimensions,
                    errors.WebpageMediaEmpty,
                ):
                    pic = imdb.get("poster")
                    poster = pic.replace(".jpg", "._V1_UX360.jpg")
                    await msg.reply_photo(
                        photo=poster,
                        caption=cap[:1024],
                        reply_markup=types.InlineKeyboardMarkup(btn),
                        quote=True,
                    )
                except Exception as e:
                    log.exception(e)
                    await msg.reply_text(
                        cap, reply_markup=types.InlineKeyboardMarkup(btn), quote=True
                    )
            else:
                await msg.reply_text(
                    cap,
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                    disable_web_page_preview=True,
                )
            await sts.delete()
            return
        elif cmd.startswith("fsub"):
            invite_link = await bot.create_chat_invite_link(Config.FORCE_SUB_CHANNEL)
            btn = [
                [
                    types.InlineKeyboardButton(
                        "Join Channel", url=invite_link.invite_link
                    )
                ],
            ]

            await msg.reply(FORCE_TEXT, reply_markup=types.InlineKeyboardMarkup(btn))

    await msg.reply(
        START_TEXT.format(mention=msg.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        "🔖 Join Our Group to Use Me",
                        url="https://t.me/MKS_RequestGroup",
                    )
                ]
            ]
        ),
        disable_web_page_preview=True,
    )


@Bot.on_callback_query(filters.regex("help"))  # type: ignore
async def help_handler_query(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    await query.edit_message_text(
        HELP_TEXT,
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("◀️ Back", callback_data="back_home")]]
        ),
    )


@Bot.on_callback_query(filters.regex("back"))  # type: ignore
async def home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    await query.edit_message_text(
        START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        "🔖 Join Our Group to Use Me",
                        url="https://t.me/MKS_RequestGroup",
                    )
                ]
            ]
        ),
        disable_web_page_preview=True,
    )


@Bot.on_message(filters.command("help") & filters.incoming)  # type: ignore
async def help_handler(bot: Bot, msg: types.Message):
    await msg.reply(HELP_TEXT)


@Bot.on_message(filters.command("stats"))  # type: ignore
async def get_stats(_, msg: types.Message):
    count = await a_filter.col.count_documents({})  # type: ignore
    size = (await a_filter.db.command("dbstats"))["dataSize"]  # type: ignore
    users = await usersDB.total_users_count()
    free = 536870912 - size
    await msg.reply(
        f"**Stats**\n\n**Total Files**: `{count}`"
        f"\nTotal Users: {users}"
        f"\n**Total DB Used:** `{get_size(size)}`"
        f"\n**Free:** `{get_size(free)}`"
    )


@Bot.on_message(filters.command("delete") & filters.user(Config.ADMINS))  # type: ignore
async def handleDelete(bot: Bot, msg: types.Message):
    """Delete file from database"""
    reply = msg.reply_to_message
    if reply and reply.media:
        msg = await msg.reply("Processing...⏳", quote=True)
    else:
        await msg.reply(
            "Reply to file with /delete which you want to delete", quote=True
        )
        return

    for file_type in ("document", "video", "audio", "photo"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit("This is not supported file format")
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await a_filter.col.delete_one(
        {
            "_id": file_id,
        }
    )  # type: ignore
    if file_type == "photo":
        result = await a_filter.col.delete_one(
            {
                "file_ref": media.file_id,
            }
        )  # type: ignore
    if result.deleted_count:
        await msg.edit("File is successfully deleted from database")
    else:
        if file_type != "photo":
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
            result = await a_filter.col.delete_many(
                {
                    "file_name": file_name,
                    "file_size": media.file_size,
                    "mime_type": media.mime_type,
                }
            )  # type: ignore
            if result.deleted_count:
                return await msg.edit("File is successfully deleted from database")

        await msg.edit("File not found in database")


@Bot.on_message(filters.command('set_pics_plus') & filters.user(Config.ADMINS))
async def set_pics_plus_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a URL to add.")
        return
    
    pic_urls = []
    for arg in message.command[1:]:
        if isinstance(arg, str):
            pic_urls.append(arg)
    
    Config.PICS += pic_urls
    await message.reply_text("URLs added successfully.")

@Bot.on_message(filters.command('set_pics') & filters.user(Config.ADMINS))
async def set_pics_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a URL to add.")
        return
    
    pic_urls = []
    for arg in message.command[1:]:
        if isinstance(arg, str):
            pic_urls.append(arg)
    
    Config.PICS = pic_urls  # Replace the previous PICS with the newly supplied URLs
    await message.reply_text("URLs updated successfully.")

@Bot.on_message(filters.command('set_database') & filters.user(Config.ADMINS))
async def set_database_command(client, message):
    # Extract the database URI from the command arguments
    database_uri = ' '.join(message.command[1:])

    # Update the DATABASE_URI in the Config class
    Config.DATABASE_URL = database_uri

    # Save the updated value to the .env file
    with open('.env', 'a') as env_file:
        env_file.write(f"DATABASE_URL={database_uri}\n")

    # Reply to the user with a success message
    await message.reply("Database URI has been updated successfully!")

@bot.on_message(filters.command('set_dbname') & filters.user(Config.ADMINS))
async def set_dbname_command(client, message):
    # Get the input argument from the command
    if len(message.command) > 1:
        new_dbname = message.command[1]

        # Update the SESSION_NAME variable
        Config.SESSION_NAME2 = new_dbname

        # Reply to the user with the updated SESSION_NAME
        await message.reply(f"SESSION_NAME has been set to: {new_dbname}")
    else:
        # If no argument is provided, reply with an error message
        await message.reply("Please provide a new SESSION_NAME.")
