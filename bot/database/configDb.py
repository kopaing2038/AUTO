from .mongoDb import MongoDb
from ..config import Config


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
                "CH_POST": Config.CH_POST,
                "TEXT_LINK": Config.TEXT_LINK,
                "ADS": Config.ADS,
                "TEMPLATE": Config.TEMPLATE,
                "FORCE_SUB_CHANNEL": Config.FORCE_SUB_CHANNEL,
                "CUSTOM_FILE_CAPTION": Config.CUSTOM_FILE_CAPTION,
                "SUDO_USERS": Config.SUDO_USERS,
            }
        return {}



configDB = ConfigDB()
