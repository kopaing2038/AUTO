import asyncio
from pyrogram import filters, Client
from bot import Bot
from pyrogram.types import Message, InlineKeyboardButton
from speedtest_cli import Speedtest

SUDOERS = filters.user()

@Bot.on_message(filters.command(["speedtest"]) & ~filters.channel)
async def speedtest_function(bot: Bot, message: Message):
    m = await message.reply_text("Running Speed test")
    test = Speedtest()

    # Fetch available servers
    test.get_servers()
    servers = test.servers

    # Choose a server manually
    server = servers[0]  # Replace 0 with the desired index of the server

    try:
        # Test latency with the selected server
        test.get_best_server(servers=[server])

        # Run download and upload tests
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
    except speedtest.SpeedtestBestServerFailure as e:
        # Handle the case where the best server couldn't be determined
        error_message = "Unable to determine the best server. Please try again later."
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=error_message
        )

    await m.delete()
