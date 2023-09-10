from singletons.database import Database
from singletons.bot import Bot
from singletons.logger import Logger
log = Logger()

import os
from pathlib import Path
from datetime import datetime

import json

from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.types.input_media_document import InputMediaDocument
router = Router()

from aiogram_media_group import media_group_handler

@router.message(Command("backup"))
async def cmd_backup(message: types.Message) -> None:
    """Start a backup with a command /backup"""
    db = await Database()
    user = await db.select(f"interviewers:{message.from_user.username}")
    if user is not None and "admin" in user["tags"]:
        buttons = [[
            types.InlineKeyboardButton(text="Locally", callback_data="local_backup"),
            types.InlineKeyboardButton(text="Locally & Telegram", callback_data="tg_backup")
        ]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(
            "How do you want to backup?",
            reply_markup=keyboard
        )
    else:
        await message.reply(
            "You are not allowed to make backups, because you are not an admin"
        )

@router.callback_query(F.data == "local_backup")
async def cb_local_backup(callback: types.CallbackQuery) -> None:
    """Perform only local backup"""
    db = await Database()
    path = Path("data/backups")
    if not path.is_dir():
        path.mkdir()

    now = datetime.now()
    path = path / f"{now.strftime('%d.%m.%Y_%H:%M:%S')}"
    path.mkdir()

    interviewers = await db.select("interviewers")
    interviewees = await db.select("interviewees")
    tests = await db.select("tests")

    with open(f"{path}/interviewers.json", "w") as interviewers_file:
        json.dump(interviewers, interviewers_file, indent=2)
    with open(f"{path}/interviewees.json", "w") as interviewees_file:
        json.dump(interviewees, interviewees_file, indent=2)
    with open(f"{path}/tests.json", "w") as tests_file:
        json.dump(tests, tests_file, indent=2)
    with open(f"{path}/interviewers_tags.json", "w") as interviewers_tags_file:
        json.dump((await db.query("return $interviewers_tags"))[0]["result"], interviewers_tags_file, indent=2)

    log.info(f"Local backup was created by {callback.message.from_user.username} ({now.strftime('%d.%m.%Y, %H:%M:%S')})")
    await callback.message.reply(
        f"Database was backuped at {now.strftime('%d.%m.%Y, %H:%M:%S')}"
    )
    await callback.answer()

@router.callback_query(F.data == "tg_backup")
async def cb_tg_backup(callback: types.CallbackQuery) -> None:
    """Perform local & telegram backup"""
    db = await Database()
    path = Path("data/backups")
    if not path.is_dir():
        path.mkdir()

    now = datetime.now()
    path = path / f"{now.strftime('%d.%m.%Y_%H:%M:%S')}"
    path.mkdir()

    interviewers = await db.select("interviewers")
    interviewees = await db.select("interviewees")
    tests = await db.select("tests")
    
    with open(f"{path}/interviewers.json", "w") as interviewers_file:
        json.dump(interviewers, interviewers_file, indent=2)
    with open(f"{path}/interviewees.json", "w") as interviewees_file:
        json.dump(interviewees, interviewees_file, indent=2)
    with open(f"{path}/tests.json", "w") as tests_file:
        json.dump(tests, tests_file, indent=2)
    with open(f"{path}/interviewers_tags.json", "w") as interviewers_tags_file:
        json.dump((await db.query("return $interviewers_tags"))[0]["result"], interviewers_tags_file, indent=2)
    await callback.message.answer_media_group(media=[
        InputMediaDocument(media=FSInputFile(path / "interviewers.json")),
        InputMediaDocument(media=FSInputFile(path / "interviewees.json")),
        InputMediaDocument(media=FSInputFile(path / "tests.json")),
        InputMediaDocument(media=FSInputFile(path / "interviewers_tags.json")),
    ])

    log.info(f"Local and Telegram backup was created by {callback.message.from_user.username} ({now.strftime('%d.%m.%Y, %H:%M:%S')})")
    await callback.message.reply(
        f"Database was backuped at {now.strftime('%d.%m.%Y, %H:%M:%S')}"
    )
    await callback.answer()

@router.message(Command("restore"))
async def cmd_restore(message: types.Message) -> None:
    """Start a restore with a command /restore"""
    db = await Database()
    user = await db.select(f"interviewers:{message.from_user.username}")
    if user is not None and "admin" in user["tags"]:
        buttons = [[
            types.InlineKeyboardButton(text="Locally", callback_data="local_restore"),
            types.InlineKeyboardButton(text="From Telegram", callback_data="tg_restore")
        ]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(
            "How do you want to restore?",
            reply_markup=keyboard
        )
    else:
        await message.reply(
            "You are not allowed to restore, because you are not an admin"
        )

@router.callback_query(F.data == "local_restore")
async def cb_local_restore(callback: types.CallbackQuery) -> None:
    """Perform local restore"""
    path = Path("data/backups")
    backups = [
        backup.parts[-1]
        for backup in sorted(path.iterdir(), key=os.path.getctime)
        if backup.is_dir()
    ]
    buttons = [
        [types.InlineKeyboardButton(text=backup.replace("_", " "), callback_data=f"backup_{backup}")]
        for backup in backups
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer(
        "Select backup to restore",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("backup_"))
async def cb_local_restore_backup(callback: types.CallbackQuery) -> None:
    """Restore specified backup"""
    db = await Database()
    
    backup = "_".join(callback.data.split("_")[1:])
    path = Path("data/backups") / backup

    interviewers_tags_backed = json.loads((path / "interviewers.json").read_text(encoding="UTF-8"))
    await db.update("interviewers_tags", interviewers_tags_backed)

    # interviewers
    interviewers_db_ids = (await db.query("select value id from interviewers"))[0]["result"]
    interviewers_backed = json.loads((path / "interviewers.json").read_text(encoding="UTF-8"))
    for backed in interviewers_backed:
        try:
            try:
                await db.update(backed["id"], backed)
                interviewers_db_ids.remove(backed["id"])
            except:
                await db.create(backed["id"], backed)
        except:
            await callback.message.answer(f"Can't restore `{backed['id']}`")
    for id in interviewers_db_ids:
        await db.delete(id)
    
    # interviewees
    interviewees_db_ids = (await db.query("select value id from interviewees"))[0]["result"]
    interviewees_backed = json.loads((path / "interviewees.json").read_text(encoding="UTF-8"))
    for backed in interviewees_backed:
        try:
            try:
                await db.update(backed["id"], backed)
                interviewees_db_ids.remove(backed["id"])
            except:
                await db.create(backed["id"], backed)
        except:
            await callback.message.answer(f"Can't restore `{backed['id']}`")
    for id in interviewees_db_ids:
        await db.delete(id)
    
    # tests
    tests_db_ids = (await db.query("select value id from tests"))[0]["result"]
    tests_backed = json.loads((path / "tests.json").read_text(encoding="UTF-8"))
    for backed in tests_backed:
        try:
            try:
                await db.update(backed["id"], backed)
                tests_db_ids.remove(backed["id"])
            except:
                await db.create(backed["id"], backed)
        except:
            await callback.message.answer(f"Can't restore `{backed['id']}`")
    for id in tests_db_ids:
        await db.delete(id)
        
    log.info(f"Backup was restored by {callback.message.from_user.username} ({backup.replace('_', ' ')})")
    await callback.message.reply(f"Database restored from backup `{backup.replace('_', ' ')}`")   
    await callback.answer()

@router.callback_query(F.data == "tg_restore")
async def cb_tg_restore(callback: types.CallbackQuery) -> None:
    """Perform restore from Telegram"""
    #TODO:
    pass

@router.message(F.is_media_group & F.content_type==types.ContentType.DOCUMENT)
@media_group_handler
async def cb_tg_restore_files(message: types.Message) -> None:
    """Perform restore from Telegram files"""
    #TODO:
    pass
