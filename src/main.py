import asyncio
from typing import NoReturn

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

dp = Dispatcher()

from yaml import safe_load
config = {
    "bot": safe_load(open("config/bot_config.yaml", "r")),
    "db": safe_load(open("config/db_config.yaml", "r"))
}

from surrealdb import Surreal
db = Surreal(f"ws://localhost:{config['db']['port']}/rpc")

@dp.message(Command("start"))
async def start(message: types.Message) -> None:
    """Send a message when the command /start is issued."""
    await message.answer("Without thinking twice Bot")

async def db_connect():
    await db.connect()
    await db.signin({"user": config["db"]["user"], "pass": config["db"]["pass"]})
    await db.use(config["db"]["ns"], config["db"]["db"])

async def main() -> NoReturn:
    await db_connect()

    bot = Bot(token=config["bot"]["token"])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())