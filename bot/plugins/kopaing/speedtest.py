import asyncio
import speedtest_cli
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import Message, InlineKeyboardButton

SUDOERS = filters.user()

async def testspeed(m):
    try:
        m = await m.edit("Running SpeedTest")
        result = speedtest_cli.speedtest()
    except Exception as e:
        return await m.edit(str(e))
    return result

@Bot.on_message(filters.command(["speedtest"]) & ~filters.channel)
async def speedtest_function(bot: Bot, message):
    m = await message.reply_text("Running Speed test")
    result = await testspeed(m)
    download_speed = result.download / 1000000
    upload_speed = result.upload / 1000000
    output = f"""**Speedtest Results**

<u>**Speed:**</u>

**__Download Speed:__** {download_speed:.2f} Mbps
**__Upload Speed:__** {upload_speed:.2f} Mbps
    
<u>**Client:**</u>
**__ISP:__** {result.client['isp']}
**__Country:__** {result.client['country']}

<u>**Server:**</u>
**__Name:__** {result.server['name']}
**__Country:__** {result.server['country']}, {result.server['cc']}
**__Sponsor:__** {result.server['sponsor']}
**__Latency:__** {result.server['latency']}  
**__Ping:__** {result.server['ping']}"""

    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=output
    )
    await m.delete()

    
