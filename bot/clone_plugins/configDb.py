from bot.database.mongoDb import MongoDb
from ..config import Config


IMDB = True
IMDB_POSTER = True
CHANNEL = True
PM_IMDB = True
PM_IMDB_POSTER = True
PHOTO_FILTER = True

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
                "IMDB": IMDB,
                "IMDB_POSTER": IMDB_POSTER,
                "CHANNEL": CHANNEL,
                "PM_IMDB": PM_IMDB,
                "PM_IMDB_POSTER": PM_IMDB_POSTER,
                "DOWNLOAD_BUTTON": True,
                "PHOTO_FILTER": PHOTO_FILTER
            }
        return {}


configDB = ConfigDB()
