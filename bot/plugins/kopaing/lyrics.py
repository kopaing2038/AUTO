from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

API = "https://apis.xditya.me/lyrics?song="

@Client.on_message(filters.text & filters.command(["lyrics"]))
async def sng(bot, message):
    if not message.reply_to_message:
        await message.reply_text("Please reply to a message")
    else:
        mee = await message.reply_text("`Searching 🔎`")
        song = message.reply_to_message.text
        chat_id = message.from_user.id
        if song is not None and song.strip():  # Check if the song is not None and not empty or only whitespace
            rpl = lyrics(song)
            await mee.delete()
            try:
                await mee.delete()
                await bot.send_message(
                    chat_id,
                    text=rpl,
                    reply_to_message_id=message.id,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Creator", url="t.me/KOPAINGLAY15")]])
                )
            except Exception as e:
                await message.reply_text(
                    f"I Can't Find A Song With `{song}`",
                    quote=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Creator", url="t.me/KOPAINGLAY15")]])
                )
        else:
            await message.reply_text("Please provide a valid song name.")

def search(song):
    r = requests.get(API + song)
    find = r.json()
    return find

def lyrics(song):
    fin = search(song)
    if "lyrics" not in fin:
        return f"Lyrics not found for {song}"
    text = f'**🎶 Successfully Extracted Lyrics of {song}**\n\n'
    text += f'`{fin["lyrics"]}`'
    text += '\n\n\n**Made By @KOPAINGLAY15**'
    return text
