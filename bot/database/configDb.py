from .mongoDb import MongoDb
from ..config import Config


class ConfigDB(MongoDb):
    def __init__(self):
        super().__init__()
        self.col = self.get_collection("configs")
        self.grp = self.get_collection("groups") 

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
                "PHOTO_FILTER2": Config.PHOTO_FILTER2,
                "PHOTO_FILTER3": Config.PHOTO_FILTER3,
                "PHOTO_FILTER4": Config.PHOTO_FILTER4,
                "PHOTO_FILTER5": Config.PHOTO_FILTER5,
                "V_FILTER": Config.V_FILTER,
                "V_FILTER2": Config.V_FILTER2,
                "V_FILTER3": Config.V_FILTER3,
                "V_FILTER4": Config.V_FILTER4,
                "V_FILTER5": Config.V_FILTER5,
                "CH_POST": Config.CH_POST,
                "TEXT_LINK": Config.TEXT_LINK,
                "IMDB_TEMPLATES": Config.IMDB_TEMPLATES,
                "TEMPLATE": Config.TEMPLATE,
                "CAP2": Config.CAP2,
            }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('SETTINGS_', default)
        return {}

    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})

configDB = ConfigDB()
