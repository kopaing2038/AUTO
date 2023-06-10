import asyncio
import speedtest_cli
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import Message, InlineKeyboardButton

SUDOERS = filters.user()

async def testspeed(m):
    try:
        m = await m.edit("Running Download SpeedTest")
        download_speed = speedtest_cli.download()
        m = await m.edit("Running Upload SpeedTest")
        upload_speed = speedtest_cli.upload()
        m = await m.edit("Sharing SpeedTest Results")
        result = speedtest_cli.results.dict()
    except Exception as e:
        return await m.edit(str(e))
    return result

@Bot.on_message(filters.command(["speedtest"]) & ~filters.channel)
async def speedtest_function(bot: Bot, message):
    m = await message.reply_text("Running Speed test")
    result = await testspeed(m)
    download_speed = result['download']['speed'] if isinstance(result['download'], dict) else result['download']
    upload_speed = result['upload']['speed'] if isinstance(result['upload'], dict) else result['upload']
    output = f"""**Speedtest Results**

<u>**Speed:**</u>

**__Download Speed:__** {download_speed}  Mbps
**__Upload Speed:__** {upload_speed}  Mbps
    
<u>**Client:**</u>
**__ISP:__** {result['client']['isp']}
**__Country:__** {result['client']['country']}

<u>**Server:**</u>
**__Name:__** {result['server']['name']}
**__Country:__** {result['server']['country']}, {result['server']['cc']}
**__Sponsor:__** {result['server']['sponsor']}
**__Latency:__** {result['server']['latency']}  
**__Ping:__** {result['ping']}"""

    msg = await bot.send_photo(
        chat_id=message.chat.id, 
        photo=result["share"], 
        caption=output
    )
    await m.delete()
