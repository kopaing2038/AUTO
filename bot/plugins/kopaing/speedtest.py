import asyncio
import speedtest
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import Message, InlineKeyboardButton

SUDOERS = filters.user()

def testspeed(m):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = m.edit("Running Download SpeedTest")
        test.download()
        m = m.edit("Running Upload SpeedTest")
        test.upload()
        test.results.share()
        result = test.results.dict()
        m = m.edit("Sharing SpeedTest Results")
    except Exception as e:
        return m.edit(e)
    return result

@Bot.on_message(filters.command(["speedtest"]) & ~filters.channel)
async def speedtest_function(bot: Bot, message):
    m = await message.reply_text("Running Speed test")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m)
    speedtester = speedtest.Speedtest()
    speedtester.get_best_server()
    download_speed = result['download'] if isinstance(result['download'], float) else result['download'].get('speed', '-')
    upload_speed = result['upload'] if isinstance(result['upload'], float) else result['upload'].get('speed', '-')
    download_speed = round(speedtester.download() / 1000000, 2)
    upload_speed = round(speedtester.upload() / 1000000, 2)
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
