import pymongo


from bot.config.config import Config
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(Config.DATABASE_URI)
mydb = myclient[Config.SESSION_NAME]
mycol = mydb['CONNECTION']   
btcol = mydb['CLONEBOT']


async def delete_bot(user_id, bot_id):

    try:
        update = btcol.update_one(
            {"_id": user_id},
            {"$pull" : { "bot_details" : {"bot_id":bot_id} } }
        )
        if update.modified_count == 0:
            return False
        query = btcol.find_one(
            { "_id": user_id },
            { "_id": 0 }
        )
        if len(query["bot_details"]) >= 1:
            if query['active_bot'] == bot_id:
                prvs_bot_id = query["bot_details"][len(query["bot_details"]) - 1]["bot_id"]

                btcol.update_one(
                    {'_id': user_id},
                    {"$set": {"active_bot" : prvs_bot_id}}
                )
        else:
            btcol.update_one(
                {'_id': user_id},
                {"$set": {"active_bot" : None}}
            )
        return True
    except Exception as e:
        logger.exception(f'Some error occurred! {e}', exc_info=True)
        return False

async def all_bot(user_id):
    query = btcol.find_one(
        { "_id": user_id },
        { "_id": 0, "active_bot": 0 }
    )
    if query is not None:
        return [x["bot_id"] for x in query["bot_details"]]
    else:
        return None

async def add_id(bot_id, user_id):
    query = btcol.find_one(
        { "_id": user_id },
        { "_id": 0, "active_bot": 0 }
    )
    if query is not None:
        bot_ids = [x["bot_id"] for x in query["bot_details"]]
        if bot_id in bot_ids:
            return False

    bot_details = {
        "bot_id" : bot_id
    }

    data = {
        '_id': user_id,
        'bot_details' : [bot_details],
        'active_bot' : bot_id
    }
    if btcol.count_documents( {"_id": user_id} ) == 0:
        try:
            btcol.insert_one(data)
            return True
        except:
            logger.exception('Some error occurred!', exc_info=True)

    else:
        try:
            btcol.update_one(
                {'_id': user_id},
                {
                    "$push": {"bot_details": bot_details},
                    "$set": {"active_bot" : bot_id}
                }
            )
            return True
        except:
            logger.exception('Some error occurred!', exc_info=True)

async def add_connection(group_id, user_id):
    query = mycol.find_one(
        { "_id": user_id },
        { "_id": 0, "active_group": 0 }
    )
    if query is not None:
        group_ids = [x["group_id"] for x in query["group_details"]]
        if group_id in group_ids:
            return False

    group_details = {
        "group_id" : group_id
    }

    data = {
        '_id': user_id,
        'group_details' : [group_details],
        'active_group' : group_id,
    }

    if mycol.count_documents( {"_id": user_id} ) == 0:
        try:
            mycol.insert_one(data)
            return True
        except:
            logger.exception('Some error occurred!', exc_info=True)

    else:
        try:
            mycol.update_one(
                {'_id': user_id},
                {
                    "$push": {"group_details": group_details},
                    "$set": {"active_group" : group_id}
                }
            )
            return True
        except:
            logger.exception('Some error occurred!', exc_info=True)

        
async def active_connection(user_id):

    query = mycol.find_one(
        { "_id": user_id },
        { "_id": 0, "group_details": 0 }
    )
    if not query:
        return None

    group_id = query['active_group']
    return int(group_id) if group_id != None else None


async def all_connections(user_id):
    query = mycol.find_one(
        { "_id": user_id },
        { "_id": 0, "active_group": 0 }
    )
    if query is not None:
        return [x["group_id"] for x in query["group_details"]]
    else:
        return None


async def if_active(user_id, group_id):
    query = mycol.find_one(
        { "_id": user_id },
        { "_id": 0, "group_details": 0 }
    )
    return query is not None and query['active_group'] == group_id


async def make_active(user_id, group_id):
    update = mycol.update_one(
        {'_id': user_id},
        {"$set": {"active_group" : group_id}}
    )
    return update.modified_count != 0


async def make_inactive(user_id):
    update = mycol.update_one(
        {'_id': user_id},
        {"$set": {"active_group" : None}}
    )
    return update.modified_count != 0


async def delete_connection(user_id, group_id):

    try:
        update = mycol.update_one(
            {"_id": user_id},
            {"$pull" : { "group_details" : {"group_id":group_id} } }
        )
        if update.modified_count == 0:
            return False
        query = mycol.find_one(
            { "_id": user_id },
            { "_id": 0 }
        )
        if len(query["group_details"]) >= 1:
            if query['active_group'] == group_id:
                prvs_group_id = query["group_details"][len(query["group_details"]) - 1]["group_id"]

                mycol.update_one(
                    {'_id': user_id},
                    {"$set": {"active_group" : prvs_group_id}}
                )
        else:
            mycol.update_one(
                {'_id': user_id},
                {"$set": {"active_group" : None}}
            )
        return True
    except Exception as e:
        logger.exception(f'Some error occurred! {e}', exc_info=True)
        return False
