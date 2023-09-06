import os
from pathlib import Path

import asyncio
from typing import NoReturn
import json

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
async def cmd_start(message: types.Message) -> None:
    """Send a message when the command /start is issued."""
    user = await db.select(f"interviewers:{message.from_user.username}")
    if user is None:
        user = await db.select(f"interviewees:{message.from_user.username}")
        if user is None:
            await message.answer("You are not registered")
        else:
            await message.reply(f"Hello, {user['name']}")
            await message.answer(f"You are registered with tags {user['tags']}. You can only take tests you are assigned to.")
    else:
        answer = ""
        if "admin" in user["tags"]:
            answer += "You are registered as `admin` so you can add other interviewers to the bot.\n\n"
        answer += f"You roles are {user['tags']}"
        await message.reply(f"Hello, {user['name']}")
        await message.answer(answer)
        await message.answer(str(await db.info()))

async def db_connect() -> Surreal:
    """Just the way to connect to the database"""
    await db.connect()
    await db.signin({"user": config["db"]["user"], "pass": config["db"]["pass"]})
    await db.use(config["db"]["ns"], config["db"]["db"])
    await db.let("interviewers_tags", config["bot"]["interviewers_tags"])
    return db

#############
import backup

async def main() -> NoReturn:
    db = await db_connect()

    try:
        backups = [
            b for b in sorted(Path("data/backups").iterdir(), key=os.path.getctime)
            if b.is_dir()
        ]
        if len(backups) != 0:
            path = backups[-1]
            interviewers_tags_backed = json.loads((path / "interviewers.json").read_text(encoding="UTF-8"))
            await db.update("interviewers_tags", interviewers_tags_backed)

            await db.delete("interviewers")
            interviewers_backed = json.loads((path / "interviewers.json").read_text(encoding="UTF-8"))
            for backed in interviewers_backed:
                await db.create(backed["id"], backed)

            await db.delete("interviewees")
            interviewees_backed = json.loads((path / "interviewees.json").read_text(encoding="UTF-8"))
            for backed in interviewees_backed:
                await db.create(backed["id"], backed)

            await db.delete("tests")
            tests_backed = json.loads((path / "tests.json").read_text(encoding="UTF-8"))
            for backed in tests_backed:
                await db.create(backed["id"], backed)

            print("Database is restored from the last backup")
        else:
            await db.let("interviewers_tags", config["bot"]["interviewers_tags"])
            await db.create(
                f"interviewers:{config['bot']['admin']['id']}",
                {
                    "id": config['bot']['admin']['id'],
                    "name": config['bot']['admin']['name'],
                    "description": config['bot']['admin']['description'],
                    "tags": config['bot']['admin']['tags'],
                    "tests": config['bot']['admin']['tests'],
                }
            )

            print("Database is created from config file")
    except:
        print("\n\tHas to be unreachable\n")
        pass

    bot = Bot(token=config["bot"]["token"])
    dp.include_router(backup.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())