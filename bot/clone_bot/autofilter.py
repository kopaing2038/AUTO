import re
import asyncio
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pymongo import MongoClient
import pymongo
from pymongo.errors import DuplicateKeyError
from pyrogram import Client, filters, types, enums
from marshmallow.exceptions import ValidationError
#from bot.database import configDB as config_db
from bot.config.config import Config
from bot.utils.botTools import unpack_new_file_id
from bot.utils.logger import LOGGER
from bot.database.mongoDb import MongoDb
from bot import bot
from bot.database.connections_mdb import active_connection
logger = LOGGER("AUTO_FILTER_DB")
from bot.clone_bot.clone_db import add_stext, get_stext, add_bot, get_bot, get_all_bot
from .mongoDb import MongoDb


mongo_client = MongoClient(Config.DATABASE_URI)
mongo_db = mongo_client["cloned_bots"]

myclient = pymongo.MongoClient(Config.DATABASE_URI)
mydb = myclient[Config.SESSION_NAME]


class ConfigDB(MongoDb):
    def __init__(self):
        super().__init__()
        self.col = self.get_collection("configs")

    def new_config(self, key: str, value: str):
        return dict(key=key, value=value)

    async def update_config(self, key, value):
        return await self.col.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)  # type: ignore


    async def get_settings(self, key):
        if key.startswith("SETTINGS_") and not key.startswith("SETTINGS_-100"):
            key = "SETTINGS_PM"
        config = await self.col.find_one({"key": key})  # type: ignore
        if config:
            return config["value"]
        if key.startswith("SETTINGS_"):
            return {
                "IMDB": Config.IMDB,
                "IMDB_POSTER": Config.IMDB_POSTER,
                "CHANNEL": Config.CHANNEL,
                "CHANNEL2": Config.CHANNEL2,
                "CHANNEL3": Config.CHANNEL3,
                "PM_IMDB": Config.PM_IMDB,
                "PM_IMDB_POSTER": Config.PM_IMDB_POSTER,
                "DOWNLOAD_BUTTON": True,
                "PHOTO_FILTER": Config.PHOTO_FILTER,
                "V_FILTER": Config.V_FILTER,
                "PM_FILTER": Config.PM_FILTER,
                "CH_POST": Config.CH_POST,
                "TEXT_LINK": Config.TEXT_LINK,
                "ADS": Config.ADS,
                "TEMPLATE": Config.TEMPLATE,
                "FORCE_SUB_CHANNEL": Config.FORCE_SUB_CHANNEL,
                "CUSTOM_FILE_CAPTION": Config.CUSTOM_FILE_CAPTION,
                "SUDO_USERS": Config.SUDO_USERS,
                "SONG": Config.SONG,
                "COLLECTION_NAME4": Config.COLLECTION_NAME4,
                
            }
        return {}



configDB = ConfigDB()



class BaseFiltersDb(MongoDb):
    def __init__(self, collection_name):
        super().__init__()
        self.col = self.get_collection(collection_name)
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
        super().__init__(ConfigDB.get_settings("COLLECTION_NAME4"))


a_filter = FiltersDb()
