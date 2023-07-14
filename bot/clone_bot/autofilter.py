import re

from pymongo.errors import BulkWriteError, DuplicateKeyError
from bot.config.config import Config
from bot.clone_bot.botTools import unpack_new_file_id
from bot.utils.logger import LOGGER
from bot.database.mongoDb import MongoDb

logger = LOGGER("AUTO_FILTER_DB")


class clonedme(object):
    ME = None
    U_NAME = None
    B_NAME = None

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
                insert = await self.col.insert_many(self.data, ordered=False)  # type: ignore
            except BulkWriteError as e:
                inserted = e.details["nInserted"]  # type: ignore
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
                insert = await self.col.insert_many(self.data, ordered=False)  # type: ignore
            except BulkWriteError as e:
                inserted = e.details["nInserted"]  # type: ignore
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
    
        channel_name = None
        if hasattr(media, 'channel_name'):
            channel_name = media.channel_name
    
        return dict(
            _id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            chat_id=media.chat_id,
            channel_name=channel_name,
            message_id=media.message_id,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
       )
    async def save_file(self, media):
        """Save file in database"""
        file = await self.file_dict(media)
        try:
            await self.col.insert_one(file)  # type: ignore
        except DuplicateKeyError:
            logger.warning(
                f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
            )
            return False, 0
        else:
            logger.info(
                f'{getattr(media, "file_name", "NO_FILE")} is saved to database'
            )
            return True, 1


    async def get_search_results(self, query: str, file_type: str = None, max_results: int = 5, offset: int = 0, filter: bool = False, photo: bool = True, video: bool = True):  # type: ignore
        """For given query return (results, next_offset)"""

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
            filter_ = {"$or": [{"file_name": regex}, {"caption": regex}]}  # type: ignore
        else:
            filter_ = {"file_name": regex}  # type: ignore

        if not photo:
            filter_ = {"$and": [filter_, {"file_type": {"$ne": "photo"}}]}

        if not video:
            filter_ = {"$and": [filter_, {"file_type": {"$ne": "video"}}]}

        total_results = await self.col.count_documents(filter_)  # type: ignore
        next_offset = offset + max_results

        if next_offset > total_results:
            next_offset = ""

        cursor = self.col.find(filter_)
        # Sort by recent
        cursor.sort("$natural", -1)  # type: ignore
        # Slice files according to offset and max results
        cursor.skip(offset)  # type: ignore
        cursor.limit(max_results)  # type: ignore
        # Get list of files
        files = await cursor.to_list(length=max_results)

        return files, next_offset, total_results

    async def get_file_details(self, file_id: str):
        return await self.col.find_one({"_id": file_id})  # type: ignore

    async def count_documents(self, filter_: dict) -> int:
        return await self.col.count_documents(filter_)

    async def get_distinct_chat_ids(self):
        return await self.col.distinct("chat_id")

    async def delete_many(self, chat_id: dict):
        result = await self.col.delete_many({"chat_id": chat_id})
        return result

    async def delete_files(self, query, filter=True):
        query = query.strip()
        # for better results
        if filter:
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
        file_filter = {'file_name': regex}  # Renamed 'filter' variable to 'file_filter' to avoid confusion with built-in 'filter' function
        total = await self.count_documents(file_filter)  # Use 'self' to access the instance variable
        files = await self.col.find(file_filter).to_list(None)
        return total, files


class FiltersDb(BaseFiltersDb):
    def __init__(self, bot_id):
        collection_name = f"{clonedme.U_NAME}_{clonedme.B_NAME}_{bot_id}"
        super().__init__(collection_name)



a_filter = FiltersDb(bot_id)



