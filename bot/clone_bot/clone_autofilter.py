import math
import re
import random
import asyncio
from bot import Bot
from pyrogram import enums, errors, filters, types
from pyrogram.errors import MessageNotModified

from bot.config.config import Config
from bot.clone_bot.autofilter import a_filter
from bot.database import b_filter, c_filter
from bot.database import configDB as config_db
from bot.utils.botTools import check_fsub, format_buttons, format_buttons2, get_size, parse_link
from bot.utils.cache import Cache
from bot.utils.imdbHelpers import get_poster, get_photo
from bot.utils.logger import LOGGER

log = LOGGER(__name__)

@Bot.on_message(filters.group & filters.text & filters.incoming, group=-1)
async def auto_filter(bot: Bot, message: types.Message, text=True):
    #if not await check_fsub(bot, message):
        #return 
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['V_FILTER'] or settings['PHOTO_FILTER']:
        a = await ch1_give_filter(bot, message)
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['CH_POST']:
        kt = await ch9_imdb(bot, message)
        return 
   



@Bot.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    data_parts = re.split(r"(?<!\\)#", query.data)

    if len(data_parts) < 3:
        return await query.answer("Invalid data format.", show_alert=True)

    _, req, search, language = data_parts + [""] * (3 - len(data_parts))

    if int(req) not in [query.from_user.id, 0]:
        await query.answer("This is not for you\nဒါက မင်းအတွက်မဟုတ်ဘူး။", show_alert=True)
        return 

    if search in [str(query.from_user.id), "0"]:
        await query.answer(f"No {search.upper()} found!", show_alert=True)
        return

    if language == "unknown":
        return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)


    if language != "home":
        search = f"{search} {language}"

    if 3 < len(search) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True
        )

        if not files:
            await query.answer(f"The {search} file does not exist.", show_alert=True)
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

    btn = await format_buttons2(files, settings["CHANNEL"])
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
                        text="NEXT ⏩", callback_data=f"chnext2_{req}_{key}_{offset}"
                    ),
                ]
            )
        else:
            btn.append([
                types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")
            ])
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    f"↓↓ {search}  ↓↓", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ],
            [
                types.InlineKeyboardButton(
                    f"📥  Download 📥", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ]
        ]

    try:
        await query.edit_message_reply_markup(reply_markup=types.InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()


@Bot.on_callback_query(filters.regex(r"^select_lang"))
async def select_language(bot, query):
    data_parts = query.data.split("#")
    if len(data_parts) < 2:
        return await query.answer("Invalid data format.", show_alert=True)

    _, req, search = data_parts

    if int(req) not in [query.from_user.id, 0]:
        await query.answer("This is not for you\nဒါက မင်းအတွက်မဟုတ်ဘူး။", show_alert=True)
        return 

    btn = [
        [
            types.InlineKeyboardButton("↓ Channel နဲ့ Video Quality ရွေးချယ်ပါ။ ↓", callback_data=f"lang#{req}#{search}#unknown")
        ],
        [
            types.InlineKeyboardButton("Eɴɢʟɪꜱʜ", callback_data=f"lang#{req}#{search}#eng"),
            types.InlineKeyboardButton("Channel Myanmar", callback_data=f"lang#{req}#{search}#cm"),
            types.InlineKeyboardButton("Gold Channel", callback_data=f"lang#{req}#{search}#gc"),
        ],
        [
            types.InlineKeyboardButton("One Channel", callback_data=f"lang#{req}#{search}#one"),
            types.InlineKeyboardButton("Happy Channel", callback_data=f"lang#{req}#{search}#hc"),
        ],
        [
            types.InlineKeyboardButton("360P", callback_data=f"lang#{req}#{search}#360"),
            types.InlineKeyboardButton("480P", callback_data=f"lang#{req}#{search}#480"),
            types.InlineKeyboardButton("720P", callback_data=f"lang#{req}#{search}#720"),
            types.InlineKeyboardButton("1080P", callback_data=f"lang#{req}#{search}#1080")
        ],
        [
            types.InlineKeyboardButton("All List", callback_data=f"lang#{req}#{search}#home")
        ]
    ]

    try:
        await query.edit_message_reply_markup(reply_markup=types.InlineKeyboardMarkup(btn))
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
        files_b, offset, total_results_b = await b_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER'], video=settings['V_FILTER']
        )
        files_a, offset, total_results_a = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER'], video=settings['V_FILTER']
        )
        files_c = []  # Initialize files_c as an empty list
        if not files_b and not files_a:
            search = message.text
            files_c, offset, total_results_c = await c_filter.get_search_results(
                search, offset=0, filter=True, photo=settings['PHOTO_FILTER'], video=settings['V_FILTER']
            )

            if not files_c:
                english_chars = re.findall("[a-zA-Z]+", message.text)
                photo_search = "https://telegra.ph/file/19602f3dea66d7238ed69.jpg"
                nosearch = f"Sᴏʀʀʏ. {message.from_user.mention}  {search}  ကိုရှာမတွေ့ပါ။!\nရှာမတွေရတဲ့ အကြောင်းရင်းမှာ 👇\n\n◉ 1. ဤ Group တွင် ကိုးရီးယားစီးရီးများနဲ့ တစ်ကားထဲအပြီး ဇာတ်ကားများကိုသာရရှိနိုင်ပါသည်။\n\n◉ 2. ကျွန်ုပ်တို့၏ Database တွင်မရှိတာ၊ မတင်ရသေးတာ၊ မြန်မာစာတန်းထိုးမရသေးတာတစ်ခုခုပါ။ 💾\n\n◉ 3. ဒါမှမဟုတ် သင့်ရဲ့ စာလုံးပေါင်း မှားနေတာ ဖြစ်နိုင်တယ် google မှာ စာလုံးပေါင်းစစ်ဆေးကြည့်ပါ။ 🔍."
                if english_chars:
                    search = " ".join(english_chars)
                    m = await message.reply_photo(
                        photo=photo_search,
                        caption=nosearch,
                        reply_markup=types.InlineKeyboardMarkup(           
                            [
                                [types.InlineKeyboardButton(f"Sᴩᴇʟʟɪɴɢ Oɴ Gᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={search.replace(' ', '+')}")]
                            ]
                    )
                    )
                    await asyncio.sleep(30)
                    await m.delete()
                    return

    else:
        return

    #m=await message.reply_text("🔍")
    #await asyncio.sleep(2)
    #await m.delete()
    #m=await message.reply_sticker("CAACAgIAAxkBAAEEkwJkqPLz8LokQt6Cb_rB31rMcnxHUAAC9wADVp29CgtyJB1I9A0wHgQ")
    #await asyncio.sleep(1)
    #await m.delete()

    files = files_b + files_a or files_c  # Combine the files from all filters
    total_results = total_results_b + total_results_a or total_results_c 
    btn_a = []
    btn_b = []
    btn_c = []

    if files_b:
        key = f"{message.chat.id}-{message.id}"
        Cache.BUTTONS[key] = search
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["IMDB"]:
            imdb = await get_poster(search, file=(files_b[0])["file_name"])
        else:
            imdb = {}
        Cache.SEARCH_DATA[key] = files_b, offset, total_results_b, imdb, settings
        btn_b = await format_buttons(files_b, settings["CHANNEL2"])

    elif files_c:
        key = f"{message.chat.id}-{message.id}"
        Cache.BUTTONS[key] = search
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["IMDB"]:
            imdb = await get_poster(search, file=(files_c[0])["file_name"])
        else:
            imdb = {}
        Cache.SEARCH_DATA[key] = files_c, offset, total_results_c, imdb, settings
        btn_c = await format_buttons2(files_c, settings["CHANNEL3"])

    elif files_a:
        key = f"{message.chat.id}-{message.id}"
        Cache.BUTTONS[key] = search
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["IMDB"]:
            imdb = await get_poster(search, file=(files_a[0])["file_name"])
        else:
            imdb = {}
        Cache.SEARCH_DATA[key] = files_a, offset, total_results_a, imdb, settings


    else:
        return

    cap = f"""🔮 𝙌𝙪𝙚𝙧𝙮 : {search} 
📥 𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️ 𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention}\n\n"""

    req = message.from_user.id if message.from_user else 0

    if files_a:
        if not settings.get("DOWNLOAD_BUTTON"):
            req = message.from_user.id if message.from_user else 0
            if offset != "":
                req = message.from_user.id if message.from_user else 0
                btn_a.append(
                    [
                        types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{req}#{search}")
                    ]
                )
            else:
                btn_a.append(
                    [types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{req}#{search}")]
                )
        else:
            btn_a = [
                [
                    types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{req}#{search}")
                ]
            ]

    if files_b:
        if not settings.get("DOWNLOAD_BUTTON"):
            btn_b = await format_buttons(files_b, settings["CHANNEL2"])            
            if offset != "":
                req = message.from_user.id if message.from_user else 0
                btn_b.append(
                    [
                        types.InlineKeyboardButton(
                            text=f"🗓 1/{math.ceil(int(total_results_b) / 5)}",
                            callback_data="pages",
                        ),
                        types.InlineKeyboardButton(
                            text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}"
                        ),
                    ]
                )
            else:
                btn_b.append(
                    [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
                )
        else:
            btn_b = [
                [
                    types.InlineKeyboardButton(
                        f"📥  {search}  📥", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                    )
                ]
            ]

    if files_c:
        if not settings.get("DOWNLOAD_BUTTON"):
            btn_c = await format_buttons2(files_c, settings["CHANNEL3"])
            if offset != "":
                req = message.from_user.id if message.from_user else 0
                btn_c.append(
                    [
                        types.InlineKeyboardButton(
                            text=f"🗓 1/{math.ceil(int(total_results_c) / 5)}",
                            callback_data="pages",
                        ),
                        types.InlineKeyboardButton(
                            text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"ch3next_{req}_{key}_{offset}"
                        ),
                    ]
                )
            else:
                btn_c.append(
                    [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
                )
        else:
            btn_c = [
                [
                    types.InlineKeyboardButton(
                        f"📥  {search}  📥", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                    )
                ]
            ]

    if imdb:
        #cap += settings["TEMPLATE"].format(query=search, **imdb, **locals())
        cap += settings["TEMPLATE"].format(
            query=search,
            **imdb,
            **locals(),
        )

    else:
        cap += f""


    #buttons = []

    #k = 1
    #for file in files:
        #cap += f"{k}. [{file['file_name']} {get_size(file['file_size'])}]({await parse_link(file['chat_id'], file['message_id'])})\n\n"
       # k += 1




    cap2 = f"""🔮 𝙌𝙪𝙚𝙧𝙮 : {search} 
📥 𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️ 𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention}

⚠️<a href='https://t.me/kopainglay15'>ကြော်ငြာများထည့်သွင်းရန်</a>\n\n"""

    btn = btn_a + btn_b + btn_c
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
            try:
                file_send = await bot.send_photo(
                    chat_id=Config.FILE_GROUP2,
                    photo=imdb.get("poster"),
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                )
                ad1 = random.choice(settings["ADS"])
                photo_url = ad1["photo"]
                caption = ad1["caption"] + "\n\n" + cap2
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
            except (errors.MediaEmpty, errors.PhotoInvalidDimensions, errors.WebpageMediaEmpty):
                pic = imdb.get("poster")
                poster = pic.replace(".jpg", "._V1_UX360.jpg")
                file_send2 = await bot.send_photo(
                    chat_id=Config.FILE_GROUP2,
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                )
                ad1 = random.choice(settings["ADS"])
                photo_url = ad1["photo"]
                caption = ad1["caption"] + "\n\n" + cap2
                await message.reply_photo(
                    photo=photo_url,
                    caption=caption,
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                            [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send2.link)]
                        ]
                    ),
                    quote=True,
                )
    else:
        if not settings["TEXT_LINK"]:
            ad = random.choice(settings["ADS"])
            photo_url = ad["photo"]
            caption = ad["caption"] + "\n\n" + cap2
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True
            )
        else:
            ad = random.choice(settings["ADS"])
            photo_url = ad["photo"]
            caption = ad["caption"] + "\n\n" + cap2
            file_send3 = await bot.send_photo(
                chat_id=Config.FILE_GROUP2,
                photo=random.choice(Config.PICS),
                caption=cap,
                reply_markup=types.InlineKeyboardMarkup(btn),
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



@Bot.on_callback_query(filters.regex(r"^chnext2"))  # type: ignore
async def chnext2_next_page(bot: Bot, query: types.CallbackQuery):
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

    btn = await format_buttons2(files, settings["CHANNEL"])  # type: ignore

    if 0 < offset <= 5:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 5
    if n_offset == 0:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"chnext2_{req}_{key}_{off_set}"
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
                    "NEXT ⏩", callback_data=f"chnext2_{req}_{key}_{n_offset}"
                ),
            ]
        )
    else:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"chnext2_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"chnext2_{req}_{key}_{n_offset}"
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

    files, n_offset, total = await b_filter.get_search_results(
        search, offset=offset, filter=True
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")

    btn = await format_buttons(files, settings["CHANNEL2"])  # type: ignore

    if 0 < offset <= 5:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 5
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

@Bot.on_callback_query(filters.regex(r"^ch3next"))  # type: ignore
async def ch3next_next_page(bot: Bot, query: types.CallbackQuery):
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

    files, n_offset, total = await c_filter.get_search_results(
        search, offset=offset, filter=True
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")

    btn = await format_buttons2(files, settings["CHANNEL3"])  # type: ignore

    if 0 < offset <= 5:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 5
    if n_offset == 0:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"ch3next_{req}_{key}_{off_set}"
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
                    "NEXT ⏩", callback_data=f"ch3next_{req}_{key}_{n_offset}"
                ),
            ]
        )
    else:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"ch3next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"ch3next_{req}_{key}_{n_offset}"
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



@Bot.on_callback_query(filters.regex("^file"))
async def handle_file(bot: Bot, query: types.CallbackQuery):
    _, file_id = query.data.split()
    file_info_a = await a_filter.get_file_details(file_id) if file_id else None
    file_info_b = await b_filter.get_file_details(file_id) if file_id else None
    file_info_c = await c_filter.get_file_details(file_id) if file_id else None

    file_info = {}
    if file_info_a:
        file_info.update(file_info_a)
    if file_info_b:
        file_info.update(file_info_b)
    if file_info_c:
        file_info.update(file_info_c)

    if not file_info:
        return await query.answer("ဖိုင်ကို ရှာမတွေ့သော အမှား ", True)

    if file_info["file_type"] == "photo":
        file_id = file_info["file_ref"]

    query.message.from_user = query.from_user
    isMsg = query.message.chat.type == enums.ChatType.PRIVATE
    if not await check_fsub(bot, query.message, sendMsg=isMsg):
        if not isMsg:
            return await query.answer(url=f"https://t.me/{bot.me.username}?start=fsub")
        return await query.answer("Please Join My Main Channel and click again\n\nကျေးဇူးပြု၍ ကျွန်ုပ်၏ ပင်မချန်နယ်သို့ ဝင်ရောက်ပြီး ထပ်မံနှိပ်ပါ။")
    try:
        file_send = await bot.send_cached_media(
                Config.FILE_GROUP,
                file_id,
                caption=Config.CUSTOM_FILE_CAPTION.format(  # type: ignore
                file_name=file_info["file_name"],
                file_size=get_size(file_info["file_size"]),
                caption=file_info["caption"],
                user_link=query.from_user.mention,
            ),                
                reply_to_message_id=query.message.id,
        )
           
        settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
        invite_link = await bot.create_chat_invite_link(file_info["chat_id"])
        caption1 = f"Hi {query.from_user.mention} \n\nအချောလေး ရှာတဲ့ [{file_info['file_name']}]({await parse_link(file_info['chat_id'], file_info['message_id'])}) ဇာတ်ကား အဆင့်သင့်ပါ ⬇️\n\nဝင်မရရင် <a href='{invite_link.invite_link}'>🍿 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ🍿</a> ကို Join ပါ \n\n <a href='{invite_link.invite_link}'>{file_info['channel_name']}</a>"
        if not settings["DOWNLOAD_BUTTON"]:
            m = await query.message.reply_text(f"Hi {query.from_user.mention} အချောလေး [{file_info['file_name']}] ကိုတင်ပေးနေတယ် ခဏစောင့်ပေးပါ")  
            await m.edit(              
                caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton("🍿ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ🍿", url=invite_link.invite_link)],  
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]} {file_info["caption"]}📥', url=f'{(await parse_link(file_info["chat_id"], file_info["message_id"]))}')]
                    ]
                ),               
                disable_web_page_preview=True,
            )

        else:
            await bot.send_message(
                chat_id=query.from_user.id,                
                text=caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton("🍿ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ🍿", url=invite_link.invite_link)],  
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]} {file_info["caption"]} 📥', url=f'{(await parse_link(file_info["chat_id"], file_info["message_id"]))}')]
                    ]
                )
	    )

    except errors.PeerIdInvalid:
        return await query.answer(f"https://t.me/{bot.me.username}?start=okok")
    await query.answer(f'Sending: သင်နှိပ်လိုက်တဲ့ ဇာတ်ကားအား Channel သို့ပေးပို့လိုက်ပါပြီ \n\nCheck Channel Message \n\n {file_info["file_name"]}')


@Bot.on_callback_query(filters.regex("^ch2file"))
async def ch2_handle_file(bot: Bot, query: types.CallbackQuery):
    _, file_id = query.data.split()
    file_info_a = await a_filter.get_file_details(file_id) if file_id else None
    file_info_b = await b_filter.get_file_details(file_id) if file_id else None
    file_info_c = await c_filter.get_file_details(file_id) if file_id else None

    file_info = {}
    if file_info_a:
        file_info.update(file_info_a)
    if file_info_b:
        file_info.update(file_info_b)
    if file_info_c:
        file_info.update(file_info_c)

    if not file_info:
        return await query.answer("ဖိုင်ကို ရှာမတွေ့သော အမှား ", True)

    if file_info["file_type"] == "photo":
        file_id = file_info["file_ref"]

    query.message.from_user = query.from_user
    isMsg = query.message.chat.type == enums.ChatType.PRIVATE
    if not await check_fsub(bot, query.message, sendMsg=isMsg):
        if not isMsg:
            return await query.answer(url=f"https://t.me/{bot.me.username}?start=fsub")
        return await query.answer("Please Join My Main Channel and click again\n\nကျေးဇူးပြု၍ ကျွန်ုပ်၏ ပင်မချန်နယ်သို့ ဝင်ရောက်ပြီး ထပ်မံနှိပ်ပါ။")
    try:              
        file_send = await bot.send_cached_media(
                chat_id=Config.FILE_GROUP,
                file_id=file_id,
                caption=Config.CUSTOM_FILE_CAPTION.format(
                file_name=file_info["file_name"],
                file_size=get_size(file_info["file_size"]),
                caption=file_info["caption"],
                user_link=query.from_user.mention,
            ),
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton("𝐕𝐈𝐏 𝐒𝐞𝐫𝐢𝐞𝐬 𝐌𝐞𝐦𝐛𝐞𝐫 ဝင်ရန်", url="https://t.me/Kpautoreply_bot")
                    ],
                    [    
                        types.InlineKeyboardButton("Channel & Group Link ", url="https://t.me/Movie_Zone_KP/3")    
                    ],           
                    [
                        types.InlineKeyboardButton("⭕️ DONATE ⭕️", url="https://t.me/kpmovielist/277"),
                        types.InlineKeyboardButton("⭕️ Owner Acc ⭕️", url="https://t.me/KOPAINGLAY15")
                    ]
                ]

            ),
                reply_to_message_id=query.message.id,
        )
        invite_link = await bot.create_chat_invite_link(file_info["chat_id"])
        caption1 = f"Hi {query.from_user.mention} \n\nအချောလေး ရှာတဲ့ <a href='{file_send.link}'>{file_info['file_name']}</a> ဇာတ်ကား အဆင့်သင့်ပါ ⬇️\n\nဝင်မရရင် <a href='https://t.me/+6Rq1ZLh5UExiNTUx'>🍿 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🍿</a> ကို Join ပါ \n\n <a href='{invite_link.invite_link}'>{file_info['channel_name']}</a>"
        settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
        if not settings["DOWNLOAD_BUTTON"]:
            m = await query.message.reply_text(f"Hi {query.from_user.mention} အချောလေး [{file_info['file_name']}] ကိုတင်ပေးနေတယ် ခဏစောင့်ပေးပါ") 
            await m.edit(              
                caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('🍿 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🍿', url="https://t.me/+6Rq1ZLh5UExiNTUx")],
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]} 📥', url=file_send.link)]
                    ]
                ),                
                disable_web_page_preview=True,
            )
        else:
            await bot.send_message(
                chat_id=query.from_user.id,                
                text=caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton(' 🍿 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🍿', url="https://t.me/+6Rq1ZLh5UExiNTUx")],
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]}  📥', url=file_send.link)]
                    ]
                )
            ) 
    except errors.PeerIdInvalid:
        return await query.answer(f"https://t.me/{bot.me.username}?start=okok")
    await query.answer(f'Sending : သင်နှိပ်လိုက်တဲ့ ဇာတ်ကားအား DATABASE GROUP သို့ပေးပို့လိုက်ပါပြီ \n\nCheck DATABASE GROUP Message \n\n {file_info["file_name"]}') 

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

 
