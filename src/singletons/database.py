from utils.sync import make_async

from typing import Any
from surrealdb import Surreal

from yaml import safe_load
config = {
    "db": safe_load(open("config/db_config.yaml", "r")),
    "bot": safe_load(open("config/bot_config.yaml", "r"))
}

class Database:
    """
    Singleton for database connection
    """

    _instance: 'Database' = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = Surreal(f"ws://localhost:{config['db']['port']}/rpc")
            return cls._instance 
        
        return make_async(cls._instance._connection)()
    
    def __await__(self):
        return self._connect().__await__()

    async def _connect(self):
        await self._connection.connect()
        await self._connection.signin({"user": config["db"]["user"], "pass": config["db"]["pass"]})
        await self._connection.use(config["db"]["ns"], config["db"]["db"])
        await self._connection.let("interviewers_tags", config["bot"]["interviewers_tags"])
        return self._connection