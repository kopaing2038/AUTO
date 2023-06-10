import asyncio
import speedtest
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import Message, InlineKeyboardButton
import speedtest_cli 


SUDOERS = filters.user()


async def testspeed(m):
    try:
        result = await asyncio.to_thread(speedtest_cli.speedtest)
        return result
    except Exception as e:
        return str(e)

@Bot.on_message(filters.command(["speedtest"]) & ~filters.channel)
async def speedtest_function(bot: Bot, message):
    m = await message.reply_text("Running Speed test")
    result = await testspeed(m)
    download_speed = round(result.download / 1000000, 2)
    upload_speed = round(result.upload / 1000000, 2)
    output = f"""**Speedtest Results**

<u>**Speed:**</u>

**__Download Speed:__** {download_speed}  Mbps
**__Upload Speed:__** {upload_speed}  Mbps
    
<u>**Client:**</u>
**__ISP:__** {result.client['isp']}
**__Country:__** {result.client['country']}

<u>**Server:**</u>
**__Name:__** {result.server['name']}
**__Country:__** {result.server['country']}, {result.server['cc']}
**__Sponsor:__** {result.server['sponsor']}
**__Latency:__** {result.server['latency']}  
**__Ping:__** {result.ping}"""

    msg = await bot.send_photo(
        chat_id=message.chat.id, 
        photo=result.share(),
        caption=output
    )
    await m.delete()
