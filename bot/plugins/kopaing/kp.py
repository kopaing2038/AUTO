import asyncio
import random
import os
from time import time, sleep
from bot import Bot
from pyrogram import errors, filters, types, enums
from bot.config.config import Config
from bot.config.script import Script
from bot.plugins.kopaing.admin_check import admin_check, admin_fliter, extract_user
from bot.database import configDB as config_db

class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}

#@Bot.on_message(filters.new_chat_members & filters.group)		
async def save_group(bot, message):
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        if settings["WELCOME"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('WELCOME') is not None:
                    try:
                        await (temp.MELCOW['WELCOME']).delete()
                    except:
                        pass
                temp.MELCOW['WELCOME'] = await message.reply_photo(
                                                 photo=(Script.MELCOW_PHOTO),
                                                 caption=(Script.MELCOW_ENG.format(u.mention, message.chat.title)),
                                                 reply_markup=types.InlineKeyboardMarkup(
                                                                         [[
                                                                           types.InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=Script.GRP_LNK),
                                                                           types.InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=Script.CHNL_LNK)
                                                                        ],[
                                                                           types.InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/KOPAINGLAY15")
                                                                         ]]
                                                 ),
                                                 parse_mode=enums.ParseMode.HTML
                )
                
        #if settings["auto_delete"]:
            await asyncio.sleep(30)
            await (temp.MELCOW['WELCOME']).delete()
	

#-----------------------------------------------------------------------------------------------------------------------------	

@Bot.on_message(filters.command(["stickerid"]))
async def stickerid(bot, message):   
    if message.reply_to_message.sticker:
       await message.reply(f"**Sticker ID is**  \n `{message.reply_to_message.sticker.file_id}` \n \n ** Unique ID is ** \n\n`{message.reply_to_message.sticker.file_unique_id}`", quote=True)
    else: 
       await message.reply("Oops !! Not a sticker file")



#----------------------------------------------------------------------------------------    


@Bot.on_message(filters.command("ban"))
async def ban_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return 
    user_id, user_first_name = extract_user(message)
    try:
        await message.chat.ban_member(user_id=user_id)
    except Exception as error:
        await message.reply_text(str(error))                    
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(f"Someone else is dusting off..! \n{user_first_name} \nIs forbidden.")                              
        else:
            await message.reply_text(f"Someone else is dusting off..! \n<a href='tg://user?id={user_id}'>{user_first_name}</a> Is forbidden")                      
            

@Bot.on_message(filters.command("tban"))
async def temp_ban_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return
    if not len(message.command) > 1:
        return
    user_id, user_first_name = extract_user(message)
    until_date_val = extract_time(message.command[1])
    if until_date_val is None:
        return await message.reply_text(text=f"Invalid time type specified. \nExpected m, h, or d, Got it: {message.command[1][-1]}")   
    try:
        await message.chat.ban_member(user_id=user_id, until_date=until_date_val)            
    except Exception as error:
        await message.reply_text(str(error))
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(f"Someone else is dusting off..!\n{user_first_name}\nbanned for {message.command[1]}!")
        else:
            await message.reply_text(f"Someone else is dusting off..!\n<a href='tg://user?id={user_id}'>Lavane</a>\n banned for {message.command[1]}!")
                
                
                
#--------------------------umte----unban------------- 

@Bot.on_message(filters.command(["unban", "unmute"]))
async def un_ban_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return
    user_id, user_first_name = extract_user(message)
    try:
        await message.chat.unban_member(user_id=user_id)
    except Exception as error:
        await message.reply_text(str(error))
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "Okay, changed ... now "
                f"{user_first_name} To "
                " You can join the group!"
            )
        else:
            await message.reply_text(
                "Okay, changed ... now "
                f"<a href='tg://user?id={user_id}'>"
                f"{user_first_name}"
                "</a> To "
                " You can join the group!"
            )
            
                
@Bot.on_message(filters.command("mute"))
async def mute_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return
    user_id, user_first_name = extract_user(message)
    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            )
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "👍🏻 "
                f"{user_first_name}"
                " Lavender's mouth is shut! 🤐"
            )
        else:
            await message.reply_text(
                "👍🏻 "
                f"<a href='tg://user?id={user_id}'>"
                "Of lavender"
                "</a>"
                " The mouth is closed! 🤐"
            )


@Bot.on_message(filters.command("tmute"))
async def temp_mute_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    if not len(message.command) > 1:
        return

    user_id, user_first_name = extract_user(message)

    until_date_val = extract_time(message.command[1])
    if until_date_val is None:
        await message.reply_text(
            (
                "Invalid time type specified. "
                "Expected m, h, or d, Got it: {}"
            ).format(
                message.command[1][-1]
            )
        )
        return

    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            ),
            until_date=until_date_val
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "Be quiet for a while! 😠"
                f"{user_first_name}"
                f" muted for {message.command[1]}!"
            )
        else:
            await message.reply_text(
                "Be quiet for a while! 😠"
                f"<a href='tg://user?id={user_id}'>"
                "Of lavender"
                "</a>"
                " Mouth "
                f" muted for {message.command[1]}!"
            )
    
#-------------------------------------------------kick-------------------------    
CREATOR_REQUIRED = """❗<b>You have To Be The Group Creator To Do That.</b>"""
      
INPUT_REQUIRED = "❗ **Arguments Required**"
      
KICKED = """✔️ Successfully Kicked {} Members According To The Arguments Provided."""
      
START_KICK = """🚮 Removing Inactive Members This May Take A While..."""
      
ADMIN_REQUIRED = """❗<b>I will not go where I am not made Admin Bii..Add Me Again with all admin rights.</b>"""
      
DKICK = """✔️ Kicked {} Deleted Accounts Successfully."""
      
FETCHING_INFO = """<b>Let's get rid of everything now...</b>"""

@Bot.on_message(filters.group & filters.command('inkick'))
def inkick(client, message):
  user = client.get_chat_member(message.chat.id, message.from_user.id)
  if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
    if len(message.command) > 1:
      input_str = message.command
      sent_message = message.reply_text(START_KICK)
      sleep(20)
      sent_message.delete()
      message.delete()
      count = 0
      for member in client.get_chat_members(message.chat.id):
        if member.user.status in input_str and not member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
          try:
            client.ban_chat_member(message.chat.id, member.user.id, int(time() + 45))
            count += 1
            sleep(1)
          except (ChatAdminRequired, UserAdminInvalid):
            sent_message.edit(ADMIN_REQUIRED)
            client.leave_chat(message.chat.id)
            break
          except FloodWait as e:
            sleep(e.x)
      try:
        sent_message.edit(KICKED.format(count))
      except ChatWriteForbidden:
        pass
    else:
      message.reply_text(INPUT_REQUIRED)
  else:
    sent_message = message.reply_text(CREATOR_REQUIRED)
    sleep(5)
    sent_message.delete()
    message.delete()


@Bot.on_message(filters.group & filters.command('dkick'))
def dkick(client, message):
  user = client.get_chat_member(message.chat.id, message.from_user.id)
  if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
    sent_message = message.reply_text(START_KICK)
    sleep(20)
    sent_message.delete()
    message.delete()
    count = 0
    for member in client.get_chat_members(message.chat.id):
      if member.user.is_deleted and not member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        try:
          client.ban_chat_member(message.chat.id, member.user.id, int(time() + 45))
          count += 1
          sleep(1)
        except (ChatAdminRequired, UserAdminInvalid):
          sent_message.edit(ADMIN_REQUIRED)
          client.leave_chat(message.chat.id)
          break
        except FloodWait as e:
          sleep(e.x)
    try:
      sent_message.edit(DKICK.format(count))
    except ChatWriteForbidden:
      pass
  else:
    sent_message = message.reply_text(CREATOR_REQUIRED)
    sleep(5)
    sent_message.delete()
    message.delete()

  
@Bot.on_message((filters.channel | filters.group) & filters.command('instatus'))
def instatus(client, message):
    sent_message = message.reply_text("🔁 Processing.....")
    recently = 0
    within_week = 0
    within_month = 0
    long_time_ago = 0
    deleted_acc = 0
    uncached = 0
    bot = 0
    for member in client.get_chat_members(message.chat.id, limit=int(10000)):
      user = member.user
      if user.is_deleted:
        deleted_acc += 1
      elif user.is_bot:
        bot += 1
      elif user.status == enums.UserStatus.RECENTLY:
        recently += 1
      elif user.status == enums.UserStatus.LAST_WEEK:
        within_week += 1
      elif user.status == enums.UserStatus.LAST_MONTH:
        within_month += 1
      elif user.status == enums.UserStatus.LONG_AGO:
        long_time_ago += 1
      else:
        uncached += 1

    chat_type = message.chat.type
    if chat_type == enums.ChatType.CHANNEL:
         sent_message.edit(f"{message.chat.title}\nChat Member Status\n\nRecently - {recently}\nWithin Week - {within_week}\nWithin Month - {within_month}\nLong Time Ago - {long_time_ago}\n\nDeleted Account - {deleted_acc}\nBot - {bot}\nUnCached - {uncached}")            
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        user = client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER, Config.ADMINS):
            sent_message.edit(f"{message.chat.title}\nChat Member Status\n\nRecently - {recently}\nWithin Week - {within_week}\nWithin Month - {within_month}\nLong Time Ago - {long_time_ago}\n\nDeleted Account - {deleted_acc}\nBot - {bot}\nUnCached - {uncached}")
        else:
            sent_message.edit("you are not administrator in this chat")
