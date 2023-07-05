from bot import Bot
from ..config import Config
from pyrogram import enums, errors, filters, types

from ..database import configDB as config_db
from ..utils.botTools import CONFIGURABLE, get_bool, get_buttons


@Bot.on_message(filters.command("settings"))  # type: ignore
async def handle_settings(bot: Bot, msg: types.Message):
    if msg.chat.type == enums.ChatType.PRIVATE:
        settings = await config_db.get_settings(f"SETTINGS_PM")
    else:
        settings = await config_db.get_settings(f"SETTINGS_{msg.chat.id}")

    await msg.reply(
        "Configure your bot here", reply_markup=types.InlineKeyboardMarkup(get_buttons(settings))  # type: ignore
    )


@Bot.on_callback_query(filters.regex("^settings"))  # type: ignore
async def setup_settings(bot: Bot, query: types.CallbackQuery):
    if query.from_user.id not in Config.ADMINS:
        return await query.answer("This is not for you!")
    set_type, key = query.data.split("#")  # type: ignore
    if set_type == "settings_info":
        return await query.answer(CONFIGURABLE[key]["help"], show_alert=True)  # type: ignore

    # setattr(Config, key, get_bool(getattr(Config, key)))
    if query.message.chat.type == enums.ChatType.PRIVATE:
        data_key = "SETTINGS_PM"
    else:
        data_key = f"SETTINGS_{query.message.chat.id}"
    settings = await config_db.get_settings(data_key)
    settings[key] = get_bool(settings.get(key, True))  # type: ignore
    # setattr(Config, key, settings[key])


    await config_db.update_config(data_key, settings)
    await query.answer()
    try:
        await query.edit_message_reply_markup(types.InlineKeyboardMarkup(get_buttons(settings)))  # type: ignore
    except errors.MessageNotModified:
        pass
