import asyncio
import datetime
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import BOT_TOKEN, CHECK_INTERVAL
from database import *
from checker import check_account
from notifier import send_unban
from utils import log

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ✅ COMMANDS

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🚀 Unban Monitor Bot Active")


@dp.message(Command("add"))
async def add(msg: types.Message):
    try:
        username = msg.text.split(" ")[1].replace("@", "")
        await add_account(username, msg.from_user.id)
        await msg.answer(f"✅ Tracking @{username}")
    except:
        await msg.answer("Usage: /add username")


@dp.message(Command("remove"))
async def remove(msg: types.Message):
    try:
        username = msg.text.split(" ")[1].replace("@", "")
        await remove_account(username, msg.from_user.id)
        await msg.answer(f"❌ Removed @{username}")
    except:
        await msg.answer("Usage: /remove username")


@dp.message(Command("list"))
async def list_accounts(msg: types.Message):
    accounts = await get_user_accounts(msg.from_user.id)

    if not accounts:
        return await msg.answer("No accounts tracked")

    text = "\n".join([f"@{a[1]} | {a[3]}" for a in accounts])
    await msg.answer(text)


# 🔁 CONFIRMATION SYSTEM (prevents false alerts)

async def confirm_active(username):
    confirmations = 0

    for _ in range(3):
        await asyncio.sleep(random.uniform(2, 4))
        result = await check_account(username)

        if result == "active":
            confirmations += 1

    return confirmations >= 2


# 🔄 MONITOR ENGINE

async def monitor():
    while True:
        try:
            accounts = await get_accounts()

            for acc in accounts:
                id, username, user_id, status, added_at, last_checked, unbanned_at, notified = acc

                result = await check_account(username)
                await update_status(id, result)

                # 🔥 Detect unban
                if status in ["banned", "unknown"] and result == "active" and not notified:

                    is_real = await confirm_active(username)

                    if is_real:
                        start_time = datetime.datetime.fromisoformat(added_at)

                        await send_unban(user_id, username, start_time)
                        await mark_unbanned(id)

                        log(f"{username} unbanned")

        except Exception as e:
            log(f"Monitor error: {str(e)}")

        await asyncio.sleep(CHECK_INTERVAL)


# 🚀 MAIN START

async def main():
    await init_db()

    # start background monitor
    asyncio.create_task(monitor())

    # start bot polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print("CRASH:", e)
            asyncio.sleep(5)
