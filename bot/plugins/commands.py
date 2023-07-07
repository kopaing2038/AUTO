import math
import re
import random
import json
from bot import Bot
import pyrogram
from pyrogram.errors.exceptions.bad_request_400 import MessageIdInvalid
from pyrogram import errors, filters, types
import re, asyncio, time, shutil, psutil, os, sys
from pyrogram import errors, filters, types, enums
import time
from bot.database.connections_mdb import active_connection
#from bot.database.autofilter import delete_files
from ..config import Config
from bot.database.configDb import configDB
from ..database import a_filter, usersDB, b_filter, c_filter, d_filter
from ..utils.botTools import (
    check_fsub,
    format_buttons,
    format_buttons2,
    get_size,
    unpack_new_file_id,
    FORCE_TEXT,
    save_group_settings,
    get_settings,
    humanbytes,
)
from ..utils.cache import Cache
from ..utils.imdbHelpers import get_poster
from ..utils.logger import LOGGER
from ..utils.decorators import is_banned

log = LOGGER(__name__)

BOT_START_TIME = time.time()
START_TEXT = """Hey {mention} 👋

Iam An Advanced AutoFilter Bot

I'm a group manager bot, I'm built only for CIMENA group

**@KOPAINGLAY15**
"""

HELP_TEXT = START_TEXT


@Bot.on_message(filters.command("start") & filters.incoming)  # type: ignore
@is_banned
async def start_handler(bot: Bot, msg: types.Message):
    if len(msg.command) > 1:
        _, cmd = msg.command
        if cmd.startswith("filter"):
            if not await check_fsub(bot, msg, cmd):
                return
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
                            text=f"🗓 1/{math.ceil(int(total_results) / 5)}",
                            callback_data="pages",
                        ),
                        types.InlineKeyboardButton(
                            text="NEXT ⏩", callback_data=f"ch2next_{req}_{key}_{offset}"
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
    await start_ch2handler(bot, msg)

async def start_ch2handler(bot: Bot, msg: types.Message):
    if len(msg.command) > 1:
        _, cmd = msg.command
        if cmd.startswith("ch2filter"):
            if not await check_fsub(bot, msg, cmd):
                return
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
            btn = await format_buttons2(files, settings["CHANNEL"])
            if offset != "":
                req = msg.from_user.id if msg.from_user else 0
                btn.append(
                    [
                        types.InlineKeyboardButton(
                            text=f"🗓 1/{math.ceil(int(total_results) / 5)}",
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

    await msg.reply_photo(
        photo=random.choice(Config.PICS),
        caption=START_TEXT.format(mention=msg.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [                
                [
                    types.InlineKeyboardButton(
                        "♻️ 𝕁𝕆𝕀ℕ 𝕆𝕌ℝ 𝔾ℝ𝕆𝕌ℙ 𝕋𝕆 𝕌𝕊𝔼 𝕄𝔼 ♻️",
                        url="https://t.me/+X7DNvf9iCy5jOGJl",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 GROUP 1",
                        url="https://t.me/+_1Hs8V60HGs1NzA1",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 2",
                        url="https://t.me/+z5lhEpxP5Go4MWM1",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 3",
                        url="https://t.me/MKS_RequestGroup",
                    ),
                ],
                [

                    types.InlineKeyboardButton(
                        "🔖 GROUP 4",
                        url="https://t.me/Movie_Group_MMSUB",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 5",
                        url="https://t.me/+cHMLAeatqKdlNGVl",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 6",
                        url="https://t.me/+X7DNvf9iCy5jOGJl",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 1",
                        url="https://t.me/MKSVIPLINK",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 2",
                        url="https://t.me/MKSVIPLINK2",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 3",
                        url="https://t.me/+3xS_MTfvJSEzZjY1",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 4",
                        url="https://t.me/MKSMAINCHANNEL",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 5",
                        url="https://t.me/MKSMAINCHANNEL2",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 6",
                        url="https://t.me/kpmovielist",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 7",
                        url="https://t.me/+6lHs-byrjxczY2U1",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 8",
                        url="https://t.me/ONGOING_MKS",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 9",
                        url="https://t.me/Movie_Zone_KP",
                    ),
                ]               
            ]

        ),
        quote=True,  
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
                        "♻️ 𝕁𝕆𝕀ℕ 𝕆𝕌ℝ 𝔾ℝ𝕆𝕌ℙ 𝕋𝕆 𝕌𝕊𝔼 𝕄𝔼 ♻️",
                        url="https://t.me/+X7DNvf9iCy5jOGJl",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 GROUP 1",
                        url="https://t.me/+_1Hs8V60HGs1NzA1",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 2",
                        url="https://t.me/+z5lhEpxP5Go4MWM1",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 3",
                        url="https://t.me/MKS_RequestGroup",
                    ),
                ],
                [

                    types.InlineKeyboardButton(
                        "🔖 GROUP 4",
                        url="https://t.me/Movie_Group_MMSUB",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 5",
                        url="https://t.me/+cHMLAeatqKdlNGVl",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 GROUP 6",
                        url="https://t.me/+X7DNvf9iCy5jOGJl",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 1",
                        url="https://t.me/MKSVIPLINK",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 2",
                        url="https://t.me/MKSVIPLINK2",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 3",
                        url="https://t.me/+3xS_MTfvJSEzZjY1",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 4",
                        url="https://t.me/MKSMAINCHANNEL",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 5",
                        url="https://t.me/MKSMAINCHANNEL2",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 6",
                        url="https://t.me/kpmovielist",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 7",
                        url="https://t.me/+6lHs-byrjxczY2U1",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 8",
                        url="https://t.me/ONGOING_MKS",
                    ),
                    types.InlineKeyboardButton(
                        "🔖 CHANNEL 9",
                        url="https://t.me/Movie_Zone_KP",
                    ),
                ]  
            ]
        ),
        disable_web_page_preview=True,
    )


@Bot.on_message(filters.command("help") & filters.incoming)  # type: ignore
async def help_handler(bot: Bot, msg: types.Message):
    await msg.reply(HELP_TEXT)


@Bot.on_message(filters.command("stats"))  # type: ignore
async def get_stats_at(_, msg: types.Message):
    count1 = await a_filter.col.count_documents({})  # type: ignore
    count2 = await b_filter.col.count_documents({})  # type: ignore
    count3 = await c_filter.col.count_documents({})  # type: ignore
    count4 = await d_filter.col.count_documents({})  # type: ignore
    count = count1 + count2 + count3 + count4  # type: ignore
    size = (await a_filter.db.command("dbstats"))["dataSize"]  # type: ignore
    users = await usersDB.total_users_count()
    free = 536870912 - size

    currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - BOT_START_TIME))
    total, used, free2 = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free2 = humanbytes(free2)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    buttons = [[types.InlineKeyboardButton('𝚁𝙴𝙵𝚁𝙴𝚂𝙷 ♻️', callback_data='rfrsh')]]
    await msg.reply(
        f"**Stats**\n\nTotal 1 Files: {count1}"
        f"\nTotal 2 Files: {count2}"
        f"\nTotal 3 Files: {count3}"
        f"\nTotal 4 Files: {count4}"
        f"\n\nTotal All Files: {count}"
        f"\n\nTotal Users: {users}"
        f"\nTotal DB Used: {get_size(size)}"
        f"\nFree: {get_size(free)}"
        f"\n\nUptime: {currentTime}"
        f"\nCPU Usage: {cpu_usage}%"
        f"\nRAM Usage: {ram_usage}%"        
        f"\nTotal Disk Space: {total}"
        f"\nUsed Space: {used} ({disk_usage}%)"
        f"\nFree Space: {free2}"
        f"\n\nPower By @KOPAINGLAY15",
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML    
    )

@Bot.on_message(filters.command("status"))  # type: ignore
async def get_stats(_, msg: types.Message):
    count1 = await a_filter.col.count_documents({})  # type: ignore
    count2 = await b_filter.col.count_documents({})  # type: ignore
    count3 = await c_filter.col.count_documents({})  # type: ignore
    count4 = await d_filter.col.count_documents({})  # type: ignore
    count = count1 + count2 + count3 + count4  # type: ignore
    size = (await a_filter.db.command("dbstats"))["dataSize"]  # type: ignore
    users = await usersDB.total_users_count()
    free = 536870912 - size

    currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - BOT_START_TIME))
    total, used, free2 = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free2 = humanbytes(free2)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    buttons = [[types.InlineKeyboardButton('𝚁𝙴𝙵𝚁𝙴𝚂𝙷 ♻️', callback_data='rfrsh')]]
    await msg.reply(
        f"**Stats**\n\nTotal 1 Files: {count1}"
        f"\nTotal 2 Files: {count2}"
        f"\nTotal 3 Files: {count3}"
        f"\nTotal 4 Files: {count4}"
        f"\n\nTotal All Files: {count}"
        f"\n\nTotal Users: {users}"
        f"\nTotal DB Used: {get_size(size)}"
        f"\nFree: {get_size(free)}"
        f"\n\nUptime: {currentTime}"
        f"\nCPU Usage: {cpu_usage}%"
        f"\nRAM Usage: {ram_usage}%"        
        f"\nTotal Disk Space: {total}"
        f"\nUsed Space: {used} ({disk_usage}%)"
        f"\nFree Space: {free2}"
        f"\n\nPower By @KOPAINGLAY15",
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML    
    )

@Bot.on_callback_query(filters.regex("rfrsh"))  # type: ignore
async def ref_get_stats(bot: Bot, query: types.CallbackQuery): 
    count1 = await a_filter.col.count_documents({})  # type: ignore
    count2 = await b_filter.col.count_documents({})  # type: ignore
    count3 = await c_filter.col.count_documents({})  # type: ignore
    count4 = await d_filter.col.count_documents({})  # type: ignore
    count = count1 + count2 + count3 + count4  # type: ignore
    size = (await a_filter.db.command("dbstats"))["dataSize"]  # type: ignore
    users = await usersDB.total_users_count()
    free = 536870912 - size

    currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - BOT_START_TIME))
    total, used, free2 = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free2 = humanbytes(free2)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    buttons = [[types.InlineKeyboardButton('𝚁𝙴𝙵𝚁𝙴𝚂𝙷 ♻️', callback_data='rfrsh')]]
    text = (
        f"**Stats**\n\nTotal 1 Files: {count1}"
        f"\nTotal 2 Files: {count2}"
        f"\nTotal 3 Files: {count3}"
        f"\nTotal 4 Files: {count4}"
        f"\n\nTotal All Files: {count}"
        f"\n\nTotal Users: {users}"
        f"\nTotal DB Used: {get_size(size)}"
        f"\nFree: {get_size(free)}"
        f"\n\nUptime: {currentTime}"
        f"\nCPU Usage: {cpu_usage}%"
        f"\nRAM Usage: {ram_usage}%"        
        f"\nTotal Disk Space: {total}"
        f"\nUsed Space: {used} ({disk_usage}%)"
        f"\nFree Space: {free2}"
        f"\n\nPower By @KOPAINGLAY15"
    )
    await query.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    ) 

@Bot.on_message(filters.command("restart") & filters.user(Config.ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(message.chat.id, text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**")
    await asyncio.sleep(3)
    await msg.edit_text("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")

    python = sys.executable
    os.execl(python, python, "-m", "bot")




@Bot.on_message(filters.command("delete1") & filters.user(Config.ADMINS))  # type: ignore
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

@Bot.on_message(filters.command("delete2") & filters.user(Config.ADMINS))  # type: ignore
async def handleDelete2(bot: Bot, msg: types.Message):
    """Delete file from database"""
    reply = msg.reply_to_message
    if reply and reply.media:
        msg = await msg.reply("2 Processing...⏳", quote=True)
    else:
        await msg.reply(
            "2 Reply to file with /delete which you want to delete", quote=True
        )
        return

    for file_type in ("document", "video", "audio", "photo"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit("2 This is not supported file format")
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await c_filter.col.delete_one(
        {
            "_id": file_id,
        }
    )  # type: ignore
    if file_type == "photo":
        result = await b_filter.col.delete_one(
            {
                "file_ref": media.file_id,
            }
        )  # type: ignore
    if result.deleted_count:
        await msg.edit("2 File is successfully deleted from database")
    else:
        if file_type != "photo":
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
            result = await b_filter.col.delete_many(
                {
                    "file_name": file_name,
                    "file_size": media.file_size,
                    "mime_type": media.mime_type,
                }
            )  # type: ignore
            if result.deleted_count:
                return await msg.edit("2 File is successfully deleted from database")

        await msg.edit("2 File not found in database")

@Bot.on_message(filters.command("delete3") & filters.user(Config.ADMINS))  # type: ignore
async def handleDelete3(bot: Bot, msg: types.Message):
    """Delete file from database"""
    reply = msg.reply_to_message
    if reply and reply.media:
        msg = await msg.reply("3 Processing...⏳", quote=True)
    else:
        await msg.reply(
            "3 Reply to file with /delete which you want to delete", quote=True
        )
        return

    for file_type in ("document", "video", "audio", "photo"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit("3 This is not supported file format")
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await c_filter.col.delete_one(
        {
            "_id": file_id,
        }
    )  # type: ignore
    if file_type == "photo":
        result = await c_filter.col.delete_one(
            {
                "file_ref": media.file_id,
            }
        )  # type: ignore
    if result.deleted_count:
        await msg.edit("3 File is successfully deleted from database")
    else:
        if file_type != "photo":
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
            result = await c_filter.col.delete_many(
                {
                    "file_name": file_name,
                    "file_size": media.file_size,
                    "mime_type": media.mime_type,
                }
            )  # type: ignore
            if result.deleted_count:
                return await msg.edit("3 File is successfully deleted from database")

        await msg.edit("3 File not found in database")

@Bot.on_message(filters.command("delete4") & filters.user(Config.ADMINS))  # type: ignore
async def handleDelete4(bot: Bot, msg: types.Message):
    """4 Delete file from database"""
    reply = msg.reply_to_message
    if reply and reply.media:
        msg = await msg.reply("4 Processing...⏳", quote=True)
    else:
        await msg.reply(
            " 4 Reply to file with /delete which you want to delete", quote=True
        )
        return

    for file_type in ("document", "video", "audio", "photo"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit("4 This is not supported file format")
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await d_filter.col.delete_one(
        {
            "_id": file_id,
        }
    )  # type: ignore
    if file_type == "photo":
        result = await d_filter.col.delete_one(
            {
                "file_ref": media.file_id,
            }
        )  # type: ignore
    if result.deleted_count:
        await msg.edit(" 4 File is successfully deleted from database")
    else:
        if file_type != "photo":
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
            result = await d_filter.col.delete_many(
                {
                    "file_name": file_name,
                    "file_size": media.file_size,
                    "mime_type": media.mime_type,
                }
            )  # type: ignore
            if result.deleted_count:
                return await msg.edit(" 4 File is successfully deleted from database")

        await msg.edit("4 File not found in database")

@Bot.on_message(filters.command('del') & filters.user(Config.ADMINS))
async def deleteindex(bot, message):
    _, chat_id = message.text.split(" ", 1)

    result = await b_filter.delete_many({'chat_id': chat_id})

    if result.deleted_count:
        await message.reply_text(f"Successfully deleted {result.deleted_count} documents with chat_id {chat_id} from the database.")
    else:
        await message.reply_text(f"No documents found with chat_id {chat_id} in the database.")




    
@Bot.on_message(filters.command('delete') & filters.user(Config.ADMINS))
async def delete(bot, message):
    msg = await message.reply_text('Fetching...')
    btn = [[
        types.InlineKeyboardButton(f"A Filter", callback_data="deletev1"),
        types.InlineKeyboardButton(f"B Filter", callback_data="deletev2"),
    ],[
        types.InlineKeyboardButton("CLOSE", callback_data="close_data")
    ]]
    await msg.edit('Choose do you want to delete file Database?', reply_markup=types.InlineKeyboardMarkup(btn))
    
@Bot.on_callback_query(filters.regex(r'^close_data'))
async def close_data_delete(bot, query):
    await query.message.delete()

@Bot.on_callback_query(filters.regex(r'^deletev1'))
async def deletefilev1(bot, query):
    msg = await query.message.edit_text('Fetching...')
    filters_db = a_filter
    
    srt = await filters_db.count_documents({'mime_type': 'application/x-subrip'})
    avi = await filters_db.count_documents({'mime_type': 'video/x-msvideo'})
    zip = await filters_db.count_documents({'mime_type': 'application/zip'})
    rar = await filters_db.count_documents({'mime_type': 'application/x-rar-compressed'})
    mkv = await filters_db.count_documents({'mime_type': 'video/x-matroska'})
    jpg = await filters_db.count_documents({'mime_type': 'image/jpg'})
    mp4 = await filters_db.count_documents({'mime_type': 'video/mp4'})
    
    btn = [
        [
            types.InlineKeyboardButton(f"SRT ({srt})", callback_data="srt_delete"),
            types.InlineKeyboardButton(f"AVI ({avi})", callback_data="avi_delete"),
            types.InlineKeyboardButton(f"MKV ({mkv})", callback_data="mkv_delete"),
        ],
        [
            types.InlineKeyboardButton(f"ZIP ({zip})", callback_data="zip_delete"),
            types.InlineKeyboardButton(f"RAR ({rar})", callback_data="rar_delete"),
            types.InlineKeyboardButton(f"MP4 ({mp4})", callback_data="mp4_delete")
        ],
        [
            types.InlineKeyboardButton(f"JPG ({jpg})", callback_data="jpg_delete"),
            types.InlineKeyboardButton("CLOSE", callback_data="close_datav1")
        ]
    ]
    
    await msg.edit('Choose the file type you want to delete:', reply_markup=types.InlineKeyboardMarkup(btn))


@Bot.on_callback_query(filters.regex(r'^srt_delete'))
async def srt_delete(bot, query):
    if query.data == "srt_delete":
        await query.message.edit_text("Deleting...")
        
        filters_db = a_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'application/x-subrip'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted SRT files")
        else:
            await query.message.edit_text("No SRT files to delete")


@Bot.on_callback_query(filters.regex(r'^avi_delete'))
async def avi_delete(bot, query):
    if query.data == "avi_delete":
        await query.message.edit_text("Deleting...")
        
        filters_db = a_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'video/x-msvideo'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted AVI files")
        else:
            await query.message.edit_text("No AVI files to delete")

@Bot.on_callback_query(filters.regex(r'^rar_delete'))
async def rar_delete(bot, query):
    if query.data == "rar_delete":
        await query.message.edit_text("Deleting...")
        
        filters_db = a_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'application/x-rar-compressed'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted RAR files")
        else:
            await query.message.edit_text("No RAR files to delete")


@Bot.on_callback_query(filters.regex(r'^zip_delete'))
async def zip_delete(bot, query):
    if query.data == "zip_delete":
        await query.message.edit_text("Deleting...")
        
        filters_db = a_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'application/zip'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted ZIP files")
        else:
            await query.message.edit_text("No ZIP files to delete")


@Bot.on_callback_query(filters.regex(r'^mkv_delete'))
async def mkv_delete(bot, query):
    if query.data == "mkv_delete":
        await query.message.edit_text("Deleting...")
        
        filters_db = a_filter # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'video/x-matroska'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted MKV files")
        else:
            await query.message.edit_text("No MKV files to delete")


@Bot.on_callback_query(filters.regex(r'^jpg_delete'))
async def jpg_delete(bot, query):
    if query.data == "jpg_delete":
        await query.message.edit_text("Deleting...")
        
        filters_db = a_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'image/jpg'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted JPG files")
        else:
            await query.message.edit_text("No JPG files to delete")


@Bot.on_callback_query(filters.regex(r'^mp4_delete'))
async def mp4_delete(bot, query):
    if query.data == "mp4_delete":
        await query.message.edit_text("Deleting...")

        filters_db = a_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'video/mp4'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted MP4 files")
        else:
            await query.message.edit_text("No MP4 files to delete")


@Bot.on_callback_query(filters.regex(r'^close_datav1'))
async def close_data_deletev1(bot, query):
    await query.message.delete()

@Bot.on_callback_query(filters.regex(r'^deletev2'))
async def deletefilev2(bot, query):
    msg = await query.message.edit_text('Fetching...')
    filters_db = b_filter
    
    srt = await filters_db.count_documents({'mime_type': 'application/x-subrip'})
    avi = await filters_db.count_documents({'mime_type': 'video/x-msvideo'})
    zip = await filters_db.count_documents({'mime_type': 'application/zip'})
    rar = await filters_db.count_documents({'mime_type': 'application/x-rar-compressed'})
    mkv = await filters_db.count_documents({'mime_type': 'video/x-matroska'})
    jpg = await filters_db.count_documents({'mime_type': 'image/jpg'})
    mp4 = await filters_db.count_documents({'mime_type': 'video/mp4'})

    chat_id_list = await filters_db.get_distinct_chat_ids()
    chat = len(chat_id_list)

    cht = await filters_db.count_documents({'chat_id': {'$in': chat_id_list}})

    chat_id_text = "\n".join([f"chat_id {cid}" for cid in chat_id_list])
    
    btn = [
        [
            types.InlineKeyboardButton(f"SRT ({srt})", callback_data="srt_deletev2"),
            types.InlineKeyboardButton(f"AVI ({avi})", callback_data="avi_deletev2"),
            types.InlineKeyboardButton(f"MKV ({mkv})", callback_data="mkv_deletev2"),
        ],
        [
            types.InlineKeyboardButton(f"ZIP ({zip})", callback_data="zip_deletev2"),
            types.InlineKeyboardButton(f"RAR ({rar})", callback_data="rar_deletev2"),
            types.InlineKeyboardButton(f"MP4 ({mp4})", callback_data="mp4_deletev2")
        ],
        [
            types.InlineKeyboardButton(f"JPG ({jpg})", callback_data="jpg_deletev2"), 
            types.InlineKeyboardButton(f"CH ({chat}) ({cht})", callback_data="chatlistv2"),                     
        ],
        [                  
            types.InlineKeyboardButton("CLOSE", callback_data="close_datav2")
        ]
    ]
    
    await msg.edit(f'Choose the file type you want to delete', reply_markup=types.InlineKeyboardMarkup(btn))


@Bot.on_callback_query(filters.regex(r'^chatlistv2'))
async def chat_listv2(bot, query):
    K = 1
    if query.data == "chatlistv2":        
        await query.message.edit_text("Fetching chat IDs...")
        
        filters_db = b_filter
        chat_id_list = await filters_db.get_distinct_chat_ids()
        
        # Convert Int64 values to regular integers
        chat_id_list = [int(cid) for cid in chat_id_list]
        
        cht = await filters_db.count_documents({'chat_id': {'$in': chat_id_list}})
        btn = [
            [types.InlineKeyboardButton(f"{cid} ", callback_data=f"delete_chat_id {cid}")]
            for cid in chat_id_list
        ]

        btn.append([types.InlineKeyboardButton("CLOSE", callback_data="close_chatlistv2")])
        
        chat_id_text = "\n".join([f"{K}. {cid}" for K, cid in enumerate(chat_id_list, start=K)])
        
        K += len(chat_id_list)  
        
        await query.message.edit_text(f"{cht} Chat Id list:\n\n{chat_id_text}", reply_markup=types.InlineKeyboardMarkup(btn))


@Bot.on_callback_query(filters.regex(r'^delete_chat_id'))
async def delete_chat_id(bot, query):
    if query.data.startswith("delete_chat_id"):
        channel_id = query.data.split()[1]
        await query.message.edit_text(f"Deleting chat_id {channel_id}...")
        
        filters_db = b_filter
        #result = await filters_db.delete_one(channel_id)

        result = await filters_db.col.delete_many(
            {
                "chat_id": channel_id,
            }
        ) 
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted {result.deleted_count} files for chat_id {channel_id}")
        else:
            await query.message.edit_text(f"No files found for{result.deleted_count} chat_id {channel_id} to delete")



@Bot.on_callback_query(filters.regex(r'^srt_deletev2'))
async def srt_deletev2(bot, query):
    if query.data == "srt_deletev2":
        await query.message.edit_text("Deleting...")
        
        filters_db = b_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'application/x-subrip'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted SRT files")
        else:
            await query.message.edit_text("No SRT files to delete")


@Bot.on_callback_query(filters.regex(r'^avi_deletev2'))
async def avi_deletev2(bot, query):
    if query.data == "avi_deletev2":
        await query.message.edit_text("Deleting...")
        
        filters_db = b_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'video/x-msvideo'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted AVI files")
        else:
            await query.message.edit_text("No AVI files to delete")

@Bot.on_callback_query(filters.regex(r'^rar_deletev2'))
async def rar_deletev2(bot, query):
    if query.data == "rar_deletev2":
        await query.message.edit_text("Deleting...")
        
        filters_db = b_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'application/x-rar-compressed'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted RAR files")
        else:
            await query.message.edit_text("No RAR files to delete")


@Bot.on_callback_query(filters.regex(r'^zip_deletev2'))
async def zip_deletev2(bot, query):
    if query.data == "zip_deletev2":
        await query.message.edit_text("Deleting...")
        
        filters_db = b_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'application/zip'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted ZIP files")
        else:
            await query.message.edit_text("No ZIP files to delete")


@Bot.on_callback_query(filters.regex(r'^mkv_deletev2'))
async def mkv_deletev2(bot, query):
    if query.data == "mkv_deletev2":
        await query.message.edit_text("Deleting...")
        
        filters_db = b_filter # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'video/x-matroska'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted MKV files")
        else:
            await query.message.edit_text("No MKV files to delete")


@Bot.on_callback_query(filters.regex(r'^jpg_deletev2'))
async def jpg_deletev2(bot, query):
    if query.data == "jpg_deletev2":
        await query.message.edit_text("Deleting...")
        
        filters_db = b_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'image/jpg'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted JPG files")
        else:
            await query.message.edit_text("No JPG files to delete")


@Bot.on_callback_query(filters.regex(r'^mp4_deletev2'))
async def mp4_deletev2(bot, query):
    if query.data == "mp4_deletev2":
        await query.message.edit_text("Deleting...")

        filters_db = b_filter  # Create an instance of the FiltersDb class
        
        result = await filters_db.col.delete_many({'mime_type': 'video/mp4'})
        if result.deleted_count:
            await query.message.edit_text(f"Successfully deleted MP4 files")
        else:
            await query.message.edit_text("No MP4 files to delete")


@Bot.on_callback_query(filters.regex(r'^close_datav2'))
async def close_data_deletev2(bot, query):
    await query.message.delete()


@Bot.on_message(filters.command('delete_file') & filters.user(Config.ADMINS))
async def delete_file(bot, message):
    try:
        query = message.text.split(" ", 1)[1]
    except IndexError:
        return await message.reply_text("Command Incomplete!")

    msg = await message.reply_text('Searching...')
    total, files = await b_filter.delete_files(query)

    if int(total) == 0:
        await message.reply_text('No files found in your query')
    else:
        btn = [
            [
                types.InlineKeyboardButton("YES", callback_data=f"deleteV3_{query}")
            ],
            [
                types.InlineKeyboardButton("CLOSE", callback_data="close_data")
            ]
        ]
        await msg.edit(f"Total {total} files found in your query {query}.\n\nDo you want to delete?", reply_markup=types.InlineKeyboardMarkup(btn))


@Bot.on_callback_query(filters.regex(r'^deleteV3_'))
async def deleteV3(bot, query):
    deleted = 0
    query_ = query.data.split("_", 1)[1]

    await query.message.edit_text('Deleting...')
    total, files = await b_filter.delete_files(query_)

    for file in files:
        await b_filter.col.delete_one({'_id': file})
        deleted += 1

    await query.message.edit_text(f'Deleted {deleted} files in your database for the query "{query_}"')
	

@Bot.on_message(filters.command('deleteall') & filters.user(Config.ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text="DB File 1 YES", callback_data="autofilter_delete1"
                    )
                ],  
                [
                    types.InlineKeyboardButton(
                        text="DB File 2 YES", callback_data="autofilter_delete2"
                    )
                ],  
                [
                    types.InlineKeyboardButton(
                        text="DB File 3 YES", callback_data="autofilter_delete3"
                    )
                ],  
                [
                    types.InlineKeyboardButton(
                        text="DB File YES", callback_data="autofilter_delete4"
                    )
                ],   
                [
                    types.InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )








@Bot.on_callback_query(filters.regex(r'^autofilter_delete1'))
async def adelete_all_index_confirm(bot, message):
    await a_filter.col.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.') 

@Bot.on_callback_query(filters.regex(r'^autofilter_delete1'))
async def adelete_all_2index_confirm(bot, message):
    await b_filter.col.drop()
    await message.answer('2 Piracy Is Crime')
    await message.message.edit('2 Succesfully Deleted All The Indexed Files.') 

@Bot.on_callback_query(filters.regex(r'^autofilter_delete3'))
async def adelete_all_3index_confirm(bot, message):
    await c_filter.col.drop()
    await message.answer('3 Piracy Is Crime')
    await message.message.edit('3 Succesfully Deleted All The Indexed Files.') 

@Bot.on_callback_query(filters.regex(r'^autofilter_delete4'))
async def adelete_all_4index_confirm(bot, message):
    await d_filter.col.drop()
    await message.answer('4 Piracy Is Crime')
    await message.message.edit('4 Succesfully Deleted All The Indexed Files.') 

#@Bot.on_message(filters.command('set_pics') & filters.user(Config.ADMINS))
async def set_pics_command(client, message):
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

#@Bot.on_message(filters.command('set_database') & filters.user(Config.ADMINS))
async def set_database_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a DATABASE_URI to set.")
        return
    
    database_uri = message.command[1]
    Config.DATABASE_URI = database_uri
    await message.reply_text("DATABASE_URI updated successfully.")


@Bot.on_message(filters.command('set_database') & filters.user(Config.ADMINS))
async def set_database_command(client, message):
    # Extract the database URI from the command arguments
    database_uri = ' '.join(message.command[1:])

    # Update the DATABASE_URI in the Config class
    Config.DATABASE_URI = database_uri

    # Save the updated value to the .env file
    with open('.env', 'a') as env_file:
        env_file.write(f"DATABASE_URL={database_uri}\n")

    # Reply to the user with a success message
    await message.reply("Database URI has been updated successfully!")


@Bot.on_message(filters.command('set_cap2') & filters.user(Config.ADMINS))
async def set_cap2_command(client, message):
    caption = message.text.split('/set_cap2', 1)[1].strip()

    if not caption:
        await message.reply_text("Please provide a caption to set for CAP2.")
        return

    Config.CAP2 = caption
    await message.reply_text("CAP2 updated successfully.")


@Bot.on_message(filters.command('set_ads') & filters.user(Config.ADMINS))
async def set_ads(bot, message: Message):
    ads = Config.ADS

    caption = "Please choose one of the following ADS:\n\n"

    keyboard = []

    for index, ad in enumerate(ads, start=1):
        caption += f"{index}. {ad['caption']}\n\n"
        keyboard.append([InlineKeyboardButton(str(index), callback_data=f"select_ad_{index}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(caption, reply_markup=reply_markup)

@Bot.on_callback_query(filters.regex(r'select_ad_(\d+)') & filters.user(Config.ADMINS))
async def select_ad_callback(bot, callback_query):
    ad_number = int(callback_query.matches[0].group(1))
    ads = Config.ADS

    if ad_number <= 0 or ad_number > len(ads):
        await callback_query.answer("Invalid selection. Please choose a valid ADS number.")
        return

    selected_ad = ads[ad_number - 1]

    # You can perform further actions with the selected AD, such as saving it to a database or using it in your bot's logic.

    await callback_query.answer(f"You selected ADS {ad_number}.")
    await callback_query.message.reply_text(selected_ad["caption"])
