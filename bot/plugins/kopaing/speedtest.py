import asyncio
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import Message, InlineKeyboardButton
from speedtest import Speedtest  # Updated import statement
SUDOERS = filters.user()

@Bot.on_message(filters.command(["speedtest"]) & ~filters.channel)
async def speedtest_function(bot: Bot, message: Message):
    m = await message.reply_text("Running Speed test")
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    download_speed = result['download'] / 1000000
    upload_speed = result['upload'] / 1000000
    output = f"""**Speedtest Results**

<u>**Speed:**</u>

**__Download Speed:__** {download_speed:.2f} Mbps
**__Upload Speed:__** {upload_speed:.2f} Mbps
    
<u>**Client:**</u>
**__ISP:__** {message.from_user.username}
**__Country:__** {result['client']['country']}

<u>**Server:**</u>
**__Name:__** {result['server']['name']}
**__Country:__** {result['server']['country']}, {result['server']['cc']}
**__Sponsor:__** {result['server']['sponsor']}
**__Latency:__** {result['server']['latency']}  
**__Ping:__** {result['ping']}"""

    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=output
    )
    await m.delete()
