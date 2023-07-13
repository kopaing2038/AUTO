import re
import logging
import asyncio
import pymongo
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from ..config import Config
from ..database import configDB as config_db

from pyrogram import enums, errors, filters, types



from pymongo.errors import DuplicateKeyError
from marshmallow.exceptions import ValidationError


mongo_client = MongoClient(Config.DATABASE_URI)
mongo_db = mongo_client["cloned_bots"]

myclient = pymongo.MongoClient(Config.DATABASE_URI)
mydb = myclient[Config.SESSION_NAME]

logging.basicConfig(level=logging.ERROR)



#@Client.on_message((filters.regex(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}')) & filters.private)
async def on_clone(self, message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', message.text, re.IGNORECASE)
        bot_token = bot_token[0] if bot_token else None
        bot_id = re.findall(r'\d[0-9]{8,10}', message.text)

        if not str(message.forward_from.id) != "93372553":
            msg = await message.reply_text(f" <code>{bot_token}</code>\n\n ♻️𝙰𝚖 𝚃𝚛𝚢𝚒𝚗𝚐 𝚃𝚘 𝙲𝚕𝚘𝚗𝚎 𝚄𝚛 𝙱𝚘𝚝 𝚆𝚊𝚒𝚝 𝙰 𝙼𝚒𝚗𝚞𝚝𝚎♻️")
            try:
                ai = Client(
                    f"{bot_token}", Config.API_ID, Config.API_HASH,
                    bot_token=bot_token,
                    plugins={"root": "bot/clone_plugins"},
                )
                await ai.start()
                bot = await ai.get_me()
                details = {
                    'bot_id': bot.id,
                    'is_bot': True,
                    'user_id': user_id,
                    'name': bot.first_name,
                    'token': bot_token,
                    'username': bot.username
                }
                mongo_db.bots.insert_one(details)
                clonedme.ME = bot.id
                clonedme.U_NAME = bot.username
                clonedme.B_NAME = bot.first_name
                await msg.edit_text(f"𝚂𝚞𝚌𝚌𝚎𝚜𝚏𝚞𝚕𝚕𝚢 𝙲𝚕𝚘𝚗𝚎𝚍 𝚢𝚘𝚞𝚛 @{bot.username} .\n\n⚠️ <u>𝙳𝚘 𝙽𝚘𝚝 𝚂𝚎𝚗𝚍 𝚃𝚘 𝙰𝚗𝚢 𝙾𝚗𝚎</u> 𝚃𝚑𝚎 𝙼𝚎𝚜𝚜𝚊𝚐𝚎 𝚆𝚒𝚝𝚑 <u>𝚃𝚑𝚎 𝚃𝚘𝚔𝚎𝚗</u> 𝙾𝚏 𝚃𝚑𝚎 𝙱𝚘𝚝, 𝚆𝚑𝚘 𝙷𝚊𝚜 𝙸𝚝 𝙲𝚊𝚗 𝙲𝚘𝚗𝚝𝚛𝚘𝚕 𝚈𝚘𝚞𝚛 𝙱𝚘𝚝!\n<i>𝙸𝚏 𝚈𝚘𝚞 𝚃𝚑𝚒𝚗𝚔 𝚂𝚘𝚖𝚎𝚘𝚗𝚎 𝙵𝚘𝚞𝚗𝚍 𝙾𝚞𝚝 𝙰𝚋𝚘𝚞𝚝 𝚈𝚘𝚞𝚛 𝙱𝚘𝚝 𝚃𝚘𝚔𝚎𝚗, 𝙶𝚘 𝚃𝚘 @Botfather, 𝚄𝚜𝚎 /revoke 𝙰𝚗𝚍 𝚃𝚑𝚎𝚗 𝚂𝚎𝚕𝚎𝚌𝚝 @{bot.username}</i>")
            except BaseException as e:
                logging.exception("Error while cloning bot.")
                await msg.edit_text(f"⚠️ <b>𝙱𝙾𝚃 𝙴𝚁𝚁𝙾𝚁:</b>\n\n<code>{e}</code>\n\n❔ 𝙵𝚘𝚛𝚠𝚊𝚛𝚍 𝚃𝚑𝚒𝚜 𝙼𝚎𝚜𝚜𝚊𝚐𝚎 𝚃𝚘 @Lallu_tgs 𝚃𝚘 𝙱𝚎 𝙵𝚒𝚡𝚎𝚍.")
    except Exception as e:
        logging.exception("Error while handling message.")

async def get_bot():
    await ai.start()
    crazy = await ai.get_me()
    await ai.stop()
    return crazy

#@Client.on_message(filters.command("clone2") & filters.private)
async def ononv_clone(client, message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        # Extract bot_token and bot_id from the message text using regex
        bot_token = re.findall(r'\d{8,10}:[0-9A-Za-z_-]{35}', message.text)
        bot_token = bot_token[0] if bot_token else None
        bot_ids = re.findall(r'\d{8,10}', message.text)

        if not bot_token:
            await message.reply_text("Please provide a valid bot token to clone.")
            return

        if not bot_ids:
            await message.reply_text("Unable to find the bot ID.")
            return

        bot_id = bot_ids[0]  # Extract the first bot ID from the list

        msg = await message.reply_text(f"Cloning your bot with token: {bot_token}")
        if bot_ids:
            await savefiles(bot_id)
        try:
            ai = Client(
                f"{bot_token}", Config.API_ID, Config.API_HASH,
                bot_token=bot_token,
                plugins={"root": "bot/clone_bot"},
            )
            await ai.start()
            bot = await ai.get_me()
 
            details = {
                'bot_id': bot.id,
                'is_bot': True,
                'user_id': user_id,
                'name': bot.first_name,
                'token': bot_token,
                'username': bot.username
            }
            mongo_db.bots.insert_one(details)

            settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
            settings["COLLECTION_NAME4"] = bot_id
            await config_db.update_config(f"SETTINGS_{message.chat.id}", settings)
            await message.reply(f"Collection name set to: {bot_id}")

            await add_bot(user_id, bot_id)

            clonedme.ME = bot.id
            clonedme.U_NAME = bot.username
            clonedme.B_NAME = bot.first_name
            await msg.edit_text(f"Successfully cloned your bot: @{bot.username}.\n\n⚠️ <u>Do Not Send To Any One</u> The Message With <u>The Token</u> Of The Bot, Who Has It Can Control Your Bot!\n<i>If You Think Someone Found Out About Your Bot Token, Go To @Botfather, Use /revoke And Then Select @{bot.username}</i>")
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await msg.edit_text(f"⚠️ <b>BOT ERROR:</b>\n\n<code>{e}</code>\n\nPlease forward this message to @Lallu_tgs for help.")
    except Exception as e:
        logging.exception("Error while handling message.")



@Client.on_message(filters.command("clone") & filters.private)
async def ono2_clone(client, message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        # Extract bot_token and bot_id from the message text using regex
        bot_token = re.findall(r'\d{8,10}:[0-9A-Za-z_-]{35}', message.text)
        bot_token = bot_token[0] if bot_token else None
        bot_id = re.findall(r'\d{8,10}', message.text)

        if not bot_token:
            await message.reply_text("Please provide a valid bot token to clone.")
            return

        if not bot_id:
            await message.reply_text("Unable to find the bot ID.")
            return

        msg = await message.reply_text(f"Cloning your bot with token: {bot_token}")

        try:
            cloneboy = Client(
                "clone_session", api_id=Config.API_ID, api_hash=Config.API_HASH,
                bot_token=bot_token,
                plugins={"root": "bot/plugins"},
            )
            await cloneboy.start()
            bot = await cloneboy.get_me()

            details = {
                'bot_id': bot.id,
                'is_bot': True,
                'user_id': user_id,
                'name': bot.first_name,
                'token': bot_token,
                'username': bot.username
            }
            mongo_db.bots.insert_one(details)
            clonedme.ME = bot.id
            clonedme.U_NAME = bot.username
            clonedme.B_NAME = bot.first_name
            await msg.edit_text(f"Successfully cloned your bot: @{bot.username}.\n\n⚠️ <u>Do Not Send To Anyone</u> The Message With <u>The Token</u> Of The Bot. Whoever Has It Can Control Your Bot!\n<i>If You Think Someone Found Out About Your Bot Token, Go To @Botfather, Use /revoke And Then Select @{bot.username}</i>")
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await msg.edit_text(f"⚠️ <b>BOT ERROR:</b>\n\n<code>{e}</code>\n\nPlease forward this message to @Lallu_tgs for help.")
    except Exception as e:
        logging.exception("Error while handling message.")

@Client.on_message(filters.command("clonedbots") & filters.private)
async def cloned_bots_list(client, message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        bots = list(mongo_db.bots.find({'user_id': user_id}))

        if len(bots) == 0:
            await message.reply_text("You haven't cloned any bots yet.")
            return

        text = "<b>Your cloned bots:</b>\n\n"

        for bot in bots:
            text += f"- @{bot['username']} ({bot['name']})\n"
            text += f"  Bot ID: {bot['bot_id']}\n"
            text += f"  Token: {bot['token']}\n"
            text += "\n"

        await message.reply_text(text)
    except Exception as e:
        logging.exception("Error while handling cloned bots command.")

@Client.on_message(filters.command('cloned_count') & filters.private)
async def cloned_count(client, message):
    user_id = message.from_user.id
    if user_id not in Config.ADMINS:
        await message.reply_text("You are not authorized to use this command.")
        return
    cloned_bots = list(mongo_db.bots.find())
    count = len(cloned_bots)
    if count == 0:
        await message.reply_text("No bots have been cloned yet.")
    else:
        bot_usernames = [f"@{bot['username']}" for bot in cloned_bots]
        bot_usernames_text = '\n'.join(bot_usernames)
        await message.reply_text(f"{count} bots have been cloned:\n\n{bot_usernames_text}")

@Client.on_message(filters.command(["removebot"]) & filters.user(Config.ADMINS))
async def remove_bot(client: Client, message: Message):
    try:
        bot_username = message.text.split(" ", maxsplit=1)[1].strip()
    except IndexError:
        await message.reply_text("Please provide a bot username.")
        return

    bot_data = mongo_db.bots.find_one_and_delete({"username": bot_username})

    if bot_data:
        bot_id = bot_data["bot_id"]
        cloned_sessions = mongo_db.cloned_sessions.find({"bot_id": bot_id})
        if cloned_sessions.count() > 0:
            for session in cloned_sessions:
                await session.stop()
                mongo_db.cloned_sessions.delete_one({"_id": session["_id"]})
        await message.reply_text(f"Bot @{bot_username} removed successfully.")
    else:
        await message.reply_text(f"Bot @{bot_username} is not in the cloned bots list.")

@Client.on_message(filters.command("deletecloned") & filters.private)
async def delete_cloned_bot(client, message):
    try:
        bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', message.text, re.IGNORECASE)
        bot_token = bot_token[0] if bot_token else None
        bot_id = re.findall(r'\d[0-9]{8,10}', message.text)

        cloned_bot = mongo_collection.find_one({"token": bot_token})
        if cloned_bot:
            mongo_collection.delete_one({"token": bot_token})
            await message.reply_text("The cloned bot has been removed from the list and its details have been removed from the database.")
        else:
            await message.reply_text("The bot token provided is not in the cloned list.")
    except Exception as e:
        logging.exception("Error while deleting cloned bot.")
        await message.reply_text("An error occurred while deleting the cloned bot.")

async def clone_start():
    print("Starting Clone bots")
    try:
        cloneboy = Client(
            "clone_session", api_id=Config.API_ID, api_hash=Config.API_HASH,
            bot_token="YOUR_BOT_TOKEN",
            plugins={"root": "bot/plugins"},
        )
        await cloneboy.start()
        bot = await cloneboy.get_me()
        details = {
            'bot_id': bot.id,
            'is_bot': True,
            'name': bot.first_name,
            'username': bot.username
        }
        mongo_db.bots.insert_one(details)
        while True:
            await asyncio.sleep(1)  # Keeps the bot running without blocking the event loop
    except BaseException as e:
        logging.exception("Error while cloning bot.")
        print(f"Error while cloning bot: {e}")

async def clone_stop():
    print("Stopping Clone bots")
    try:
        cloneboy = Client("clone_session", api_id=Config.API_ID, api_hash=Config.API_HASH)
        await cloneboy.connect()
        bot = await cloneboy.get_me()
        await cloneboy.log_out()
        details = {
            'bot_id': bot.id,
            'is_bot': True,
            'name': bot.first_name,
            'username': bot.username
        }
        mongo_db.bots.delete_one(details)
        print("Clone bots stopped successfully")
    except BaseException as e:
        logging.exception("Error while stopping clone bot.")
        print(f"Error while stopping clone bot: {e}")


async def restart_bots():
    logging.info("Restarting all bots........")
    bots = list(mongo_db.bots.find())
    for bot in bots:
        bot_token = bot['token']
        try:
            ai = Client(
                f"{bot_token}", Config.API_ID, Config.API_HASH,
                bot_token=bot_token,
                plugins={"root": "bot/plugins"},
            )
            await ai.start()
            logging.info(f"Bot @{ai.username} restarted.")
        except Exception as e:
            logging.exception(f"Error while restarting bot with token {bot_token}: {e}")
    #logging.info("All bots restarted.")

@Client.on_message(filters.command("restartall") & filters.user(Config.ADMINS))
async def on_restart_all_bots(client: Client, message: Message):
    logging.info("Received restart command.")
    await message.reply_text("ʀᴇꜱᴛᴀʀᴛɪɴɢ ᴀʟʟ ʙᴏᴛꜱ....🏹")
    await restart_bots()
    await message.reply_text("ᴀʟʟ ʙᴏᴛꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇꜱᴛᴀʀᴛᴇᴅ 🔋")  
