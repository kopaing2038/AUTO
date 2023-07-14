import pymongo
from bot.config.config import Config

#-------------»[Create_DB]«--------------#

myclient = pymongo.MongoClient(Config.DATABASE_URI)
db_x = myclient["KP_Clone_Bot"]
clonedb = db_x["clone_db"]
string = db_x["STRING"]

#-------------»[Saving_DB]«-------------#

async def add_bot(user_id, client):
    await string.update_one({'id' : id}, {'$set' : {'token' : client}})

async def get_bot(user_id):
    bot = string.find_one({"_id": user_id})
    return False if not bot else bot.get('token')

async def rmsession(client):
    await string.delete_one({"string": client})


async def get_all_bot():
    lol = [n for n in string.find({})]
    return lol

async def is_session_in_db(client):
    k = await string.find_one({"string": client})
    if k:
        return True
    else:
        return False

async def count_bot():
    b_count=await string.token.count_documents({})
    return b_count


async def add_stext(id, text):	
    clonedb.update_one({'id' : id}, {'$set' : {'text' : text}})

async def get_stext(id):
    text = clonedb.find_one({'id' : int(id)})
    return False if not text else text.get('text')
