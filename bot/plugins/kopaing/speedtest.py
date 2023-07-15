import asyncio
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import InlineKeyboardButton
from speedtest_cli import Speedtest

SUDOERS = filters.user()

async def testspeed(m):
    try:
        await m.edit("Running SpeedTest")
        speedtester = Speedtest()
        speedtester.get_best_server()
        speedtester.download()
        speedtester.upload()
        result = speedtester.results.dict()
    except Exception as e:
        return await m.edit(str(e))
    return result

@Bot.on_message(filters.command(["speedtest"]) & ~filters.channel)
async def speedtest_function(bot: Bot, message):
    m = await message.reply_text("Running Speed test")
    result = await testspeed(m)
    if isinstance(result, dict):
        download_speed = result.get('download', 0) / 1000000
        upload_speed = result.get('upload', 0) / 1000000
        client_country = result.get('client', {}).get('country', '')
        server_name = result.get('server', {}).get('name', '')
        server_country = result.get('server', {}).get('country', '')
        server_cc = result.get('server', {}).get('cc', '')
        server_sponsor = result.get('server', {}).get('sponsor', '')
        server_latency = result.get('server', {}).get('latency', '')
        server_ping = result.get('ping', '')
    else:
        download_speed = 0
        upload_speed = 0
        client_country = ''
        server_name = ''
        server_country = ''
        server_cc = ''
        server_sponsor = ''
        server_latency = ''
        server_ping = ''

    output = f"""**Speedtest Results**

<u>**Speed:**</u>

**__Download Speed:__** {download_speed:.2f} Mbps
**__Upload Speed:__** {upload_speed:.2f} Mbps
    
<u>**Client:**</u>
**__ISP:__** {message.chat.username}
**__Country:__** {client_country}

<u>**Server:**</u>
**__Name:__** {server_name}
**__Country:__** {server_country}, {server_cc}
**__Sponsor:__** {server_sponsor}
**__Latency:__** {server_latency}  
**__Ping:__** {server_ping}"""

    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=output
    )
    await m.delete()
