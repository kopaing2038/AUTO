import math
import re
import random
import asyncio
from bot import Bot
from pyrogram import enums, errors, filters, types
from pyrogram.errors import MessageNotModified

from ..config import Config
from ..database import a_filter
from ..database import configDB as config_db
from ..utils.botTools import check_fsub, format_buttons, get_size, parse_link
from ..utils.cache import Cache
from ..utils.imdbHelpers import get_poster, get_photo
from ..utils.logger import LOGGER

log = LOGGER(__name__)
ALRT_TXT = "test1"
ALRT_TXT2 = "test2"
OLD_ALRT_TXT = "test3"

@Bot.on_message(filters.group & filters.text & filters.incoming, group=-1)
async def auto_filter(bot: Bot, message: types.Message, text=True):
    #if not await check_fsub(bot, message):
        #return 
    a = await ch1_give_filter(bot, message)
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['CH_POST']:
        kt = await ch9_imdb(bot, message)
        

@Bot.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    data_parts = query.data.split("#")

    if len(data_parts) < 2:
        return await query.answer("Invalid data format.", show_alert=True)

    _, search, language = data_parts + [""] * (3 - len(data_parts))
    req = query.from_user.id if query.from_user else 0

    if search in [str(query.from_user.id), "0"]:
        await query.answer(f"No {search.upper()} found!", show_alert=True)
        return


    if language == "unknown":
        return await query.answer("Please select the language and video quality channel!", show_alert=True)

    if not search:
        await query.answer(OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        return 
    if language != "home":
        search = f"{search} {language}"
    if 2 < len(search) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True
        )

        if not files:
            return
    else:
        return


    key = f"{query.message.chat.id}-{query.message.id}"
    Cache.BUTTONS[key] = search
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    if settings["IMDB"]:
        imdb = await get_poster(search, file=files[0]["file_name"])
    else:
        imdb = {}
    Cache.SEARCH_DATA[key] = files, offset, total_results, imdb, settings
    btn = await format_buttons(files, settings["CHANNEL"])
    # btn = []
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    if not settings.get("DOWNLOAD_BUTTON"):
        if offset != "":
            req = query.from_user.id if query.from_user else 0
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
            btn.insert(0,
                [types.InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs  ရွေးချယ်ပေးပါ။ !", callback_data=f"lang#{search}#home")]
            )
        else:
            btn.append(
                [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
            btn.insert(0,
                [types.InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs  ရွေးချယ်ပေးပါ။ !", callback_data=f"lang#{search}#home")]
            )


    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    f"↓↓ {search}  ↓↓", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ],[
                types.InlineKeyboardButton(
                    f"📥  Download 📥", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ]
        ]

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Bot.on_callback_query(filters.regex(r"^select_lang"))
async def select_language(bot, query):
    data_parts = query.data.split("#")
    if len(data_parts) < 2:
        return await query.answer("Invalid data format.", show_alert=True)
    req = query.from_user.id if query.from_user else 0
    _, search = data_parts

    btn = [
        [
            types.InlineKeyboardButton("↓ Channel နဲ့ Video Quality ရွေးချယ်ပါ။ ↓", callback_data=f"lang#{search}#unknown")
        ],
        [
            types.InlineKeyboardButton("Channel Myanmar", callback_data=f"lang#{search}#cm"),
            types.InlineKeyboardButton("Gold Channel", callback_data=f"lang#{search}#gc"),
        ],
        [
            types.InlineKeyboardButton("One Channel", callback_data=f"lang#{search}#one"),
            types.InlineKeyboardButton("Happy Channel", callback_data=f"lang#{search}#hc"),
        ],
        [
            types.InlineKeyboardButton("360P", callback_data=f"lang#{search}#360"),
            types.InlineKeyboardButton("480P", callback_data=f"lang#{search}#480"),
            types.InlineKeyboardButton("720P", callback_data=f"lang#{search}#720"),
            types.InlineKeyboardButton("1080P", callback_data=f"lang#{search}#1080")
        ]
    ]


    try:
        await query.edit_message_reply_markup(
            reply_markup=types.InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    
    # Show an alert message
    await query.answer()

async def ch1_give_filter(bot: Bot, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands

    if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()]).*)", str(message.text), re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER']
        )
        if not files:
            return
    else:
        return
    key = f"{message.chat.id}-{message.id}"

    Cache.BUTTONS[key] = search

    if settings["IMDB"]:
        imdb = await get_poster(search, file=(files[0])["file_name"])
    else:
        imdb = {}
    Cache.SEARCH_DATA[key] = files, offset, total_results, imdb, settings
    if not settings.get("DOWNLOAD_BUTTON"):
        btn = await format_buttons(files, settings["CHANNEL"])
        if offset != "":
            req = message.from_user.id if message.from_user else 0

            btn.append(
                [
                    types.InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs  ရွေးချယ်ပေးပါ။ !", callback_data=f"select_lang#{search}")
                ]
            )

        else:
            btn.append(
                [
                    types.InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs  ရွေးချယ်ပေးပါ။!", callback_data=f"select_lang#{search}") 
                ]
            )
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    "! Lᴀɴɢᴜᴀɢᴇs  ရွေးချယ်ပေးပါ။!", callback_data=f"select_lang#{search}"
                )
            ]
        ]

    if imdb:
        cap = Config.TEMPLATE.format(
            query=search,
            **imdb,
            **locals(),
        )
    else:
        cap = f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"
    cap2 = f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"	
    ADS = [
        {"photo": "https://graph.org/file/00644e75f1d747f4b132c.jpg", "caption": cap2},
        {"photo": "https://graph.org/file/14b989e4cb562882f28c3.jpg", "caption": cap2},
    ]
    if imdb and imdb.get("poster") and settings["IMDB_POSTER"]:
        if not settings["TEXT_LINK"]:
            try:
                await message.reply_photo(
                    photo=imdb.get("poster"),  # type: ignore
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
            except (errors.MediaEmpty, errors.PhotoInvalidDimensions, errors.WebpageMediaEmpty):
                pic = imdb.get("poster")
                poster = pic.replace(".jpg", "._V1_UX360.jpg")
                await message.reply_photo(
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
        else:
            file_send = await bot.send_photo(
                chat_id=Config.FILE_GROUP2,
                photo=imdb.get("poster"),
                caption=cap[:1024],
                reply_markup=types.InlineKeyboardMarkup(btn),
            )
            ad1 = random.choice(ADS)
            photo_url = ad1["photo"]
            caption = ad1["caption"]
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                        [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send.link)]
                    ]
                ),
                quote=True,
            )
    else:
        if not settings["TEXT_LINK"]:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True
            )
        else:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            file_send3 = await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True
            )
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                        [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send3.link)]
                    ]
                ),
                quote=True
            )


async def ch11_give_filter(bot: Bot, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands

    if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()]).*)", str(message.text), re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER']
        )
        if not files:
            return
    else:
        return
    key = f"{message.chat.id}-{message.id}"

    Cache.BUTTONS[key] = search

    if settings["IMDB"]:
        imdb = await get_poster(search, file=(files[0])["file_name"])
    else:
        imdb = {}
    Cache.SEARCH_DATA[key] = files, offset, total_results, imdb, settings
    if not settings.get("DOWNLOAD_BUTTON"):
        btn = await format_buttons(files, settings["CHANNEL"])
        if offset != "":
            req = message.from_user.id if message.from_user else 0
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
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    f"📥  {search}  📥", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ]
        ]

    if imdb:
        cap = Config.TEMPLATE.format(
            query=search,
            **imdb,
            **locals(),
        )
    else:
        cap = f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"
    cap2 = f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"	
    ADS = [
        {"photo": "https://graph.org/file/00644e75f1d747f4b132c.jpg", "caption": cap2},
        {"photo": "https://graph.org/file/14b989e4cb562882f28c3.jpg", "caption": cap2},
    ]
    if imdb and imdb.get("poster") and settings["IMDB_POSTER"]:
        if not settings["TEXT_LINK"]:
            try:
                await message.reply_photo(
                    photo=imdb.get("poster"),  # type: ignore
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
            except (errors.MediaEmpty, errors.PhotoInvalidDimensions, errors.WebpageMediaEmpty):
                pic = imdb.get("poster")
                poster = pic.replace(".jpg", "._V1_UX360.jpg")
                await message.reply_photo(
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
        else:
            file_send = await bot.send_photo(
                chat_id=Config.FILE_GROUP2,
                photo=imdb.get("poster"),
                caption=cap[:1024],
                reply_markup=types.InlineKeyboardMarkup(btn),
            )
            ad1 = random.choice(ADS)
            photo_url = ad1["photo"]
            caption = ad1["caption"]
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                        [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send.link)]
                    ]
                ),
                quote=True,
            )
    else:
        if not settings["TEXT_LINK"]:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True
            )
        else:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            file_send3 = await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True
            )
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                        [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send3.link)]
                    ]
                ),
                quote=True
            )


@Bot.on_callback_query(filters.regex(r"^next"))  # type: ignore
async def next_page(bot: Bot, query: types.CallbackQuery):
    _, req, key, offset = query.data.split("_")  # type: ignore
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This is not for you", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = Cache.BUTTONS.get(key)
    if not search:
        await query.answer(
            "You are using one of my old messages, please send the request again.",
            show_alert=True,
        )
        return

    files, n_offset, total = await a_filter.get_search_results(
        search, offset=offset, filter=True
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")

    btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"📃 Pages {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
            ]
        )
    elif off_set is None:
        btn.append(
            [
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}"
                ),
            ]
        )
    else:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}"
                ),
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=types.InlineKeyboardMarkup(btn)
        )
    except errors.MessageNotModified:
        pass
    await query.answer()


@Bot.on_callback_query(filters.regex("^file"))  # type: ignore
async def handle_file(bot: Bot, query: types.CallbackQuery):
    _, file_id = query.data.split()
    file_info = await a_filter.get_file_details(file_id)  # type: ignore
    if not file_info:
        return await query.answer("FileNotFoundError", True)
    if file_info["file_type"] == "photo":
        file_id = file_info["file_ref"]
    query.message.from_user = query.from_user
    isMsg = query.message.chat.type == enums.ChatType.PRIVATE
    if not await check_fsub(bot, query.message, sendMsg=isMsg):
        if not isMsg:
            return await query.answer(url=f"https://t.me/{bot.me.username}?start=fsub")
        return await query.answer("Please Join My Update Channel and click again")
    try:         
        file_send = await bot.send_cached_media(
                chat_id=Config.FILE_CHANNEL2,
                file_id=file_id,
                caption=Config.CUSTOM_FILE_CAPTION2.format(
                file_name=file_info["file_name"],
                file_size=get_size(file_info["file_size"]),
                caption=file_info["caption"],
            ),
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton("Join Channel", url="https://t.me/+6lHs-byrjxczY2U1")],
                        [types.InlineKeyboardButton("Group Link ", url="https://t.me/+X7DNvf9iCy5jOGJl")]
                    ]
            ),
                reply_to_message_id=query.message.id,
        )
        caption1 = f"⚠️{query.from_user.mention} \n\nအချောလေး ရှာတဲ့ဇာတ်ကား အဆင့်သင့်ပါ ⬇️ "
        settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
        if settings["DOWNLOAD_BUTTON"]:
            await query.message.reply_text(                
                caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('Join Channel Link', url="https://t.me/+H7ERsk_04EoxOTU1")],
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]} {file_info["caption"]}📥', url=file_send.link)]
                    ]
                ),
                quote=True,
                disable_web_page_preview=True,
            )
        else:
            await bot.send_message(
                chat_id=query.from_user.id,                
                text=caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton( 'Join Channel link', url="https://t.me/+H7ERsk_04EoxOTU1")],
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]} {file_info["caption"]} 📥', url=file_send.link)]
                    ]
                )
            )
    except errors.PeerIdInvalid:
        return await query.answer(f"https://t.me/{bot.me.username}?start=okok")
    await query.answer(f'Sending : သင်နှိပ်လိုက်တဲ့ ဇာတ်ကားအား Bot Direct Message သို့ပေးပို့လိုက်ပါပြီ \n\nCheck bot Direct Message \n\n {file_info["file_name"]}')	



async def ch9_imdb(bot: Bot, message: types.Message, text=True):
    if message.text.startswith("/"):
        return  # ignore commands
    
    if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()]).*)", str(message.text), re.UNICODE):
    #if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()\d]).*)", message.text): 
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True
        )
        if not files:
            return
    else:
        return
    key = f"{message.chat.id}-{message.id}"

    Cache.BUTTONS[key] = search
    
    if settings["IMDB"]:
        imdb = await get_poster(search, file=(files[0])["file_name"])
	
    else:
        imdb = {}

    cap = f"{search}\n\n"
    
    if imdb:
        
        cap += Config.TEMPLATE2.format(
            query=search,
            **imdb,
            **locals(),
        )

    cap += f"""<a href='https://t.me/+X7DNvf9iCy5jOGJl'>ဇာတ်ကား ကြည့်ရန်
အောက်က Link ကို Join ပါ ⬇️</a>
https://t.me/+X7DNvf9iCy5jOGJl

ဂရုထဲရောက်ရင်
👉<code>  {search}  </code> 👈 ဟုရိုက်ပြီး

ဇာတ်ကားကို ကြည့်ရှုနိုင်ပါသည်။

<a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗦𝗧𝗢𝗥𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>"""
 
    if imdb and imdb.get("poster") and settings["IMDB_POSTER"]:
        try:
            await bot.send_photo(
                Config.FILE_CHANNEL3,
		photo=imdb.get("poster"),
                caption=cap,
	    )

        except (
            errors.MediaEmpty,
            errors.PhotoInvalidDimensions,
            errors.WebpageMediaEmpty,
        ):
            pic = imdb.get("poster")
            poster = pic.replace(".jpg", "._V1_UX360.jpg")
            await bot.send_photo(
                Config.FILE_CHANNEL3,
                photo=poster,
                caption=cap[:1024], 
	    )
        except Exception as e:
            log.exception(e)
            await message.reply_text(
                cap, quote=True
            )
    else:
        await message.reply_text(
            cap,            
            quote=True,
            disable_web_page_preview=True,
        )

 
	
