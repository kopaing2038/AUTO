import random
import string
import asyncio
from typing import AsyncGenerator, Optional, Union
from pyrogram import Client, filters, enums
from pyrogram.errors import UserAlreadyParticipant, FloodWait
from bot.utils.logger import LOGGER
from bot import Bot 
from bot.clone_plugin.database.database import Database 
from bot.clone_plugin.plugins.auto_filter import recacher

db = Database()
logger = LOGGER(__name__)
VERIFY = {}

async def iter_history(
    client: Client,
    chat_id: int,
    limit: int,
    offset_id: int = 0,
) -> list:
    """Iterate over the message history of a chat.
    Parameters:
        client (``pyrogram.Client``): The Pyrogram client instance.
        chat_id (``int``):
            Unique identifier of the target chat.
        limit (``int``):
            Limits the number of messages to be retrieved.
        offset_id (``int``, *optional*):
            Identifier of the message to start from.
            Use a positive value to start from a specific message or a negative value to start from the most recent messages.
            Defaults to 0 (most recent messages).
    Returns:
        ``list``: A list of :obj:`~pyrogram.types.Message` objects in reverse order.
    """
    current_id = offset_id
    messages = []
    
    async for message in client.get_chat_history(chat_id, limit=limit, offset_id=current_id):
        messages.append(message)
    
    return messages[::-1]



@Client.on_message(filters.command(["add"]) & filters.group, group=1)
async def connect(bot: Bot, update):
    """
    A Function To Handle Incoming /add Command TO Connect A Chat With Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.get_chat_members(chat_id=chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("Invalid Username...!!!")
                return
            target = target_chat[1]
            
        elif not target_chat[1].startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("Invalid Chat Id...\nChat ID Should Be Something Like This: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Invalid Input...\nYou Should Specify Valid <code>chat_id(-100xxxxxxxxxx)</code> or <code>@username</code>")
        return
    
    # Exports invite link from target channel for user to join
    try:
        join_link = await bot.export_chat_invite_link(target)
        join_link = join_link.replace('+', 'joinchat/')
    except Exception as e:
        logger.exception(e, exc_info=True)
        await update.reply_text(f"Make Sure Im Admin At <code>{target}</code> And Have Permission For <i>Inviting Users via Link</i> And Try Again.....!!!\n\n<i><b>Error Logged:</b></i> <code>{e}</code>", parse_mode='html')
        return
    
    # Get information about the bot
    bot_info = await bot.get_me()
    
    try:
        c_chat = await bot.get_chat(target)
        channel_id = c_chat.id
        channel_name = c_chat.title
        
    except Exception as e:
        await update.reply_text("Encountered Some Issue..Please Check Logs..!!")
        raise e
        
        
    in_db = await db.in_db(chat_id, channel_id)
    
    if in_db:
        await update.reply_text("Channel Already In Db...!!!")
        return
    
    wait_msg = await update.reply_text("Please Wait Till I Add All Your Files From Channel To Db\n\n<i>This May Take 10 or 15 Mins Depending On Your No. Of Files In Channel.....</i>\n\nUntil Then Please Dont Sent Any Other Command Or This Operation May Be Interrupted....")
    
    try:
        mf = enums.MessagesFilter
        type_list = [mf.VIDEO, mf.DOCUMENT, mf.AUDIO]
        data = []
        skipCT = 0

        for typ in type_list:
            messages = await iter_history(bot, channel_id, limit=200)
            
            for message in messages:
                # Filter messages based on type
                if typ == mf.VIDEO and message.video:
                    file_id = message.video.file_id
                    file_name = message.video.file_name[0:-4]
                    file_caption = message.caption if message.caption else ""
                    file_size = message.video.file_size
                    file_type = "video"
                    
                elif typ == mf.AUDIO and message.audio:
                    file_id = message.audio.file_id
                    file_name = message.audio.file_name[0:-4]
                    file_caption = message.caption if message.caption else ""
                    file_size = message.audio.file_size
                    file_type = "audio"
                    
                elif typ == mf.DOCUMENT and message.document:
                    file_id = message.document.file_id
                    file_name = message.document.file_name[0:-4]
                    file_caption = message.caption if message.caption else ""
                    file_size = message.document.file_size
                    file_type = "document"
                    
                else:
                    continue  # Skip messages that don't match the desired type
                
                for i in ["_", "|", "-", "."]: # Work Around
                    try:
                        file_name = file_name.replace(i, " ")
                    except Exception:
                        pass
                    
                file_link = message.link
                group_id = chat_id
                unique_id = ''.join(
                    random.choice(
                        string.ascii_lowercase + 
                        string.ascii_uppercase + 
                        string.digits
                    ) for _ in range(15)
                )
                
                dicted = dict(
                    file_id=file_id, # Done
                    unique_id=unique_id,
                    file_name=file_name,
                    file_caption=file_caption,
                    file_size=file_size,
                    file_type=file_type,
                    file_link=file_link,
                    chat_id=channel_id,
                    group_id=group_id,
                )
                
                data.append(dicted)
            
            print(f"{skipCT} Files Been Skipped Due To File Name Been None..... #BlameTG")
    except Exception as e:
        await wait_msg.edit_text("Couldnt Fetch Files From Channel... Please look Into Logs For More Details")
        raise e
    
    await db.add_filters(data)
    await db.add_chat(chat_id, channel_id, channel_name)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text(f"Channel Was Successfully Added With <code>{len(data)}</code> Files..")


@Client.on_message(filters.command(["del"]) & filters.group, group=1)
async def disconnect(bot: Bot, update):
    """
    A Function To Handle Incoming /del Command TO Disconnect A Chat With A Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None

    target_chat = update.text.split(None, 1)
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.get_chat_members(chat_id=chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("Invalid Username...!!!")
                return
            target = target_chat[1]
            
        elif not target_chat.startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("Invalid Chat Id...\nChat ID Should Be Something Like This: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Invalid Input...\nYou Should Specify Valid chat_id(-100xxxxxxxxxx) or @username")
        return
    
    bot_info = await bot.get_me()
    bot_name = bot_info.first_name
    bot_id = bot_info.id
    
    try:
        channel_info = await bot.get_chat(target)
        channel_id = channel_info.id
    except Exception:
        await update.reply_text(f"My Bot [{bot_name}](tg://user?id={bot_id}) Couldnt Fetch Details Of `{target}` Make Sure Bot Is Not Banned There Or Add It Manually And Try Again....!!")
        return
    
    in_db = await db.in_db(chat_id, channel_id)
    
    if not in_db:
        await update.reply_text("This Channel Is Not Connected With The Group...")
        return
    
    wait_msg = await update.reply_text("Deleting All Files Of This Channel From DB....!!!\n\nPlease Be Patience...Dont Sent Another Command Until This Process Finishes..")
    
    await db.del_filters(chat_id, channel_id)
    await db.del_active(chat_id, channel_id)
    await db.del_chat(chat_id, channel_id)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text("Successfully Deleted All Files From DB....")


@Client.on_message(filters.command(["delall"]) & filters.group, group=1)
async def delall(bot: Bot, update):
    """
    A Function To Handle Incoming /delall Command TO Disconnect All Chats From A Group
    """
    chat_id=update.chat.id
    user_id = update.from_user.id if update.from_user else None
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.get_chat_members(chat_id=chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    await db.delete_all(chat_id)
    await recacher(chat_id, True, True, bot, update)
    
    await update.reply_text("Successfully Deleted All Connected Chats From This Group....")


@Client.on_message(filters.channel & (filters.video | filters.audio | filters.document), group=0)
async def new_files(bot: Bot, update):
    """
    A Function To Handle Incoming New Files In A Channel And Add Them To Respective Channels..
    """
    channel_id = update.chat.id
    
    # Using 'if elif' instead of 'or' to determine 'file_type'
    # Better Way? Make A PR
    
    try:
        if update.video: 
            file_type = "video" 
            file_id = update.video.file_id
            file_name = update.video.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""
            file_size = update.video.file_size

        elif update.audio:
            file_type = "audio"
            file_id = update.audio.file_id
            file_name = update.audio.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""
            file_size = update.audio.file_size

        elif update.document:
            file_type = "document"
            file_id = update.document.file_id
            file_name = update.document.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""
            file_size = update.document.file_size

        for i in ["_", "|", "-", "."]: # Work Around
            try:
                file_name = file_name.replace(i, " ")
            except Exception:
                pass
    except Exception as e:
        print(e)
        return
        
    
    file_link = update.link
    group_ids = await db.find_group_id(channel_id)
    unique_id = ''.join(
        random.choice(
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits
        ) for _ in range(15)
    )
    
    data = []
    
    if group_ids:
        for group_id in group_ids:
            data_packets = dict(
                    file_id=file_id, # File Id For Future Updates Maybe...
                    unique_id=unique_id,
                    file_name=file_name,
                    file_caption=file_caption,
                    file_size = file_size,
                    file_type=file_type,
                    file_link=file_link,
                    chat_id=channel_id,
                    group_id=group_id,
                )
            
            data.append(data_packets)
        await db.add_filters(data)
    return
