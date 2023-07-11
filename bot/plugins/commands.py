import math
import re
import random
import json
import asyncio
from bot import Bot
import pyrogram
from typing import List
from pyrogram.errors.exceptions.bad_request_400 import MessageIdInvalid
from pyrogram import errors, filters, types
import re, asyncio, time, shutil, psutil, os, sys
from pyrogram import errors, filters, types, enums
import time
from ..config import Config
from ..config import Script
from bot.database.connections_mdb import add_connection
import pymongo
from pymongo import MongoClient
from ..database import configDB as config_db
from ..database import a_filter, usersDB, b_filter, c_filter
from ..utils.botTools import (
    check_fsub,
    format_buttons,
    format_buttons2,
    get_size,
    unpack_new_file_id,
    FORCE_TEXT,
    humanbytes,
    update_config,
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

    m=await msg.reply_sticker("CAACAgIAAxkBAAEEkwJkqPLz8LokQt6Cb_rB31rMcnxHUAAC9wADVp29CgtyJB1I9A0wHgQ")
    await asyncio.sleep(1)
    await m.delete()
    await msg.reply_photo(
        photo=random.choice(Config.PICS),
        caption=Script.START_TEXT.format(mention=msg.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [                
                [
                    types.InlineKeyboardButton(
                        '🔮 sᴇʟᴇᴄᴛ ʏᴏuʀ ʟᴀɴɢ 🔮',
                        callback_data='botlang'
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "🇲🇲 MYANMAR 🇲🇲",
                        callback_data="myanmar",
                    ),
                    types.InlineKeyboardButton(
                        "🇺🇸 ENGLISH 🇺🇸",
                        callback_data="english",
                    ),
                    types.InlineKeyboardButton(
                        "🇰🇷 KOREAN 🇰🇷",
                        callback_data="korean",
                    ),
		],
                [
                    types.InlineKeyboardButton(
                        "🇹🇭 THAI 🇹🇭",
                        callback_data="thai",
                    ),
                    types.InlineKeyboardButton(
                        "🇨🇳 CHINA 🇨🇳",
                        callback_data="chinese",
                    ),
                    types.InlineKeyboardButton(
                        "🇯🇵 JAPAN 🇯🇵",
                        callback_data="japan",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        '☺️ 𝚃𝙷𝙰𝙽𝙺 𝚄 ☺️',
                        callback_data='thank'
                    )
                ],            
            ]

        ),
        quote=True,  
    )


BUTTONS_START = [
    [
        types.InlineKeyboardButton(
            "♻️ 𝕁𝕆𝕀ℕ 𝕆𝕌ℝ 𝔾ℝ𝕆𝕌ℙ 𝕋𝕆 𝕌𝕊𝔼 𝕄𝔼 ♻️",
            url="https://t.me/+X7DNvf9iCy5jOGJl",
        )
    ],
    [
        types.InlineKeyboardButton(
            "𝕁𝕠𝕚𝕟 ℂ𝕙𝕒𝕟𝕟𝕖𝕝",
            url="https://t.me/+X7DNvf9iCy5jOGJl",
        ),
        types.InlineKeyboardButton(
            "𝔹𝕆𝕋 𝔾𝕌𝕀𝔻𝔼",
            url="https://t.me/+X7DNvf9iCy5jOGJl",
        )
    ],
    [
        types.InlineKeyboardButton(
            "𝕄𝕐 ℂ𝕙𝕒𝕟𝕟𝕖𝕝",
            callback_data="allchannel",
        ),
        types.InlineKeyboardButton(
            "𝕄𝕪 𝔾𝕣𝕠𝕦𝕡",
            callback_data="allgroups",
        ),
        types.InlineKeyboardButton(
            "𝕍𝕀ℙ 𝕊𝕖𝕣𝕚𝕖𝕤 𝕃𝕚𝕤𝕥",
            callback_data="vip",
        )
    ],
    [
        types.InlineKeyboardButton(
            "𝕊𝕋𝔸𝕋𝕌𝕊",
            callback_data="status",
        ),
        types.InlineKeyboardButton(
            "𝔸𝔹𝕆𝕌𝕋",
            callback_data="about",
        ),
        types.InlineKeyboardButton(
            "𝔻𝕠𝕟𝕒𝕥𝕖",
            callback_data="donate",
        ),
    ],
    [
        types.InlineKeyboardButton(
            "ℍ𝔼𝕃ℙ",
            callback_data="help",
        ),
        types.InlineKeyboardButton(
            "𝔻𝔼𝕍𝕊",
            callback_data="DEVS",
        ),
        types.InlineKeyboardButton(
            "𝔸𝔻𝕄𝕀ℕ",
            callback_data="owner",
        ),
        types.InlineKeyboardButton(
            "𝔹𝔸ℂ𝕂 🏠",
            callback_data="back_home"
        ),
    ]
]


@Bot.on_callback_query(filters.regex("myanmar"))  # type: ignore
async def myanmar_home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.MM_START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(BUTTONS_START),
    )

@Bot.on_callback_query(filters.regex("english"))  # type: ignore
async def english_home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.ENG_START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(BUTTONS_START),
    )

@Bot.on_callback_query(filters.regex("korean"))  # type: ignore
async def korean_home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.KOREAN_START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(BUTTONS_START),
    )

@Bot.on_callback_query(filters.regex("thai"))  # type: ignore
async def thai_home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.THAI_START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(BUTTONS_START),
    )

@Bot.on_callback_query(filters.regex("chinese"))  # type: ignore
async def chinese_home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.CHN_START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(BUTTONS_START),
    )

@Bot.on_callback_query(filters.regex("japan"))  # type: ignore
async def japan_home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.JAPAN_START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(BUTTONS_START),
    )

@Bot.on_callback_query(filters.regex("botlang"))  # type: ignore
async def botlang_home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)



@Bot.on_callback_query(filters.regex("thank"))  # type: ignore
async def thank_home_handler(bot: Bot, query: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton('ᴀᴅᴅ ᴍᴇ', url='https://t.me/botechs_bot?startgroup=true'),
            types.InlineKeyboardButton(" Home", callback_data="back_home"),
	],
        [
            types.InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close_data')
        ]
    ]
    reply_markup = types.InlineKeyboardMarkup(buttons)
    await bot.edit_message_media(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        media=types.InputMediaPhoto(media=random.choice(Config.PICS))
    )
    await query.message.edit_text(
        text=Script.THANK_TXT.format(query.from_user.mention),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Bot.on_callback_query(filters.regex("DEVS"))  # type: ignore  
async def DEVS_home_handler(bot: Bot, query: types.CallbackQuery):
        buttons = [[
            types.InlineKeyboardButton("𝔹𝕠𝕥 𝕆𝕨𝕟𝕖𝕣", url=f"{Script.OWNER_LINK}"),
            types.InlineKeyboardButton('ℍ𝕆𝕄𝔼', callback_data="back")            
        ]]
        reply_markup = types.InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.DEVS_TEXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

@Bot.on_callback_query(filters.regex("help"))  # type: ignore
async def help_handler_query(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.HELP_TEXT,
        reply_markup=types.InlineKeyboardMarkup(
            [
                [types.InlineKeyboardButton('⚙️ 𝙰𝙳𝙼𝙸𝙽 𝙾𝙽𝙻𝚈 ⚙️', callback_data='adminonly')],
                [types.InlineKeyboardButton("◀️ Back", callback_data="back_home")],
            
            ]
        ),
    )

@Bot.on_callback_query(filters.regex("adminonly"))  # type: ignore
async def adminonly_handler_query(bot: Bot, query: types.CallbackQuery):   
    buttons = [
        [
            types.InlineKeyboardButton('🔙 𝙱𝙰𝙲𝙺', callback_data='help'),
            types.InlineKeyboardButton("◀️ HOME", callback_data="back") 
        ]
    ]
    reply_markup = types.InlineKeyboardMarkup(buttons)
    if query.from_user.id in Config.ADMINS:
        await query.message.edit_text(text=Script.ADMINONLY_TXT, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        await query.answer("You're not authorized. ⚠️", show_alert=True)

@Bot.on_callback_query(filters.regex("back"))  # type: ignore
async def home_handler(bot: Bot, query: types.CallbackQuery):
    await query.answer()
    media = types.InputMediaPhoto(media=random.choice(Config.PICS))
    await query.message.edit_media(media=media)
    await bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        caption=Script.START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        '🔮 sᴇʟᴇᴄᴛ ʏᴏuʀ ʟᴀɴɢ 🔮',
                        callback_data='botlang'
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        "🇲🇲 MYANMAR 🇲🇲",
                        callback_data="myanmar",
                    ),
                    types.InlineKeyboardButton(
                        "🇺🇸 ENGLISH 🇺🇸",
                        callback_data="english",
                    ),
                    types.InlineKeyboardButton(
                        "🇰🇷 KOREAN 🇰🇷",
                        callback_data="korean",
                    ),
		],
                [
                    types.InlineKeyboardButton(
                        "🇹🇭 THAI 🇹🇭",
                        callback_data="thai",
                    ),
                    types.InlineKeyboardButton(
                        "🇨🇳 CHINA 🇨🇳",
                        callback_data="chinese",
                    ),
                    types.InlineKeyboardButton(
                        "🇯🇵 JAPAN 🇯🇵",
                        callback_data="japan",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        '☺️ 𝚃𝙷𝙰𝙽𝙺 𝚄 ☺️',
                        callback_data='thank'
                    )
                ], 
            ]
        )
    )


@Bot.on_message(filters.command("help") & filters.incoming)  # type: ignore
async def help_handler(bot: Bot, msg: types.Message):
    await msg.reply(Script.HELP_TEXT)

@Bot.on_callback_query(filters.regex("vip"))  # type: ignore  
async def vip_home_handler(bot: Bot, query: types.CallbackQuery):
        buttons = [[
                    types.InlineKeyboardButton('💠 VIP English Series 💠', url=f"{Script.E_SERIES_LINK}"),
                    types.InlineKeyboardButton('💠 VIP Chinese Series💠', url=f"{Script.CHINESE_LINK}")
                ],
                [
                    types.InlineKeyboardButton('💠 VIP Thai Series💠', url=f"{Script.THAI_LINK}"),
                    types.InlineKeyboardButton('💠 VIP Bollywood Series💠', url=f"{Script.BOLLYWOOD_LINK}")
                ],
                [
                    types.InlineKeyboardButton('💠 VIP Anime Series💠', url=f"{Script.ANIME_LINK}"),
                    types.InlineKeyboardButton('💠 Korean Series💠', url=f"{Script.K_SERIES_LINK}")
                ],
                [
                    types.InlineKeyboardButton("𝕄𝕐 ℂ𝕙𝕒𝕟𝕟𝕖𝕝", callback_data="allchannel"),
                    types.InlineKeyboardButton("𝕄𝕪 𝔾𝕣𝕠𝕦𝕡", callback_data="allgroups")                               
                ],[
                    types.InlineKeyboardButton("𝐕𝐈𝐏 𝐒𝐞𝐫𝐢𝐞𝐬 𝐌𝐞𝐦𝐛𝐞𝐫ဝင်ရန်", url=f"{Script.VIP_LINK}"),
                    types.InlineKeyboardButton("◀️ 𝔹𝕃𝔸ℂ𝕂", callback_data="back") 
                ]]
        reply_markup = types.InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.VIP_TEXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

@Bot.on_callback_query(filters.regex("owner"))  # type: ignore  
async def owner_home_handler(bot: Bot, query: types.CallbackQuery):
        buttons= [[
            types.InlineKeyboardButton('❣️ FOUNDER ❣️', url=f"{Script.OWNER_LINK}"),
            types.InlineKeyboardButton("MODERATORS", url=f"{Script.M_LINK}")
            ],[
            types.InlineKeyboardButton("◀️ 𝔹𝕃𝔸ℂ𝕂", callback_data="back")
        ]]
        reply_markup =types.InlineKeyboardMarkup(buttons)        
        await query.message.edit_text(
            text=Script.OWNER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

@Bot.on_callback_query(filters.regex("allchannel"))  # type: ignore  
async def allchannel_home_handler(bot: Bot, query: types.CallbackQuery):
        buttons = [[
            types.InlineKeyboardButton("𝕄𝕪 𝔾𝕣𝕠𝕦𝕡", callback_data="allgroups"),
            types.InlineKeyboardButton("𝕊𝔼ℝ𝕀𝔼𝕊 𝕃𝕀𝕊𝕋", callback_data="vip")],[
            types.InlineKeyboardButton("◀️ 𝔹𝕃𝔸ℂ𝕂", callback_data="back")
        ]]
        reply_markup = types.InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.ALL_CHANNEL,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

@Bot.on_callback_query(filters.regex("about"))  # type: ignore  
async def about_home_handler(bot: Bot, query: types.CallbackQuery):
        buttons= [[
            types.InlineKeyboardButton('❣️ 𝚂𝙾𝚄𝚁𝙲𝙴 𝙲𝙾𝙳𝙴 ❣️', callback_data='source'),
            types.InlineKeyboardButton("ℍ𝔼𝕃ℙ", callback_data="DEVS")
            ],[
            types.InlineKeyboardButton("◀️ 𝔹𝕃𝔸ℂ𝕂", callback_data="back")
        ]]
        reply_markup =types.InlineKeyboardMarkup(buttons)        
        await query.message.edit_text(
            text=Script.ABOUT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
      
@Bot.on_callback_query(filters.regex("allgroups"))  # type: ignore  
async def allgroups_home_handler(bot: Bot, query: types.CallbackQuery):
        buttons = [[
            types.InlineKeyboardButton("𝕄𝕐 ℂ𝕙𝕒𝕟𝕟𝕖𝕝", callback_data="allchannel"),
            types.InlineKeyboardButton("𝕊𝔼ℝ𝕀𝔼𝕊 𝕃𝕀𝕊𝕋", callback_data="vip")],[
            types.InlineKeyboardButton("◀️ 𝔹𝕃𝔸ℂ𝕂", callback_data="back")
        ]]
        reply_markup = types.InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.ALL_GROUPS,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
      
@Bot.on_callback_query(filters.regex("donate"))  # type: ignore  
async def donate_home_handler(bot: Bot, query: types.CallbackQuery):
        buttons = [[
            types.InlineKeyboardButton("◀️ 𝔹𝕃𝔸ℂ𝕂", callback_data="back")         
        ]]
        reply_markup = types.InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.DONATE,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
 

@Bot.on_message(filters.command("stats"))  # type: ignore
async def get_stats_at(_, msg: types.Message):
    count1 = await a_filter.col.count_documents({})  # type: ignore
    count2 = await b_filter.col.count_documents({})  # type: ignore
    count3 = await c_filter.col.count_documents({})  # type: ignore
    count = count1 + count2 + count3   # type: ignore
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
    mg = await msg.reply("Initialising")
    await mg.edit("Initialising ✪⍟⍟⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪⍟⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪✪⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪✪✪⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪✪✪✪")
    asyncio.sleep(1)
    await mg.edit("✪Connection Successful✪")
    asyncio.sleep(1)
    await mg.delete()
    await msg.reply(
        f"**Stats**\n\nTotal 1 Files: {count1}"
        f"\nTotal 2 Files: {count2}"
        f"\nTotal 3 Files: {count3}"
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
    count = count1 + count2 + count3  # type: ignore
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
    mg = await msg.reply("Initialising")
    await mg.edit("Initialising ✪⍟⍟⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪⍟⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪✪⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪✪✪⍟")
    asyncio.sleep(1)
    await mg.edit("Initialising ✪✪✪✪✪✪")
    asyncio.sleep(1)
    await mg.edit("✪Connection Successful✪")
    asyncio.sleep(1)
    await mg.delete()
    await msg.reply(
        f"**Stats**\n\nTotal 1 Files: {count1}"
        f"\nTotal 2 Files: {count2}"
        f"\nTotal 3 Files: {count3}"
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
    count = count1 + count2 + count3 # type: ignore
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
    buttons = [[types.InlineKeyboardButton('𝚁𝙴𝙵𝚁𝙴𝚂𝙷 ♻️', callback_data='rfrsh'), types.InlineKeyboardButton('◀️ Back', callback_data='back_home')]]
    text = (
        f"**Stats**\n\nTotal 1 Files: {count1}"
        f"\nTotal 2 Files: {count2}"
        f"\nTotal 3 Files: {count3}"
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
    msg = await query.message.edit_text("Initialising")
    await msg.edit("Initialising ✪⍟⍟⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪⍟⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪✪⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪✪✪")
    asyncio.sleep(1)
    await msg.edit("✪Connection Successful✪")
    await query.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    ) 

@Bot.on_callback_query(filters.regex("status"))  # type: ignore  
async def status_home_handler(bot: Bot, query: types.CallbackQuery):        
    count1 = await a_filter.col.count_documents({})  # type: ignore
    count2 = await b_filter.col.count_documents({})  # type: ignore
    count3 = await c_filter.col.count_documents({})  # type: ignore
    count = count1 + count2 + count3 # type: ignore
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
    buttons = [[types.InlineKeyboardButton('𝚁𝙴𝙵𝚁𝙴𝚂𝙷 ♻️', callback_data='rfrsh'), types.InlineKeyboardButton('◀️ Back', callback_data='back_home')]]
    text = (
        f"**Stats**\n\nTotal 1 Files: {count1}"
        f"\nTotal 2 Files: {count2}"
        f"\nTotal 3 Files: {count3}"
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
    msg = await query.message.edit_text("Initialising")
    await msg.edit("Initialising ✪⍟⍟⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪⍟⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪✪⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪✪✪")
    asyncio.sleep(1)
    await msg.edit("✪Connection Successful✪")
    await query.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    ) 

@Bot.on_message(filters.command("restart") & filters.user(Config.ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(message.chat.id, text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**")
    await msg.edit("Initialising ✪⍟⍟⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪⍟⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪⍟⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪⍟⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪✪⍟")
    asyncio.sleep(1)
    await msg.edit("Initialising ✪✪✪✪✪✪")
    asyncio.sleep(1)
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


@Bot.on_message(filters.command('del') & filters.user(Config.ADMINS))
async def deleteindex(bot, message):
    _, chat_id = message.text.split(" ", 1)

    result = await b_filter.delete_many({'chat_id': chat_id})

    if result.deleted_count:
        await message.reply_text(f"Successfully deleted {result.deleted_count} documents with chat_id {chat_id} from the database.")
    else:
        await message.reply_text(f"No documents found with chat_id {chat_id} in the database.")


@Bot.on_message(filters.command("deletefiles") & filters.user(Config.ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, This command won't work in groups. It only works on my PM !</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, Give me a keyword along with the command to delete files.</b>")
    k = await bot.send_message(chat_id=message.chat.id, text=f"<b>Fetching Files for your query {keyword} on DB... Please wait...</b>")
    files, next_offset, total = await b_filter.get_search_results(keyword)
    await k.edit_text(f"<b>Found {total} files for your query {keyword} !\n\nFile deletion process will start in 5 seconds !</b>")
    await asyncio.sleep(5)
    deleted = 0
    for file in files:
        await k.edit_text(f"<b>Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your query {keyword} !\n\nPlease wait...</b>")
        file_ids = file.file_id
        file_name = file.file_name
        result = await b_filter.collection.delete_one({
            '_id': file_ids,
        })
        if result.deleted_count:
            logger.info(f'File Found for your query {keyword}! Successfully deleted {file_name} from database.')
        deleted += 1
    await k.edit_text(text=f"<b>Process Completed for file deletion !\n\nSuccessfully deleted {str(deleted)} files from database for your query {keyword}.</b>")


    
@Bot.on_message(filters.command('delete') & filters.user(Config.ADMINS))
async def delete(bot, message):
    msg = await message.reply_text('Fetching...')
    btn = [[
        types.InlineKeyboardButton(f"A Filter", callback_data="deletev1"),
        types.InlineKeyboardButton(f"B Filter", callback_data="deletev2"),
        types.InlineKeyboardButton(f"C Filter", callback_data="deletev3"),
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



@Bot.on_message(filters.command('set_cap2') & filters.user(Config.ADMINS))
async def set_cap2_command(client, message):
    caption = message.text.split('/set_cap2', 1)[1].strip()

    if not caption:
        await message.reply_text("Please provide a caption to set for CAP2.")
        return

    Config.CAP2 = caption
    await message.reply_text("CAP2 updated successfully.")

@Bot.on_message(filters.command('set_start') & filters.user(Config.ADMINS))
async def start_text_command(client, message):
    caption = message.text.split('/set_start', 1)[1].strip()

    if not caption:
        await message.reply_text("Please provide a caption to set for START_TEXT.")
        return

    Script.START_TEXT = caption
    await message.reply_text("START_TEXT updated successfully.")


@Bot.on_message(filters.command('set_ads') & filters.user(Config.ADMINS))
async def set_ads(bot, message):
    ads = message.text.split('\n')[1:]
    ad_list = []
    for ad in ads:
        try:
            ad_data = json.loads(ad)
            ad_list.append(ad_data)
        except json.JSONDecodeError:
            pass

    if ad_list:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        settings["ADS"] = ad_list
        await config_db.update_config(f"SETTINGS_{message.chat.id}", settings)
        await message.reply("ADS settings updated successfully!")
    else:
        await message.reply("Invalid ADS format. Please provide valid JSON-formatted ADS.")

@Bot.on_message(filters.command('set_ads_plus') & filters.user(Config.ADMINS))
async def set_ads_plus(bot, message):
    ads = message.text.split('\n')[1:]
    ad_list = []
    for ad in ads:
        try:
            ad_data = json.loads(ad)
            ad_list.append(ad_data)
        except json.JSONDecodeError:
            pass

    if ad_list:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        existing_ads = settings.get("ADS", [])
        updated_ads = existing_ads + ad_list  # Append the new ADS to the existing ADS list
        settings["ADS"] = updated_ads
        await config_db.update_config(f"SETTINGS_{message.chat.id}", settings)
        await message.reply("ADS settings updated successfully!")
    else:
        await message.reply("Invalid ADS format. Please provide valid JSON-formatted ADS.")


@Bot.on_message(filters.command('show_ads') & filters.user(Config.ADMINS))
async def show_ads(bot, message):
    chat_id = message.chat.id
    settings = await config_db.get_settings(f"SETTINGS_{chat_id}")
    ads = settings.get("ADS", [])
    
    if ads:
        ad_strings = [json.dumps(ad) for ad in ads]
        ads_text = '\n'.join(ad_strings)
        await message.reply_text(f"Ads for this group:\n{ads_text}")
    else:
        await message.reply_text("No ads found for this group.")





@Bot.on_message(filters.command('set_admins_plus') & filters.user(Config.ADMINS))
async def set_admins_plus_command(client, message):
    admins = message.command[1:]
    admin_ids = []
    if not admins:
        await message.reply("Please provide a list of admin IDs.")
        return
    for admin in admins:
        try:
            admin_id = int(admin)
            admin_ids.append(admin_id)
        except ValueError:
            # Invalid admin ID, skip it
            continue

    if admin_ids:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        existing_admins = settings.get("SUDO_USERS", [])
        updated_admins = existing_admins + admin_ids  # Append the new admin IDs to the existing list
        settings["SUDO_USERS"] = updated_admins
        await config_db.update_config(f"SETTINGS_{message.chat.id}", settings)
        await message.reply(f"Admins added {admin_ids} successfully.")
    else:
        await message.reply("No valid admin IDs were provided.")

@Bot.on_message(filters.command('remove_admins_plus') & filters.user(Config.ADMINS))
async def remove_admins_plus_command(client, message):
    admins = message.command[1:]
    admin_ids = []
    if not admins:
        await message.reply("Please provide a list of admin IDs.")
        return
    for admin in admins:
        try:
            admin_id = int(admin)
            admin_ids.append(admin_id)
        except ValueError:
            # Invalid admin ID, skip it
            continue

    if admin_ids:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        existing_admins = settings.get("SUDO_USERS", [])
        updated_admins = [admin for admin in existing_admins if admin not in admin_ids]  # Remove the specified admin IDs from the existing list
        settings["SUDO_USERS"] = updated_admins
        await config_db.update_config(f"SETTINGS_{message.chat.id}", settings)
        await message.reply(f"Admins removed {admin_ids} successfully.")
    else:
        await message.reply("No valid admin IDs were provided.")


@Bot.on_message(filters.command('show_admins_plus') & filters.user(Config.ADMINS))
async def show_admins_plus_command(client, message):
    chat_id = message.chat.id
    settings = await config_db.get_settings(f"SETTINGS_{chat_id}")
    admins = settings.get("SUDO_USERS", [])
    
    if admins:
        admin_list = '\n'.join(str(admin_id) for admin_id in admins)
        await message.reply(f"Admin IDs:\n{admin_list}")
    else:
        await message.reply("No admins found.")


@Bot.on_message(filters.command('set_template') & filters.user(Config.ADMINS))
async def set_template_command(client, message):
    template = " ".join(message.command[1:])
    if not template:
        await message.reply("""Please provide a template.🏷 𝗧𝗶𝘁𝗹𝗲 :</b>: <a href={url}>{title}</a>  <a href={url}/releaseinfo>{year}</a> - #{kind}       
🌟 𝐑𝐚𝐭𝐢𝐧𝐠    : <a href={url}/ratings>{rating}</a> / 10 ({votes} 𝐮𝐬𝐞𝐫 𝐫𝐚𝐭𝐢𝐧𝐠𝐬.)
📀 𝐑𝐮𝐧𝐓𝐢𝐦𝐞 : {runtime} Minutes
📆 𝗥𝗲𝗹𝗲𝗮𝘀𝗲  : {release_date}
🎭 𝗚𝗲𝗻𝗿𝗲𝘀   : #{genres}
👥 𝗖𝗮𝘀𝘁  : #{cast}""")
        return

    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    settings["TEMPLATE"] = template
    await config_db.update_config(f"SETTINGS_{message.chat.id}", settings)
    await message.reply(f"Template has been updated.\n\n {template}")


@Bot.on_message(filters.command('set_sub_channel') & filters.user(Config.ADMINS))
async def set_sub_channel_command(client, message):
    if len(message.command) == 2:
        try:
            sub_channel_id = int(message.command[1])
            settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
            settings["FORCE_SUB_CHANNEL"] = sub_channel_id
            await message.reply(f"FORCE_SUB_CHANNEL has been set to {sub_channel_id}")
        except ValueError:
            await message.reply("Invalid channel ID. Please provide a valid numeric ID.")
    else:
        await message.reply("Invalid command format. Usage: /set_sub_channel <channel_id>")




@Bot.on_message(filters.command('set_caption') & filters.user(Config.ADMINS))
async def set_file_caption_command(client, message):
    if len(message.command) > 1:
        new_caption = " ".join(message.command[1:])
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        settings["CUSTOM_FILE_CAPTION"] = new_caption
        await config_db.update_config(f"SETTINGS_{message.chat.id}", settings)
        await message.reply_text(f"Custom file caption has been updated.\n\n {new_caption}")
    else:
        await message.reply_text("Please provide a new caption for the files.")







