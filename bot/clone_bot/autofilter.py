import re
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pymongo import MongoClient
from bot.config.config import Config
from bot.utils.botTools import unpack_new_file_id
from bot.utils.logger import LOGGER
from bot.database.mongoDb import MongoDb

logger = LOGGER("AUTO_FILTER_DB")

class ClonedMe(object):
    ME = None
    U_NAME = None
    B_NAME = None


class BaseFiltersDb:
    def __init__(self, collection_name):
        self.col = self.get_collection(collection_name)
        self.data = []

    async def insert_many(self, media):
        file = await self.file_dict(media)
        self.data.append(file)
        if len(self.data) >= 200:
            inserted, duplicate = await self._insert_many_data()
            return inserted, duplicate

        print(f'{getattr(media, "file_name", "NO_FILE")} is updated in the database')
        return None, None

    async def insert_pending(self):
        if self.data:
            inserted, duplicate = await self._insert_many_data()
            return inserted, duplicate
        return 0, 0

    async def _insert_many_data(self):
        try:
            insert = await self.col.insert_many(self.data, ordered=False)
        except BulkWriteError as e:
            inserted = e.details["nInserted"]
        else:
            inserted = len(insert.inserted_ids)
        duplicate = len(self.data) - inserted
        self.data.clear()
        return inserted, duplicate

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

    async def get_search_results(
        self,
        query: str,
        file_type: str = None,
        max_results: int = 5,
        offset: int = 0,
        filter: bool = False,
        photo: bool = True,
        video: bool = True
    ):
        query = query.strip()

        if not query:
            raw_pattern = "."
        elif " " not in query:
            raw_pattern = r"(\b|[\.\+\-_])" + query + r"(\b|[\.\+\-_])"
        else:
            raw_pattern = query.replace(" ", r".*[\s\.\+\-_]")

        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except re.error:
            return []

        if not photo:
            filter_ = {"$and": [{"file_name": regex}, {"file_type": {"$ne": "photo"}}]}
        elif not video:
            filter_ = {"$and": [{"file_name": regex}, {"file_type": {"$ne": "video"}}]}
        else:
            filter_ = {"file_name": regex}

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


class FiltersDb(BaseFiltersDb):
    def __init__(self):
        super().__init__("{ClonedMe.U_NAME}")



a_filter = FiltersDb()

