import math
import re
import random
from bot import Bot
from pyrogram import errors, filters, types
import re, asyncio, time, shutil, psutil, os, sys
from pyrogram import errors, filters, types, enums
import time

from ..config import Config
from ..database import a_filter, usersDB, b_filter, c_filter, d_filter
from ..utils.botTools import (
    check_fsub,
    format_buttons,
    format_buttons2,
    get_size,
    unpack_new_file_id,
    FORCE_TEXT,
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
                        "🔖 Join Our Group to Use Me",
                        url="https://t.me/+X7DNvf9iCy5jOGJl",
                    )
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
                        "🔖 Join Our Group to Use Me",
                        url="https://t.me/+X7DNvf9iCy5jOGJl",
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
        f"**Stats**\n\n**Total 1 Files**: {count1}"
        f"\n**Total 2 Files**: {count2}"
        f"\n**Total 3 Files**: {count3}"
        f"\n**Total 4 Files**: {count4}"
        f"\n\n**Total All Files**: {count}"
        f"\n\n**Total Users**: {users}"
        f"\n**Total DB Used:** {get_size(size)}"
        f"\n**Free:** `{get_size(free)}`"
        f"\n\n**Uptime:** {currentTime}"
        f"\n**CPU Usage:** {cpu_usage}%"
        f"\n**RAM Usage:** {ram_usage}%"        
        f"\n**Total Disk Space:** {total}"
        f"\n**Used Space:** {used} ({disk_usage}%)"
        f"\n**Free Space:** {free2}"
        f"\n\n**Power By** @KOPAINGLAY15",
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
        f"**Stats**\n\n**Total 1 Files**: {count1}"
        f"\n**Total 2 Files**: {count2}"
        f"\n**Total 3 Files**: {count3}"
        f"\n**Total 4 Files**: {count4}"
        f"\n\n**Total All Files**: {count}"
        f"\n\n**Total Users**: {users}"
        f"\n**Total DB Used:** {get_size(size)}"
        f"\n**Free:** `{get_size(free)}`"
        f"\n\n**Uptime:** {currentTime}"
        f"\n**CPU Usage:** {cpu_usage}%"
        f"\n**RAM Usage:** {ram_usage}%"        
        f"\n**Total Disk Space:** {total}"
        f"\n**Used Space:** {used} ({disk_usage}%)"
        f"\n**Free Space:** {free2}"
        f"\n\n**Power By** @KOPAINGLAY15",
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
        f"**Stats**\n\n**Total 1 Files**: {count1}"
        f"\n**Total 2 Files**: {count2}"
        f"\n**Total 3 Files**: {count3}"
        f"\n**Total 4 Files**: {count4}"
        f"\n\n**Total All Files**: {count}"
        f"\n\n**Total Users**: {users}"
        f"\n**Total DB Used:** {get_size(size)}"
        f"\n**Free:** `{get_size(free)}`"
        f"\n\n**Uptime:** {currentTime}"
        f"\n**CPU Usage:** {cpu_usage}%"
        f"\n**RAM Usage:** {ram_usage}%"        
        f"\n**Total Disk Space:** {total}"
        f"\n**Used Space:** {used} ({disk_usage}%)"
        f"\n**Free Space:** {free2}"
        f"\n\n**Power By** @KOPAINGLAY15",
    )
    await query.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
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
    
