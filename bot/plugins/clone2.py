import os
import re
import time
import asyncio
import threading
import pyrogram
from pyrogram import *
from pyrogram.types import *
from pyromod import listen
from bot.config.config import Config
from bot.database.clone_db import add_stext, get_stext, add_bot, get_bot, get_all_bot
#from utils import cancel


async def cancel(self):
    self.stopEvent = threading.Event()
    self.stopEvent.set()
    
@Client.on_message(filters.private & filters.command("clonebot") & ~filters.bot, group=3)
async def clone(bot:Client, msg:Message):
    chat = msg.chat
    btn = [[
        InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data="stop")
    ]]
    post:Message = await bot.ask(chat_id=msg.from_user.id, text = "Oᴋᴀʏ Nᴏᴡ Sᴇɴᴛ Mᴇ Bᴏᴛ Tᴏᴋᴇɴ", reply_markup=InlineKeyboardMarkup(btn), timeout = 360)
    phone = post.text
    cmd = msg.command
    bot_id1 = post.text.split(":")[0]
    try:
        text1 = await msg.reply("<b>Tʀʏɪɴɢ Tᴏ Cᴏɴɴᴇᴄᴛ Yᴏᴜʀ Bᴏᴛ...</b>")
                  
        client = Client(bot_id1 + "_0", Config.API_ID, Config.API_HASH, bot_token=phone, plugins={"root": "bot/plugins"})
        await client.start()
        idle()
        user = await client.get_me()
        user_mention = msg.from_user.mention
        user_id = msg.from_user.id
        add_bot(user_id, phone)
        await bot.send_message(chat_id=Config.LOG_CHANNEL, text=f"A New Bot Has Be Created :\n\nCreator : {user_mention}\nBot : @{user.username}")
        await text1.edit(f"<b>Hᴇʏ Bʀᴏ Yᴏᴜ Bᴏᴛ Hᴀs Bᴇᴇɴ Sᴛᴀʀᴛᴇᴅ As @{user.username} ✅ \n\nAᴅᴅ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ Aɴᴅ Eɴᴊᴏʏ.. 📣</b>")
     
    except Exception as e:
        
        await text1.edit(f"**❌ Eʀʀᴏʀ :**\n\n`{str(e)}`\n\nIғ Hᴀᴠᴇ Aɴʏ Dᴏᴜʙᴛ Asᴋ Iɴ Sᴜᴘᴘᴏʀᴛ ❗")
        
@Client.on_message(filters.private & filters.command(["clonemybots"]))
async def mybots(client, message):
    user_id=message.from_user.id
    tok=await get_bot(user_id)
    bot_ids=tok.split(":")[0]
    
    if bot_ids is None:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )
        return
    buttons = []
    for bot_id in bot_ids:
        try:
            bot = bot_id
            
            buttons.append(
                [
             
                    InlineKeyboardButton(
                        text=f"<a href=tg://user?id={bot}>.</a>", callback_data=f"botcb:{bot_id}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply(
            text="Yᴏᴜʀ Cᴏɴɴᴇᴄᴛᴇᴅ Gʀᴏᴜᴘ Dᴇᴛᴀɪʟs Rᴇ Gɪᴠᴇɴ Bᴇʟᴏᴡ :\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply(
            'Hey First Create A Bot Then Try Again ):',
            quote=True
        )
@Client.on_callback_query()
async def callback(client:Client, query:CallbackQuery):
    
    if "botcb" in query.data:
        await query.answer()

        bot_id = query.data.split(":")[1]

        hr = bot_id
        title = hr
        user_id = query.from_user.id

      

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Sᴛᴀʀᴛ Tᴇxᴛ", callback_data = f"if_text:{bot_id}"),
            InlineKeyboardButton("Dᴇʟᴇᴛᴇ", callback_data=f"deletebcb:{bot_id}")],
            [InlineKeyboardButton("Bᴀᴄᴋ", callback_data="backbcb")]
        ])

        await query.message.edit_text(
            f"Bot Name :- **{title}**",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('Hᴀᴘᴘʏ Aʟʟᴇ Dᴀ')
    
    elif query.data == "stop":
        await cancel()
        ml = await query.message.edit("Cᴀɴᴄᴇʟᴇᴅ...✅")
        
        await asyncio.sleep(10)
        await ml.delete()
        
    elif "deletebcb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        bot_id = query.data.split(":")[1]

        delcon = await delete_bot(str(user_id), str(bot_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    
    elif query.data == "backbcb":
        
        await query.answer()
        user_id = query.from_user.id
        test=await get_bot(user_id)
        bot_ids=test.message.split(":")[0]
        
        if bot_ids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
        buttons = []
        for bot_id in bot_ids:
            try:
                ttl = bot_id
                title = ttl
                
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}", callback_data=f"botcb:{bot_id}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await query.message.edit(
                "Hello"
            )
            
    elif "start_text" in query.data:
        bot_id = query.data.split(":")[1]
        post:Message = await client.ask(chat_id = query.from_user.id, text="<i>Okay Now Sent Text To Set Your Start Text 🙌</i>", timeout=360)
        st_text = post.text
        try:
            st2 = await query.message.reply("<i>Saving You Text...</i>")
            set_pic = await add_stext(bot_id, st_text)
            await st2.edit(
                "<i>Successfully Your Start Text Was Updated</i>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('🔙 Bᴀᴄᴋ', callback_data=f"botcb:{bot_id}")
                        ]
                    ]
                )
            )
        except Exception as e:
            await st2.delete()
            await query.message.reply(f"**❌ Eʀʀᴏʀ :**\n\n`{str(e)}`\n\nIғ Hᴀᴠᴇ Aɴʏ Dᴏᴜʙᴛ Asᴋ Iɴ Sᴜᴘᴘᴏʀᴛ ❗")
    
    elif "if_text" in query.data:
        bot_id = query.data.split(":")[1]
        await query.answer()
        await query.message.edit(
            "<u><b>Start Text</u></b>\n\n<i>• You Can Add Custom Start Text For Your Bot...</i>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("➕ Aᴅᴅ Nᴇᴡ Sᴛᴀʀᴛ Tᴇxᴛ ➕", callback_data=f"start_text:{bot_id}")
                    ],
                    [
                        InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data=f"botcb:{bot_id}"),
                        InlineKeyboardButton("♻️ Rᴇsᴇᴛ", callback_data=f"resetst:{bot_id}")
                    ]
                ]
            ),
            parse_mode=enums.ParseMode.HTML
        )
                                                                                                                                                                                                                                   

  
async def clone_start():
      print("Loading Clone bots")
      string = await get_all_bot()
      try:
          cloneboy = Client("c_string", api_id=API_ID, api_hash=API_HASH, bot_token=string)
          await cloneboy.start()
          user = await cloneboy.get_me()
      except BaseException as eb:
          print(eb)
      print(f"Total Client = {len(string)} User")
      await idle()


          












