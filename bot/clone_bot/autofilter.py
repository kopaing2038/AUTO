import re
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pymongo import MongoClient
import pymongo
from pymongo.errors import DuplicateKeyError
from marshmallow.exceptions import ValidationError

from bot.config.config import Config
from bot.utils.botTools import unpack_new_file_id
from bot.utils.logger import LOGGER
from bot.database.mongoDb import MongoDb
from bot import bot
from bot.database.connections_mdb import active_connection
logger = LOGGER("AUTO_FILTER_DB")
from bot.clone_bot.clone_db import add_stext, get_stext, add_bot, get_bot, get_all_bot
mongo_client = MongoClient(Config.DATABASE_URI)
mongo_db = mongo_client["cloned_bots"]

myclient = pymongo.MongoClient(Config.DATABASE_URI)
mydb = myclient[Config.SESSION_NAME]
message = ...
userid = message.from_user.id if message.from_user else None

class BaseFiltersDb:
    def __init__(self, collection_name):
        self.col = mydb[collection_name]
        self.data = []

    async def insert_many(self, media):
        file = await self.file_dict(media)
        self.data.append(file)
        if len(self.data) >= 200:
            try:
                insert = await self.col.insert_many(self.data, ordered=False)
            except BulkWriteError as e:
                inserted = e.details["nInserted"]
            else:
                inserted = len(insert.inserted_ids)
            duplicate = len(self.data) - inserted
            self.data.clear()
            return inserted, duplicate

        logger.info(f'{getattr(media, "file_name", "NO_FILE")} is updated in database')
        return None, None

    async def insert_pending(self):
        if self.data:
            try:
                insert = await self.col.insert_many(self.data, ordered=False)
            except BulkWriteError as e:
                inserted = e.details["nInserted"]
            else:
                inserted = len(insert.inserted_ids)
            duplicate = len(self.data) - inserted
            self.data.clear()
            return inserted, duplicate
        return 0, 0

    async def file_dict(self, media):
        file_id, file_ref = unpack_new_file_id(media.file_id)
        if media.file_type == "photo":
            file_ref = media.file_id
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))

        channel_name = getattr(media, 'channel_name', None)

        return {
            '_id': file_id,
            'file_ref': file_ref,
            'file_name': file_name,
            'file_size': media.file_size,
            'chat_id': media.chat_id,
            'channel_name': channel_name,
            'message_id': media.message_id,
            'file_type': media.file_type,
            'mime_type': media.mime_type,
            'caption': media.caption.html if media.caption else None,
        }

    async def save_file(self, media):
        file = await self.file_dict(media)
        try:
            await self.col.insert_one(file)
        except DuplicateKeyError:
            logger.warning(f'{getattr(media, "file_name", "NO_FILE")} is already saved in database')
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            return True, 1

    async def get_search_results(self, query: str, file_type: str = None, max_results: int = 5,
                                 offset: int = 0, filter_: bool = False, photo: bool = True, video: bool = True):
        query = query.strip()

        if not query:
            raw_pattern = "."
        elif " " not in query:
            raw_pattern = r"(\b|[\.\+\-_])" + query + r"(\b|[\.\+\-_])"
        else:
            raw_pattern = query.replace(" ", r".*[\s\.\+\-_]")

        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            return []

        if Config.USE_CAPTION_FILTER:
            filter_ = {"$or": [{"file_name": regex}, {"caption": regex}]}
        else:
            filter_ = {"file_name": regex}

        if not photo:
            filter_ = {"$and": [filter_, {"file_type": {"$ne": "photo"}}]}

        if not video:
            filter_ = {"$and": [filter_, {"file_type": {"$ne": "video"}}]}

        total_results = await self.col.count_documents(filter_)
        next_offset = offset + max_results

        if next_offset > total_results:
            next_offset = ""

        cursor = self.col.find(filter_)
        cursor.sort("$natural", -1)
        cursor.skip(offset)
        cursor.limit(max_results)
        files = await cursor.to_list(length=max_results)

        return files, next_offset, total_results

    async def get_file_details(self, file_id: str):
        return await self.col.find_one({"_id": file_id})

    async def count_documents(self, filter_: dict) -> int:
        return await self.col.count_documents(filter_)

    async def get_distinct_chat_ids(self):
        return await self.col.distinct("chat_id")

    async def delete_many(self, chat_id: dict):
        result = await self.col.delete_many({"chat_id": chat_id})
        return result

    async def delete_files(self, query, filter_: bool = True):
        query = query.strip()

        if filter_:
            query = query.replace(' ', r'(\s|\.|\+|\-|_)')
            raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
        if not query:
            raw_pattern = '.'
        elif ' ' not in query:
            raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            return []
        file_filter = {'file_name': regex}
        total = await self.count_documents(file_filter)
        files = await self.col.find(file_filter).to_list(None)
        return total, files


class FiltersDb(BaseFiltersDb):
    def __init__(self):
        group_id = active_connection(str(userid))
        super().__init__(str(group_id) if group_id is not None else '')




a_filter = FiltersDb()
