import aiogram

from yaml import safe_load
config = safe_load(open("config/bot_config.yaml", "r"))

class Bot:
    """
    Singleton for Bot
    """

    _instance: 'Bot' = None

    def __new__(cls) -> 'Bot':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._bot = aiogram.Bot(token=config["token"])
        return cls._instance._bot