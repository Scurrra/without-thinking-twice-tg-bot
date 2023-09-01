from main import db_connect

import json
from pathlib import Path
from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.types.input_media_document import InputMediaDocument

router = Router()

@router.message(Command("backup"))
async def cmd_backup(message: types.Message) -> None:
    """Start a backup with a command /backup"""
    db = await db_connect()
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
    db = await db_connect()
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

    await callback.message.reply(f"Database was backuped at {now.strftime('%d.%m.%Y, %H:%M:%S')}")
    await callback.answer()

@router.callback_query(F.data == "tg_backup")
async def cb_tg_backup(callback: types.CallbackQuery) -> None:
    """Perform local & telegram backup"""
    db = await db_connect()
    path = Path("data/backups")
    if not path.exists():
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
    await callback.message.answer_media_group(media=[
        InputMediaDocument(media=FSInputFile(path / "interviewers.json")),
        InputMediaDocument(media=FSInputFile(path / "interviewees.json")),
        InputMediaDocument(media=FSInputFile(path / "tests.json"))
    ])
    await callback.message.reply(f"Database was backuped at {now.strftime('%d.%m.%Y, %H:%M:%S')}")
    await callback.answer()

@router.message(Command("restore"))
async def cmd_restore(message: types.Message) -> None:
    """Start a restore with a command /restore"""
    db = await db_connect()
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
        backup.parts()[-1]
        for backup in path.iterdir()
        if backup.isdir()
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
    callback.answer()

@router.callback_query(F.data.startswith("backup_"))
async def cb_local_restore_backup(callback: types.CallbackQuery) -> None:
    """Restore specified backup"""
    #TODO: 
    pass

@router.callback_query(F.data == "tg_restore")
async def cb_tg_restore(callback: types.CallbackQuery) -> None:
    """Perform restore from Telegram"""
    #TODO:
    pass

@router.callback_query(F.data)
async def cb_tg_restore_files(callback: types.CallbackQuery) -> None:
    """Perform restore from Telegram files"""
    #TODO:
    pass
