import base64
from struct import pack

from bot import bot
from pyrogram import Client, enums, errors, types
from pyrogram.file_id import FileId

from ..config import Config
from bot.clone_plugins import configDB as config_db
from .cache import Cache
from .logger import LOGGER

log = LOGGER(__name__)


CONFIGURABLE = {
    "IMDB": {"help": "Enable or disable IMDB status", "name": "Imdb Info"},
    "CHANNEL": {"help": "Redirect to Channel / Send File", "name": "Channel"},
    "IMDB_POSTER": {"help": "Disable / Enable IMDB posters", "name": "IMDb Posters"},
    "PM_IMDB": {"help": "Enable or disable IMDB status in PM", "name": "PM IMDb Info"},
    "PM_IMDB_POSTER": {"help": "Disable / Enable IMDB posters in PM", "name": "PM IMDb Posters"},
    "DOWNLOAD_BUTTON": {"help": "Enable / disable download button", "name": "Download Button"},
    "PHOTO_FILTER": {"help": "Enable / disable photo filter", "name": "Photo Filter"}
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
                    text=f"[{get_size(file['file_size'])}] {file['file_name']}",
                    url=f'{(await parse_link(file["chat_id"], file["message_id"]))}',
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {file['file_name']}",
                    callback_data=f"file {file['_id']}",
                ),
            ]
            for file in files
        ]
    return btn


FORCE_TEXT = """🗣 မတ်‌ဆွေကြည့်ချင်တဲ့ဇာတ်ကားကို ပိုပေးဖိုအတွက် 👉🏻 Join Channel 👈🏻 က Join ထားဖိုလိုပါတယ်။ 
Channel လေးကို  Join ပြီးရင် 
🔄 Try Again 👈 Tap me လေးကို နှိပ်လိုက်ရင် 👌 ရပါပြီး။ 

@Movie_Zone_KP"""


async def check_fsub(bot: Client, message: types.Message, try_again: str = None, sendMsg: bool = True):  # type: ignore
    user = message.from_user.id
    try:
        member = await bot.get_chat_member(Config.FORCE_SUB_CHANNEL, user)
    except errors.UserNotParticipant:
        if sendMsg:
            invite_link = await bot.create_chat_invite_link(Config.FORCE_SUB_CHANNEL)
            btn = [
                [types.InlineKeyboardButton("Join Channel", url=invite_link.invite_link)],
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
