import re
import asyncio
import pymongo
from pymongo.errors import BulkWriteError, DuplicateKeyError
from marshmallow.exceptions import ValidationError
from bot.config.config import Config
from bot import Bot
from pyrogram import Client, filters, errors
from pyrogram.errors import MessageNotModified
from pyrogram.errors import UserAlreadyParticipant
import os

VID_SEARCH = os.environ.get("VID_SEARCH", "yes").lower()

myclient = pymongo.MongoClient(Config.DATABASE_URI)
mydb = myclient[Config.SESSION_NAME2]
from ..utils.cache import Cache
from ..utils.logger import LOGGER

logger = LOGGER("INDEX")


lock = asyncio.Lock()
_REGEX = r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"


async def savefiles(docs, group_id):
    mycol = mydb[str(group_id)]

    try:
        mycol.insert_many(docs, ordered=False)
    except Exception as e:
        print(f"savefiles error: {str(e)}")


async def channelgroup(channel_id, channel_name, group_id, group_name):
    mycol = mydb["ALL DETAILS"]

    channel_details = {
        "channel_id": channel_id,
        "channel_name": channel_name
    }

    data = {
        '_id': group_id,
        'group_name': group_name,
        'channel_details': [channel_details],
    }

    if mycol.count_documents({"_id": group_id}) == 0:
        try:
            mycol.insert_one(data)
            print(f"Files in '{channel_name}' linked to '{group_name}' ")
        except Exception as e:
            print(f"channelgroup insert error: {str(e)}")
    else:
        try:
            mycol.update_one({'_id': group_id}, {"$push": {"channel_details": channel_details}})
            print(f"Files in '{channel_name}' linked to '{group_name}' ")
        except Exception as e:
            print(f"channelgroup update error: {str(e)}")


async def if_exists(channel_id, group_id):
    mycol = mydb["ALL DETAILS"]

    query = mycol.count_documents({"_id": group_id})
    if query == 0:
        return False
    else:
        ids = mycol.find({'_id': group_id})
        channel_ids = []
        for doc in ids:
            for chid in doc['channel_details']:
                channel_ids.append(chid['channel_id'])

        return channel_id in channel_ids


async def deletefiles(channel_id, channel_name, group_id, group_name):
    mycol1 = mydb["ALL DETAILS"]

    try:
        mycol1.update_one(
            {"_id": group_id},
            {"$pull": {"channel_details": {"channel_id": channel_id}}}
        )
    except Exception as e:
        print(f"deletefiles update error: {str(e)}")

    mycol2 = mydb[str(group_id)]
    query2 = {'channel_id': channel_id}
    try:
        mycol2.delete_many(query2)
        print(f"Filters from '{channel_name}' deleted in '{group_name}'")
        return True
    except Exception as e:
        print(f"deletefiles delete error: {str(e)}")
        return False


async def deletealldetails(group_id):
    mycol = mydb["ALL DETAILS"]

    query = {"_id": group_id}
    try:
        mycol.delete_one(query)
    except Exception as e:
        print(f"deletealldetails error: {str(e)}")


async def deletegroupcol(group_id):
    mycol = mydb[str(group_id)]

    if mycol.count_documents({}) == 0:
        return 1

    try:
        mycol.drop()
    except Exception as e:
        print(f"deletegroupcol drop error: {str(e)}")
        return 2
    else:
        return 0


async def channeldetails(group_id):
    mycol = mydb["ALL DETAILS"]

    query = mycol.count_documents({"_id": group_id})
    if query == 0:
        return False
    else:
        ids = mycol.find({'_id': group_id})
        chdetails = []
        for doc in ids:
            for chid in doc['channel_details']:
                chdetails.append(
                    str(chid['channel_name']) + " ( <code>" + str(chid['channel_id']) + "</code> )"
                )
        return chdetails


async def countfilters(group_id):
    mycol = mydb[str(group_id)]

    query = mycol.count_documents({})
    return query


async def findgroupid(channel_id):
    mycol = mydb["ALL DETAILS"]

    ids = mycol.find()
    groupids = []
    for doc in ids:
        for chid in doc['channel_details']:
            if channel_id == chid['channel_id']:
                groupids.append(doc['_id'])
    return groupids


@Client.on_message(filters.group & filters.command(["add"]))
async def addchannel(client, message):

    if message.from_user.id not in Config.ADMINS:
        return

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Enter in correct format!\n\n<code>/add channelid</code>  or\n"
            "<code>/add @channelusername</code></i>"
            "\n\nGet Channel id from @ChannelidHEXbot",
        )
        return
    try:
        if not text.startswith("@"):
            chid = int(text)
            if not len(text) == 14:
                await message.reply_text(
                    "Enter valid channel ID"
                )
                return
        elif text.startswith("@"):
            chid = text
            if not len(chid) > 2:
                await message.reply_text(
                    "Enter valid channel username"
                )
                return
    except Exception:
        await message.reply_text(
            "Enter a valid ID\n"
            "ID will be in <b>-100xxxxxxxxxx</b> format\n"
            "You can also use the username of the channel with the @ symbol",
        )
        return

    try:
        invitelink = await client.export_chat_invite_link(chid)
    except:
        await message.reply_text(
            "<i>Add me as an admin in your channel with admin rights - 'Invite Users via Link' and try again</i>",
        )
        return

    try:
        user = await client.get_me()
    except Exception:
        user = None

    try:
        await client.join_chat(invitelink)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        print(e)
        await message.reply_text(
            f"<i>User {user.first_name} couldn't join your channel! Make sure the user is not banned in the channel."
            "\n\nOr manually add the user to your channel and try again</i>",
        )
        return

    try:
        chatdetails = await client.get_chat(chid)
    except:
        await message.reply_text(
            "<i>Send a message to your channel and try again</i>"
        )
        return

    intmsg = await message.reply_text(
        "<i>Please wait while I'm adding your channel files to the DB"
        "\n\nIt may take some time if you have more files in the channel!!"
        "\nDon't give any other commands now!</i>"
    )

    channel_id = chatdetails.id
    channel_name = chatdetails.title
    group_id = message.chat.id
    group_name = message.chat.title

    already_added = await ifexists(channel_id, group_id)
    if already_added:
        await intmsg.edit_text("Channel already added to the DB!")
        return

    docs = []

    try:
        async for msg in client.search_messages(channel_id, filter='document'):
            try:
                file_name = msg.document.file_name
                file_id = msg.document.file_id
                file_size = msg.document.file_size                   
                link = msg.link
                data = {
                    '_id': file_id,
                    'channel_id' : channel_id,
                    'file_name': file_name,
                    'file_size': file_size,
                    'link': link
                }
                docs.append(data)
            except:
                pass
    except:
        pass

    await asyncio.sleep(5)

    try:
        async for msg in client.search_messages(channel_id, filter='video'):
            try:
                file_name = msg.video.file_name
                file_id = msg.video.file_id   
                file_size = msg.video.file_size              
                link = msg.link
                data = {
                    '_id': file_id,
                    'channel_id' : channel_id,
                    'file_name': file_name,
                    'file_size': file_size,
                    'link': link
                }
                docs.append(data)
            except:
                pass
    except:
        pass

    await asyncio.sleep(5)

    if docs:
        await savefiles(docs, group_id)
    else:
        await intmsg.edit_text("Channel couldn't be added. Try again after some time!")
        return

    await channelgroup(channel_id, channel_name, group_id, group_name)

    await intmsg.edit_text("Channel added successfully!")

