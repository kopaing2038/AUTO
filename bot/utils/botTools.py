import base64
from struct import pack
import string
from bot import bot
from pyrogram import Client, enums, errors, types
from pyrogram.file_id import FileId

from ..config import Config
from ..database import configDB as config_db
from ..usersDb import usersDB
from .cache import Cache
from .logger import LOGGER

log = LOGGER(__name__)

db = Database(Config.DATABASE_URI, Config.SESSION_NAME)
CONFIGURABLE = {
    "IMDB": {"help": "Enable or disable IMDB status", "name": "Imdb Info"},
    "CHANNEL": {"help": "Redirect to Channel / Send File", "name": "Channel"},
    "CHANNEL2": {"help": "Redirect to Channel / Send File", "name": "Channel2"},
    "CHANNEL3": {"help": "Redirect to Channel / Send File", "name": "Channel3"},
    "IMDB_POSTER": {"help": "Disable / Enable IMDB posters", "name": "IMDb Posters"},
    "PM_IMDB": {"help": "Enable or disable IMDB status in PM", "name": "PM IMDb Info"},
    "PM_IMDB_POSTER": {"help": "Disable / Enable IMDB posters in PM", "name": "PM IMDb Posters"},
    "DOWNLOAD_BUTTON": {"help": "Enable / disable download button", "name": "Download Button"},
    "PHOTO_FILTER": {"help": "Enable / disable photo filter", "name": "Photo Filter"},
    "PHOTO_FILTER2": {"help": "Enable / disable photo filter", "name": "Photo Filter 2"},
    "PHOTO_FILTER3": {"help": "Enable / disable photo filter", "name": "Photo Filter 3"},
    "PHOTO_FILTER4": {"help": "Enable / disable photo filter", "name": "Photo Filter 4"},
    "PHOTO_FILTER5": {"help": "Enable / disable photo filter", "name": "Photo Filter 5"},
    "V_FILTER": {"help": "Enable / disable Video filter", "name": "Video Filter"},
    "V_FILTER2": {"help": "Enable / disable Video filter", "name": "Video Filter 2"},
    "V_FILTER3": {"help": "Enable / disable Video filter", "name": "Video Filter 3"},
    "V_FILTER4": {"help": "Enable / disable Video filter", "name": "Video Filter 4"},
    "V_FILTER5": {"help": "Enable / disable Video filter", "name": "Video Filter 5"},
    "CH_POST": {"help": "Enable / disable Ch Post", "name": "Ch POst"},
    "TEXT_LINK": {"help": "Enable / disable Text Link", "name": "Text Link"},
}


def b64_encode(s: str) -> str:

    return base64.urlsafe_b64encode(s.encode("ascii")).decode().strip("=")


def b64_decode(s: str) -> str:
    return (base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))).decode("ascii")


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id: str) -> str:
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack("<iiqq", int(decoded.file_type), decoded.dc_id, decoded.media_id, decoded.access_hash)
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref  # type: ignore

    


def get_size(size: int) -> str:
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)  # type: ignore
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0  # type: ignore
    return "%.2f %s" % (size, units[i])

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def get_bool(current: bool) -> bool:
    if current == True:
        return False
    else:
        return True


def better_bool(key: bool) -> str:
    if key == True:
        return "Enabled"
    return "Disabled"


def get_buttons(settings: dict):
    BTN = []
    for config in CONFIGURABLE:
        BTN.append(
            [
                types.InlineKeyboardButton(
                    CONFIGURABLE[config]["name"], callback_data=f"settings_info#{config}"
                ),
                types.InlineKeyboardButton(
                    better_bool(settings.get(config, True)), callback_data=f"settings_set#{config}"
                ),
            ]
        )
    return BTN

async def get_settings(group_id):
    settings = Cache.SETTINGS.get(group_id)
    if not settings:
        settings = await db.CONNECTION(group_id)
        Cache.SETTINGS[group_id] = settings
    return settings

async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    Cache.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)

async def parse_link(chat_id: int, msg_id: int) -> str:
    username = Cache.USERNAMES.get(chat_id)
    if username is None:
        try:
            chat = await bot.get_chat(chat_id)
        except Exception as e:
            log.exception(e)
            username = ""
        else:
            username = chat.username if chat.username else ""  # type: ignore
        Cache.USERNAMES[chat_id] = username
    if username:
        return f"https://t.me/{username}/{msg_id}"
    return f"https://t.me/c/{(str(chat_id)).replace('-100', '')}/{msg_id}"


async def update_config():
    for config in CONFIGURABLE:
        value = await config_db.get_settings(config)
        if value is not None:
            setattr(Config, config, value)


async def format_buttons(files: list, channel: bool):
    if channel:
        btn = [
            [
                types.InlineKeyboardButton(
                    text=f" {file['file_name']} {get_size(file['file_size'])}",
                    url=f'{(await parse_link(file["chat_id"], file["message_id"]))}',
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    text=f"{file['file_name']} {get_size(file['file_size'])}",
                    callback_data=f"file {file['_id']}",
                ),
            ]
            for file in files
        ]

    for row in btn:
        for button in row:
            caption = button.text.lower()
            caption = caption.translate(str.maketrans(
                "abcdefghijklmnopqrstuvwxyz0123456789",
                "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹"
            ))
            button.text = caption

    return btn

async def format_buttons2(files: list, channel: bool):
    if channel:
        btn = [
            [
                types.InlineKeyboardButton(
                    text=f" {ch2file['file_name']} {get_size(ch2file['file_size'])}",
                    url=f'{(await parse_link(ch2file["chat_id"], ch2file["message_id"]))}',
                ),
            ]
            for ch2file in files
        ]
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    text=f"{ch2file['file_name']} {get_size(ch2file['file_size'])}",
                    callback_data=f"ch2file {ch2file['_id']}",
                ),
            ]
            for ch2file in files
        ]

    for row in btn:
        for button in row:
            caption = button.text.lower()
            caption = caption.translate(str.maketrans(
                "abcdefghijklmnopqrstuvwxyz0123456789",
                "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹"
            ))
            button.text = caption

    return btn


FORCE_TEXT = """ 🗣 သင်သည် အောက်တွင်ပေးထားသော ကျွန်ုပ်တို့၏ Back-up ချန်နယ်တွင် မရှိသောကြောင့် ရုပ်ရှင်ဖိုင်ကို မရနိုင်ပါ။
ရုပ်ရှင်ဖိုင်ကို လိုချင်ပါက၊ အောက်ဖော်ပြပါ '🍿ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ🍿' ခလုတ်ကို နှိပ်ပြီး ကျွန်ုပ်တို့၏ အရန်ချန်နယ်သို့ ဝင်ရောက်ပါ၊ 
 
ထို့နောက် Group ထဲတွင် သင်ကြည်‌ချင်သော ရုပ်ရှင်အား ပြန်လည်နှိပ်ပြီး start ကို နှိပ်ပါ...
ပြီးရင် ရုပ်ရှင်ဖိုင်တွေ ရလိမ့်မယ်။ ကျေးဇူးတင်ပါတယ်😇😇
 
🗣 The movie file is not available because you are not in our Back-up channel given below.
If you want the movie file, click the '🍿ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ🍿' button below and join our support channel, 
    
Then click again on the movie you want to watch in the group and click to start…
Then you will get the movie files.  Thank you 😇😇
    
"""

async def check_fsub(bot: Client, message: types.Message, try_again: str = None, sendMsg: bool = True):  # type: ignore
    user = message.from_user.id
    try:
        member = await bot.get_chat_member(Config.FORCE_SUB_CHANNEL, user)
    except errors.UserNotParticipant:
        if sendMsg:
            invite_link = await bot.create_chat_invite_link(Config.FORCE_SUB_CHANNEL)
            btn = [
                [types.InlineKeyboardButton("🍿ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ🍿", url=invite_link.invite_link)],
            ]
            if try_again:
                btn.append(
                    [
                        types.InlineKeyboardButton(
                            "Try Again", url=f"https://t.me/{bot.me.username}?start={try_again}"
                        )
                    ]
                )
            await message.reply(FORCE_TEXT, reply_markup=types.InlineKeyboardMarkup(btn))
        return False
    else:
        if member.status in [enums.ChatMemberStatus.BANNED]:
            await message.reply("you are banned to use this bot :-/")
            return False
        return True
