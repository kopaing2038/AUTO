from bot import Bot
from pyrogram import enums, errors, filters, types
from youtubesearchpython import VideosSearch
from youtubesearchpython import SearchVideos
from bot.config import Config
from youtube_search import YoutubeSearch
import yt_dlp
import os
import requests
import wget
import math
import time
import aiofiles
import asyncio
import random
import datetime
import re
import youtube_dl
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytube.exceptions import RegexMatchError
from pytube import YouTube
from pytube import Search
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from bot.database import configDB as config_db

query_text = ""
download_links = {}


@Bot.on_message(filters.command(["song", "music", "mp3", "mp4"]) & filters.group)
async def group_song_command_handler(client, message):
	settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
	if settings['SONG']:
		await song(client, message)



async def song(client, message):
    #if message.chat.id in Config.MUSIC_AUTH_GROUPS:
        #await message.reply_text("You are not authorized to use this command in this group.")
        #return
    global query_text
    query = ' '.join(message.command[1:])
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    rpk = f"[{user_name}](tg://user?id={user_id})"
    req = message.from_user.id if message.from_user else 0

    m = await message.reply(f"**Hello {message.from_user.mention},\n\nSearching for `{query}`...**")
    query_text = query  # Store the original query text for later reference

    try:
        results = Search(query).results[:10]

        if not results:
            await m.edit(
                f"**No results found for `{query}`.**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Reload", callback_data="reload")]])
            )
            return

        buttons = []
        download_links[req] = {}  # Create a dictionary to store download links for the user

        for i, r in enumerate(results, start=1):
            title = r.title
            link = r.watch_url
            callback_data = f"song_link_{i}_{req}_{user_name}_{user_id}"  # Updated callback data
            buttons.append([InlineKeyboardButton(f"{i}. {title}", callback_data=callback_data)])
            # Store the download link for later use
            download_links[req][i] = link

        callback_data = f"reload_{req}"  # Updated callback data
        buttons.append([InlineKeyboardButton("Reload", callback_data=callback_data)])
        keyboard = InlineKeyboardMarkup(buttons)

        await m.edit(
            f"**Here are the search results for `{query}`:**",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

    except Exception as e:
        await m.edit(
            f"**`{query}` ရှာဖွေနေစဉ် အမှားအယွင်းတစ်ခု ဖြစ်ပေါ်ခဲ့သည်။ .**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Reload", callback_data=f"reload_{req}")]])
        )
        print(str(e))
        return


@Bot.on_callback_query(filters.regex('^reload$'))
async def reload_results(client, callback_query):
    message = callback_query.message
    query = query_text  # Access the stored query from the song function

    try:
        results = Search(query).results[:10]

        if not results:
            await message.reply(f"**No results found for `{query}`.**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Reload", callback_data="reload")]]))
            return

        buttons = []

        for i, r in enumerate(results, start=1):
            title = r.title
            link = r.watch_url
            buttons.append([InlineKeyboardButton(f"{i}. {title}", callback_data=f"song_link_{i}")])
            # Store the download link for later use
            download_links[i] = link

        buttons.append([InlineKeyboardButton("Reload", callback_data="reload")])
        keyboard = InlineKeyboardMarkup(buttons)

        await message.reply(f"**Here are the search results for `{query}`:**", reply_markup=keyboard, disable_web_page_preview=True)

    except Exception as e:
        await message.reply(f"**An error occurred while searching for `{query}`.**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Reload", callback_data="reload")]]))
        print(str(e))
        return



@Bot.on_callback_query(filters.regex('^song_link_'))
async def download_option(client, callback_query):
    option, index, req, user_name, user_id = callback_query.data.split("_")[1:6]
    index = int(index)
    req = int(req)

    if req != callback_query.from_user.id and req != 0:
        await callback_query.answer("This is not for you.\nဒါက မင်းအတွက်မဟုတ်ဘူး။ \nသူများရိုက်ရှာထားတာလေ သီချင်းလိုချင်ရင် ဂရုထဲကို /song musicname ရိုက်ပို့ Ok ?", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Audio (MP3)", callback_data=f"audio_{index}_{req}_{user_name}_{user_id}"), InlineKeyboardButton("Video (MP4)", callback_data=f"video_{index}_{req}_{user_name}_{user_id}")]
    ])

    await callback_query.message.edit_text(f"**Choose the desired format:**", reply_markup=keyboard)



@Bot.on_callback_query(filters.regex(r'^(audio|video)_'))
async def download_media(client, callback_query):
    global query_text
    option = callback_query.data.split("_")
    media_type = option[0]
    index = int(option[1])
    req = int(option[2])
    user_name = option[3]  # Remove the int() conversion for option[3]
    user_id = option[4] 

    if req != callback_query.from_user.id and req != 0:
        await callback_query.answer("This is not for you.\nဒါက မင်းအတွက်မဟုတ်ဘူး။ \nသူများရိုက်ရှာထားတာလေ သီချင်းလိုချင်ရင် ဂရုထဲကို /song musicname ရိုက်ပို့ Ok ?", show_alert=True)
        return

    mg = await callback_query.message.edit(f"**Downloading **")
    await mg.edit("Downloading ✪⍟⍟⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Downloading ✪✪⍟⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Downloading ✪✪✪⍟⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Downloading ✪✪✪✪⍟⍟")
    asyncio.sleep(1)
    await mg.edit("Downloading ✪✪✪✪✪⍟")
    asyncio.sleep(1)
    await mg.edit("Downloading ✪✪✪✪✪✪")
    asyncio.sleep(1)
    m = await mg.edit(f"**✪ Downloading Successful ✪ {media_type.upper()}...**")
    try:
        url = download_links[req].get(index)  # Access the download link from the correct dictionary

        if not url:
            await m.edit(f"**No download link found for index `{index}`.**")
            return

        if media_type == "audio":
            await download_audio(url, query_text, m, req, client, user_name, user_id)
        elif media_type == "video":
            await download_video(url, query_text, m, req, client, user_name, user_id)

    except Exception as e:
        await m.edit(f"**An error occurred while downloading the {media_type.upper()} file.**")
        print(str(e))


async def download_audio(url, query, message, req, client, user_name, user_id):
    try:
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        duration = info_dict['duration']
        dur = int(duration)

        thumb_name = f'thumb_{info_dict["title"]}.jpg'
        thumb = requests.get(info_dict["thumbnail"], allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        mention = f'<a href="tg://user?id={user_id}">{user_name}</a>'
        reqq = f'<b>Hey 👋 {mention} </b>\n\n<b>📫 Your {info_dict["title"]} Music File is Ready</b>\n\n{message.from_user.mention}**'
        rep = f'🎵 <b>𝑻𝒊𝒕𝒍𝒆:</b> <a href="{url}">{info_dict["title"]}</a>\n\n<b>📤 Uploaded By : <a href="https://t.me/mksviplink">© MKS Channel</a></b>'

        file_send = await client.send_audio(
            chat_id=Config.MUSIC_CHANNEL,
            audio=audio_file,
            caption=rep,
            parse_mode=enums.ParseMode.HTML,
            title=info_dict["title"],
            duration=dur,
            performer=info_dict["uploader"],
            thumb=thumb_name,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('🔎 𝕄𝕦𝕤𝕚𝕔 𝕊𝕖𝕒𝕣𝕔𝕙 𝔾𝕣𝕠𝕦𝕡 🔍', url="https://t.me/+XrP5-m5NLUIxYTU9")]
                ]
            )
        )

        await message.edit_text(
            text=reqq,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(f'📥 {info_dict["title"]}📥', url=file_send.link)],
                    [InlineKeyboardButton('📥 𝕄𝕦𝕤𝕚𝕔 𝔻𝕠𝕨𝕟𝕝𝕠𝕒𝕕 𝕃𝕚𝕟𝕜 📥', url=file_send.link)]
                ]
            )
        )
    
    except Exception as e:
        await message.edit_text("**🚫 𝙴𝚁𝚁𝙾𝚁 🚫**  Try Again")
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)



async def download_video(url, query, message, req, client, user_name, user_id):
    try:
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        try:
            with YoutubeDL(opts) as ytdl:
                ytdl_data = ytdl.extract_info(url, download=True)
        except Exception as e:
            await message.edit_text(f"**Download Failed. Please Try Again.**\n**Error:** `{str(e)}`")
            return
        c_time = time.time()
        file_stark = f"{ytdl_data['id']}.mp4"
        file_name=str(ytdl_data["title"])

        mention = f'<a href="tg://user?id={user_id}">{user_name}</a>'
        req = f'<b>Hey 👋 {mention}  </b>\n\n<b>📫 Your {file_name} Music Video File is Ready</b>\n\n{message.from_user.mention}**'
        capy = f""" 🎵 𝑻𝒊𝒕𝒍𝒆 : {file_name}\n\n <b>\n\n📤 Uploaded By : <a href="https://t.me/mksviplink">© MKS Channel</a></b>"""
        file_send = await client.send_video(
            Config.MUSIC_CHANNEL,
            video=open(file_stark, "rb"),
            duration=int(ytdl_data["duration"]),
            file_name=str(ytdl_data["title"]),
            caption=capy,
            supports_streaming=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('🔎 𝕍𝕚𝕕𝕖𝕠 𝕄𝕦𝕤𝕚𝕔 𝕊𝕖𝕒𝕣𝕔𝕙 𝔾𝕣𝕠𝕦𝕡 🔍', url="https://t.me/+XrP5-m5NLUIxYTU9")]
                ]
            )
        )
        await message.edit_text(
            text=req,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(f'📥 {file_name} 📥', url=file_send.link)],
                    [InlineKeyboardButton(f'📥 𝕄𝕦𝕤𝕚𝕔 𝔻𝕠𝕨𝕟𝕝𝕠𝕒𝕕 𝕃𝕚𝕟𝕜 📥', url=file_send.link)]
                ]
            )
        )
        for file in (file_stark,):
            if file and os.path.exists(file):
                os.remove(file)
    except Exception as e:
        await message.edit_text(f"**An error occurred. Please try again later.**\n**Error:** `{str(e)}`")

