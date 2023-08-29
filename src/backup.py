from . import db

import json
import os
from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.types.input_media_document import InputMediaDocument

router = Router()

@router.message(Command("backup"))
async def cmd_backup(message: types.Message) -> None:
    """Start a backup with a command /backup"""
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
    if not os.path.isdir("../data/backups"):
        os.mkdir("../data/backups")

    now = datetime.now()
    path = f"../data/backups/{now.strftime('%d.%m.%Y_%H:%M:%S')}"
    os.mkdir(path)

    interviewers = await db.select("interviewers")
    interviewees = await db.select("interviewees")
    tests = await db.select("tests")

    with open(f"{path}/interviewers.json", "w") as interviewers_file:
        json.dump(interviewers, interviewers_file)
    with open(f"{path}/interviewees.json", "w") as interviewees_file:
        json.dump(interviewees, interviewees_file)
    with open(f"{path}/tetss.json", "w") as tests_file:
        json.dump(tests, tests_file)

    await callback.message.reply(f"Database was backuped at {now.strftime('%d.%m.%Y, %H:%M:%S')}")
    await callback.answer()

@router.callback_query(F.data == "tg_backup")
async def cb_tg_backup(callback: types.CallbackQuery) -> None:
    """Perform local & telegram backup"""
    if not os.path.isdir("../data/backups"):
        os.mkdir("../data/backups")

    now = datetime.now()
    path = f"../data/backups/{now.strftime('%d.%m.%Y_%H:%M:%S')}"
    os.mkdir(path)

    interviewers = await db.select("interviewers")
    interviewees = await db.select("interviewees")
    tests = await db.select("tests")
    
    with open(f"{path}/interviewers.json", "w") as interviewers_file:
        json.dump(interviewers, interviewers_file)
        await callback.message.answer_document(interviewers_file, caption="Interviewers data")
    with open(f"{path}/interviewees.json", "w") as interviewees_file:
        json.dump(interviewees, interviewees_file)
        await callback.message.answer_document(interviewees_file, caption="Interviewees data")
    with open(f"{path}/tetss.json", "w") as tests_file:
        json.dump(tests, tests_file)
        await callback.message.answer_document(tests_file, caption="Tests data")
    callback.message.answer_media_group(media=[
        InputMediaDocument(f"{path}/interviewers.json"),
        InputMediaDocument(f"{path}/interviewees.json"),
        InputMediaDocument(f"{path}/tests.json"),
    ])
    await callback.message.reply(f"Database was backuped at {now.strftime('%d.%m.%Y, %H:%M:%S')}")
    await callback.answer()

@router.message(Command("restore"))
async def cmd_restore(message: types.Message) -> None:
    """Start a restore with a command /restore"""
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
    backups = [
        os.path.basename(os.path.normpath(backup))
        for backup in os.scandir("../data/backups")
        if os.path.isdir(backup)
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
