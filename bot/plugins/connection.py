from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from bot.config.config import Config
import logging
import random
import pyrogram
from bot import Bot
from bot.plugins.autofilter import ch1_give_filter
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def add_connection_handler(client, message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply(f"You are an anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except ValueError:
            await message.reply_text(
                "<b>Enter in correct format!</b>\n\n"
                "<code>/connect groupid</code>\n\n"
                "<i>Get your Group id by adding this bot to your group and use  <code>/id</code></i>",
                quote=True
            )
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, user_id)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and user_id not in Config.ADMINS
        ):
            await message.reply_text("You should be an admin in the given group!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, make sure I'm present in your group!!",
            quote=True,
        )
        return

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title

            add_con = await add_connection(str(group_id), str(user_id))
            if add_con:
                await message.reply_text(
                    f"Successfully connected to **{title}**\nNow manage your group from my PM!",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        user_id,
                        f"Connected to **{title}**!",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text(
                    "You're already connected to this chat!",
                    quote=True
                )
        else:
            await message.reply_text("Add me as an admin in the group", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('Some error occurred! Try again later.', quote=True)
        return


@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def delete_connection_handler(client, message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply(f"You are an anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text("Run /connections to view or disconnect from groups!", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, user_id)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(user_id) not in Config.ADMINS
        ):
            return

        del_con = await delete_connection(str(user_id), str(group_id))
        if del_con:
            await message.reply_text("Successfully disconnected from this chat", quote=True)
        else:
            await message.reply_text("This chat isn't connected to me!\nDo /connect to connect.", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections_handler(client, message):
    user_id = message.from_user.id

    group_ids = await all_connections(str(user_id))
    if group_ids is None:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )
        return

    buttons = []
    for group_id in group_ids:
        try:
            ttl = await client.get_chat(int(group_id))
            title = ttl.title
            active = await if_active(str(user_id), str(group_id))
            act = " - ACTIVE" if active else ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{group_id}:{act}"
                    )
                ]
            )
        except Exception:
            pass

    if buttons:
        await message.reply_text(
            "Your connected group details:\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )

@Client.on_message(filters.private & filters.text & filters.incoming)
async def psvv_filter(bot: Client, msg):
    content = msg.text
    user = msg.from_user.first_name
    user_id = msg.from_user.id
    
    if content.startswith("/") or content.startswith("#"):
        return  # ignore commands and hashtags
   
    if user_id in Config.ADMINS:
        # If the message was sent by an admin, send their reply to the user who sent the original message
        if msg.reply_to_message:
            user_msg = msg.reply_to_message.text
            user_id = msg.reply_to_message.from_msg.id
            
            await bot.send_message(chat_id=msg.reply_to_message.from_msg.id, text=f"Admin replied: {user_msg}")
        return	


    await bot.send_message(
        chat_id=Config.LOG_CHANNEL,
        text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\n@{bot.me.username}\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>")
	
    #if not await botcheck_fsub(bot, msg):
        #return	
   
    settings = await config_db.get_settings(f"SETTINGS_{msg.chat.id}")
    if settings['PM_FILTER']:
        kd = await ch1_give_filter(bot, msg) 
        return
    
    btn = [
        [InlineKeyboardButton("Group 1", url="https://t.me/MKS_REQUESTGROUP"),
	InlineKeyboardButton("Group 2", url="https://t.me/+z5lhEpxP5Go4MWM1")],
        [InlineKeyboardButton("All Link ", url="https://t.me/Movie_Zone_KP/3")],
    ]
    btn2 = [
        [InlineKeyboardButton("Group 3", url="https://t.me/Movie_Group_MMSUB"),
	InlineKeyboardButton("Group 4", url="https://t.me/+cHMLAeatqKdlNGVl")],
        [InlineKeyboardButton("All Link ", url="https://t.me/Movie_Zone_KP/3")],
    ]
    
    bt = [ 
        {"caption": f"""Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴍʏ ᴍᴏᴅᴇʀᴀᴛᴏʀs!
===========================
Can't find movies here. Search in the group given below    
@Movie_Group_MMSUB""", 
         "reply_markup": InlineKeyboardMarkup(btn)},
        {"caption": f"""သင့်စာကို မင်မင်ထံ ပေးပို့လိုက်ပါပြီး။ !
	
===========================
ဤနေရာတွေ ဇာတ်ကားများရှာမရပါ အောက်တွင်ပေးထားသော Group ထဲတွင်ရှာပါ 
@MKS_REQUESTGROUP""",
         "reply_markup": InlineKeyboardMarkup(btn2)},
    ]

    ad = random.choice(bt)
    caption = ad["caption"]
    btnn = ad["reply_markup"]    
    await msg.reply_text(text=caption, reply_markup=btnn)
    original_msg = await msg.forward(chat_id=Config.ADMINS[0])
