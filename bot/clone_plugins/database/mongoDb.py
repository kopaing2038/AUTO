from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase, AgnosticCollection

from bot.config.config import Config


DATABASE_URL = Config.DATABASE_URL
SESSION_NAME2 = Config.SESSION_NAME2

class MongoDb:
    
    def __init__(self):
        self._client = AsyncIOMotorClient(DATABASE_URL)
        self.db : AgnosticDatabase = self._client[SESSION_NAME2]

    def get_collection(self, name: str) -> AgnosticCollection:
        return self.db[name]
    

    


