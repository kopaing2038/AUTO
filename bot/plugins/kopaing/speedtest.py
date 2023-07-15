import asyncio
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import Message, InlineKeyboardButton
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
async def speedtest_function(bot: Bot, message: Message):
    m = await message.reply_text("Running Speed test")
    result = await testspeed(m)
    if isinstance(result, dict):
        download_speed = result.get('download', 0) / 1000000
        upload_speed = result.get('upload', 0) / 1000000
    else:
        download_speed = 0
        upload_speed = 0

    output = f"""**Speedtest Results**

<u>**Speed:**</u>

**__Download Speed:__** {download_speed:.2f} Mbps
**__Upload Speed:__** {upload_speed:.2f} Mbps
    
<u>**Client:**</u>
**__ISP:__** {message.chat.username}
**__Country:__** {result.get('client', {}).get('country', '')}

<u>**Server:**</u>
**__Name:__** {result.get('server', {}).get('name', '')}
**__Country:__** {result.get('server', {}).get('country', '')}, {result.get('server', {}).get('cc', '')}
**__Sponsor:__** {result.get('server', {}).get('sponsor', '')}
**__Latency:__** {result.get('server', {}).get('latency', '')}  
**__Ping:__** {result.get('ping', '')}"""

    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=output
    )
    await m.delete()
