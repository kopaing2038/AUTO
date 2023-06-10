import math
import re
import random
import asyncio
from bot import Bot
from pyrogram import enums, errors, filters, types
from pyrogram.errors import MessageNotModified

from ..config import Config

from ..database import a_filter, b_filter, c_filter
from ..database import configDB as config_db
from ..utils.botTools import check_fsub, format_buttons, format_buttons2, get_size, parse_link
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
    #a = await ch1_give_filter(bot, message)
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['V_FILTER'] or settings['PHOTO_FILTER']:
        a = await ch1_give_filter(bot, message)
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['CH_POST']:
        kt = await ch9_imdb(bot, message)
        return 
   
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['V_FILTER2'] or settings['PHOTO_FILTER2']:
        b = await ch2_give_filter(bot, message)
        return    

    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['V_FILTER3'] or settings['PHOTO_FILTER3']:
        c = await ch3_give_filter(bot, message)
        return

    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['V_FILTER4'] or settings['PHOTO_FILTER4']:
        d = await ch4_give_filter(bot, message)
        return

@Bot.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    data_parts = re.split(r"(?<!\\)#", query.data)

    if len(data_parts) < 2:
        return await query.answer("Invalid data format.", show_alert=True)

    _, search, language = data_parts + [""] * (3 - len(data_parts))
    req = query.from_user.id if query.from_user else 0
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This is not for you", show_alert=True)

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
                        text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}"
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
    req = query.from_user.id if query.from_user else 0

    _, search = data_parts

    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This is not for you", show_alert=True)

    btn = [
        [
            types.InlineKeyboardButton("↓ Channel နဲ့ Video Quality ရွေးချယ်ပါ။ ↓", callback_data=f"lang#{search}#unknown")
        ],
        [
            types.InlineKeyboardButton("Eɴɢʟɪꜱʜ", callback_data=f"lang#{search}#eng"),
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
        ],
        [
            types.InlineKeyboardButton("All List", callback_data=f"lang#{search}#home")
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

    if re.findall(r"^(\/|,|!|\.|[\U0001F600-\U000E007F\[\]])", str(message.text), re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files_a, offset, total_results_a = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER'], video=settings['V_FILTER']
        )
        files_b, offset, total_results_b = await b_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER'], video=settings['V_FILTER']
        )
        files_c = []  # Initialize files_c as an empty list
        if not files_a and not files_b:
            search = message.text
            files_c, offset, total_results_c = await c_filter.get_search_results(
                search, offset=0, filter=True, photo=settings['PHOTO_FILTER'], video=settings['V_FILTER']
            )
            if not files_c:
                return
    else:
        return

    files = files_a + files_b or files_c  # Combine the files from all filters
    total_results = total_results_a + total_results_b or total_results_c 
    btn_a = []
    btn_b = []
    btn_c = []

    if files_a:
        key = f"{message.chat.id}-{message.id}"
        Cache.BUTTONS[key] = search
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["IMDB"]:
            imdb = await get_poster(search, file=(files_a[0])["file_name"])
        else:
            imdb = {}
        Cache.SEARCH_DATA[key] = files_a, offset, total_results_a, imdb, settings

    elif files_b:
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

    else:
        return
    cap = f"""🔮 𝙌𝙪𝙚𝙧𝙮 : {search} 
📥 𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️ 𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention}\n\n"""
    if files_a:
        if not settings.get("DOWNLOAD_BUTTON"):
            if offset != "":
                req = message.from_user.id if message.from_user else 0
                btn_a.append(
                    [
                        types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
                    ]
                )
            else:
                btn_a.append(
                    [types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")]
                )
        else:
            btn_a = [
                [
                    types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
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
                            text="NEXT ⏩", callback_data=f"ch2next_{req}_{key}_{offset}"
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
        cap += Config.TEMPLATE.format(
            query=search,
            **imdb,
            **locals(),
        )

    else:
        cap += f"𝗤𝘂𝗲𝗿𝘆   :{search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"
    cap2 = f"""
🔮𝙌𝙪𝙚𝙧𝙮 : {search} 
📥𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention} 
    
⚠️<a href='https://t.me/kopainglay15'>ကြော်ငြာများထည့်သွင်းရန်</a>"""

    ADS = [
        {"photo": "https://graph.org/file/57c7be369ccd72eff94ee.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/7fb891f2249f1400c1fee.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/708102b70a54d649676d6.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/fbd0926e14e45ea736e03.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},	
        {"photo": "https://graph.org/file/e205ea937a0dcdf23c4b1.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/5930490dce2720cea4387.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/302dda114e732957e109b.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/77075138db8fa65b0c4e4.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/1c4f825c25c71a5a56335.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
        {"photo": "https://graph.org/file/5e2b262b1f3ad6a50cf31.jpg", "caption": f"""────── • ADS • ──────
ဂိမ်းကစားမယ်ဆို FHM95 ကိုသတိရလိုက်ပါ...

မန်ဘာအကောင့်ဖွင့်တာနဲ့ 👉  ဖရီး 3,000 
ပထမအကြိမ်ငွေဖြည့်တာနဲ့ 👉  ဖရီး 15,000  ရယူနိုင်ပါတယ် 

စလော့ ငါးပစ် ရှမ်းကိုးမီး ခြောက်ကောင်ဂျင် ဂိမ်းတွေ ရှယ်ကစားလိုရတယ်နော် ဒါ့အပြင် တိုက်ရိုက်ဒိုင်အချောတွေနဲ့ကစားလိုရမည့် Live Casino ဂိမ်းလဲရှိပါသေးတယ် 

ဂိမ်း Download လုပ်ရန်နှင့် 🅵🅷🅼95 ကိုဆက်သွယ်ရန် 🔥 https://fhm95.net/online-fhm/ 🔥 နှိပ်လိုက်ပါ
────── • ◆ • ──────

{cap2}"""},
    ]
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


async def ch2_give_filter(bot: Bot, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands

    if re.findall(r"^(\/|,|!|\.|[\U0001F600-\U000E007F\[\]])", str(message.text), re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files_a, offset, total_results_a = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER2'], video=settings['V_FILTER2']
        )
        files_b, offset, total_results_b = await b_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER2'], video=settings['V_FILTER2']
        )
        files_c = []  # Initialize files_c as an empty list
        if not files_a and not files_b:
            search = message.text
            files_c, offset, total_results_c = await c_filter.get_search_results(
                search, offset=0, filter=True, photo=settings['PHOTO_FILTER2'], video=settings['V_FILTER2']
            )
            if not files_c:
                return
    else:
        return

    files = files_a + files_b or files_c  # Combine the files from all filters
    total_results = total_results_a + total_results_b or total_results_c 
    btn_a = []
    btn_b = []
    btn_c = []
    cap = f"""🔮 𝙌𝙪𝙚𝙧𝙮 : {search} 
📥 𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️ 𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention}\n\n"""
    if files_a:
        key = f"{message.chat.id}-{message.id}"
        Cache.BUTTONS[key] = search
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["IMDB"]:
            imdb = await get_poster(search, file=(files_a[0])["file_name"])
        else:
            imdb = {}
        Cache.SEARCH_DATA[key] = files_a, offset, total_results_a, imdb, settings

    elif files_b:
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

    else:
        return

    if files_a:
        if not settings.get("DOWNLOAD_BUTTON"):
            if offset != "":
                req = message.from_user.id if message.from_user else 0
                btn_a.append(
                    [
                        types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
                    ]
                )
            else:
                btn_a.append(
                    [types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")]
                )
        else:
            btn_a = [
                [
                    types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
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
                            text="NEXT ⏩", callback_data=f"ch2next_{req}_{key}_{offset}"
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
        cap += Config.TEMPLATE.format(
            query=search,
            **imdb,
            **locals(),
        )

    else:
        cap += f"𝗤𝘂𝗲𝗿𝘆   :{search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"
    cap2 = f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"	
    ADS = [
        {"photo": "https://graph.org/file/c40a9f62fdca19702e93c.jpg", "caption": cap2},
        {"photo": "https://graph.org/file/c40a9f62fdca19702e93c.jpg", "caption": cap2},
    ]
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


async def ch3_give_filter(bot: Bot, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands

    if re.findall(r"^(\/|,|!|\.|[\U0001F600-\U000E007F\[\]])", str(message.text), re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files_a, offset, total_results_a = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER3'], video=settings['V_FILTER3']
        )
        files_b, offset, total_results_b = await b_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER3'], video=settings['V_FILTER3']
        )
        files_c = []  # Initialize files_c as an empty list
        if not files_a and not files_b:
            search = message.text
            files_c, offset, total_results_c = await c_filter.get_search_results(
                search, offset=0, filter=True, photo=settings['PHOTO_FILTER3'], video=settings['V_FILTER3']
            )
            if not files_c:
                return
    else:
        return

    files = files_a + files_b or files_c  # Combine the files from all filters
    total_results = total_results_a + total_results_b or total_results_c 
    btn_a = []
    btn_b = []
    btn_c = []
    cap = f"""🔮 𝙌𝙪𝙚𝙧𝙮 : {search} 
📥 𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️ 𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention}\n\n"""
    if files_a:
        key = f"{message.chat.id}-{message.id}"
        Cache.BUTTONS[key] = search
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["IMDB"]:
            imdb = await get_poster(search, file=(files_a[0])["file_name"])
        else:
            imdb = {}
        Cache.SEARCH_DATA[key] = files_a, offset, total_results_a, imdb, settings

    elif files_b:
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

    else:
        return

    if files_a:
        if not settings.get("DOWNLOAD_BUTTON"):
            if offset != "":
                req = message.from_user.id if message.from_user else 0
                btn_a.append(
                    [
                        types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
                    ]
                )
            else:
                btn_a.append(
                    [types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")]
                )
        else:
            btn_a = [
                [
                    types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
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
                            text="NEXT ⏩", callback_data=f"ch2next_{req}_{key}_{offset}"
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
        cap += Config.TEMPLATE.format(
            query=search,
            **imdb,
            **locals(),
        )

    else:
        cap += f"𝗤𝘂𝗲𝗿𝘆   :{search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"
    cap3 = f"""🔮 𝙌𝙪𝙚𝙧𝙮 : {search} 
📥 𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️ 𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention} 

⚠️<a href='https://t.me/kopainglay15'>ကြော်ငြာများထည့်သွင်းရန်</a>"""

    cap2 = f"""────── • ADS • ──────
အပျင်းပြေ အရင်းကြေ ပလေးဖိုအတွက် RBY99 မှ 
မန်ဘာဝင်သူတွေအတွက် (3)ရက်တစ်ကြိမ် 
Free-10000 ပေးနေပါပြီ

RBY99 မှာဆိုရင် 
-စလော့၊ငါးပစ်၊ဘင်းဂိုး ဂိမ်းများစွာနဲ့
-ရှမ်းကိုးမီး
-Sexy Girl လေးတွေရဲ့တိုက်ရိုက်လွှင့်အွန်လိုင်းကာစီနိုတွေအပြင်
-ဘောလုံးပါလောင်းနိုင်လို ဂိမ်းအကောင့်တစ်ခုဖွင့်ရုံနဲ့တစ်နေရာတည်းမှာစုံစုံလင်လင်ကစားလိုရနေပြီနော်

Viber-09 459666076 
Viber Link 👉 https://jdb.link/rby99viber
Telegram Link 👉 https://jdb.link/RBY99
Website Link 👉 https://www.rby999.com/?pid=KP
────── • ◆ • ──────
"""

    ADS = [
        {"photo": "https://graph.org/file/00644e75f1d747f4b132c.jpg", "caption": f"""{cap2}

{cap3}"""},		
        {"photo": "https://graph.org/file/14b989e4cb562882f28c3.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/d1215889dbfba6faa8d03.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/c177d882351c729ac7e8e.jpg", "caption": f"""{cap2}

{cap3}"""},	
        {"photo": "https://graph.org/file/9f324e79d00f2ec0bcafa.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/847d183ba402a64a7ba49.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/55b79812324eb343d3558.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/820906d948015cf87296c.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/b5ce464f5d8a614e1429e.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/417ce1b6dd431b931f134.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/8157c2d8dcf36c990bb1e.jpg", "caption": f"""{cap2}

{cap3}"""},
    ]
        
        
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


async def ch4_give_filter(bot: Bot, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands

    if re.findall(r"^(\/|,|!|\.|[\U0001F600-\U000E007F\[\]])", str(message.text), re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files_a, offset, total_results_a = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER4'], video=settings['V_FILTER4']
        )
        files_b, offset, total_results_b = await b_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER4'], video=settings['V_FILTER4']
        )
        files_c = []  # Initialize files_c as an empty list
        if not files_a and not files_b:
            search = message.text
            files_c, offset, total_results_c = await c_filter.get_search_results(
                search, offset=0, filter=True, photo=settings['PHOTO_FILTER4'], video=settings['V_FILTER4']
            )
            if not files_c:
                return
    else:
        return

    files = files_a + files_b or files_c  # Combine the files from all filters
    total_results = total_results_a + total_results_b or total_results_c 
    btn_a = []
    btn_b = []
    btn_c = []
    cap = f"""🔮 𝙌𝙪𝙚𝙧𝙮 : {search} 
📥 𝙏𝙤𝙩𝙖𝙡 : {total_results} 
🙋🏻‍♂️ 𝙍𝙚𝙦𝙪𝙚𝙨𝙩 : {message.from_user.mention}\n\n"""
    if files_a:
        key = f"{message.chat.id}-{message.id}"
        Cache.BUTTONS[key] = search
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["IMDB"]:
            imdb = await get_poster(search, file=(files_a[0])["file_name"])
        else:
            imdb = {}
        Cache.SEARCH_DATA[key] = files_a, offset, total_results_a, imdb, settings

    elif files_b:
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

    else:
        return

    if files_a:
        if not settings.get("DOWNLOAD_BUTTON"):
            if offset != "":
                req = message.from_user.id if message.from_user else 0
                btn_a.append(
                    [
                        types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
                    ]
                )
            else:
                btn_a.append(
                    [types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")]
                )
        else:
            btn_a = [
                [
                    types.InlineKeyboardButton(f"{search} အတွက် Lᴀɴɢᴜᴀɢᴇs ရွေးချယ်ပါ။!", callback_data=f"select_lang#{search}")
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
                            text="NEXT ⏩", callback_data=f"ch2next_{req}_{key}_{offset}"
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
        cap += Config.TEMPLATE.format(
            query=search,
            **imdb,
            **locals(),
        )

    else:
        cap += f"𝗤𝘂𝗲𝗿𝘆   :{search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"
    cap2 = f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"	
    ADS = [
        {"photo": "https://graph.org/file/c40a9f62fdca19702e93c.jpg", "caption": cap2},
        {"photo": "https://graph.org/file/c40a9f62fdca19702e93c.jpg", "caption": cap2},
    ]
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

    btn = await format_buttons2(files, settings["CHANNEL"])  # type: ignore

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


@Bot.on_callback_query(filters.regex(r"^ch2next"))  # type: ignore
async def ch2next_page(bot: Bot, query: types.CallbackQuery):
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
                    "⏪ BACK", callback_data=f"ch2next_{req}_{key}_{off_set}"
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
                    "NEXT ⏩", callback_data=f"ch2next_{req}_{key}_{n_offset}"
                ),
            ]
        )
    else:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"ch2next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"ch2next_{req}_{key}_{n_offset}"
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
async def ch2next_page(bot: Bot, query: types.CallbackQuery):
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
                    "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"ch3next_{req}_{key}_{off_set}"
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
                    "𝐍𝐄𝐗𝐓 ➪", callback_data=f"ch3next_{req}_{key}_{n_offset}"
                ),
            ]
        )
    else:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"ch3next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "𝐍𝐄𝐗𝐓 ➪", callback_data=f"ch3next_{req}_{key}_{n_offset}"
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
            m = await query.message.reply_text(f"**Here are the search results for")  
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
            m = await query.message.reply_text(f"**Here are the search results for")  
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

 
	
