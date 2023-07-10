from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from bot import Bot
# Set the chat ID and approval setting
CHAT_ID1 = -1001576347419 # Replace with your chat ID
CHAT_ID2 = -1001576347419 # Replace with your chat ID
CHAT_ID3 = -1001576347419 # Replace with your chat ID
CHAT_ID4 = -1001576347419 # Replace with your chat ID

APPROVED = "on"  # Set to "on" or "off" to enable/disable sending a message on approval

# Define the message to send on approval
TEXT = "Welcome to {title}, {mention}!"

# Create a Pyrogram client instance
#app = Client("my_account")

# Define the auto-approve function
@Bot.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID1) if CHAT_ID1 else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    chat = message.chat 
    user = message.from_user 
    print(f"{user.first_name} Joined (Approved)") 
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    if APPROVED == "on":
        await client.send_message(chat_id=chat.id, text=TEXT.format(mention=user.mention, title=chat.title))

@Bot.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID2) if CHAT_ID2 else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    chat = message.chat 
    user = message.from_user 
    print(f"{user.first_name} Joined (Approved)") 
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    if APPROVED == "on":
        await client.send_message(chat_id=chat.id, text=TEXT.format(mention=user.mention, title=chat.title))

@Bot.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID3) if CHAT_ID3 else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    chat = message.chat 
    user = message.from_user 
    print(f"{user.first_name} Joined (Approved)") 
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    if APPROVED == "on":
        await client.send_message(chat_id=chat.id, text=TEXT.format(mention=user.mention, title=chat.title))

@Bot.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID4) if CHAT_ID4 else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    chat = message.chat 
    user = message.from_user 
    print(f"{user.first_name} Joined (Approved)") 
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    if APPROVED == "on":
        await client.send_message(chat_id=chat.id, text=TEXT.format(mention=user.mention, title=chat.title))
