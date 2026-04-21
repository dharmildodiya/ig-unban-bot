import asyncio
import datetime
import random
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import BOT_TOKEN, CHECK_INTERVAL
from database import *
from checker import check_account
from notifier import send_unban
from utils import log

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def extract_usernames(text):
    usernames = set()
    parts = text.split()

    for part in parts:
        if "instagram.com/" in part:
            part = part.split("instagram.com/")[-1]

        part = part.replace("@", "").strip("/")

        if part:
            usernames.add(part)

    return list(usernames)


@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🚀 Unban Monitor Bot Active")


@dp.message(Command("cancel"))
async def cancel(msg: types.Message):
    await msg.answer("❌ Cancelled")


@dp.message(Command("add"))
async def add(msg: types.Message):
    text = msg.text.replace("/add", "").strip()
    usernames = extract_usernames(text)

    added = []
    for username in usernames:
        await add_account(username, msg.from_user.id)
        added.append(f"@{username}")

    await msg.answer("✅ Tracking:\n" + "\n".join(added))


@dp.message(Command("remove"))
async def remove(msg: types.Message):
    username = msg.text.split(" ")[1].replace("@", "")
    await remove_account(username, msg.from_user.id)
    await msg.answer(f"❌ Removed @{username}")


@dp.message(Command("list"))
async def list_accounts(msg: types.Message):
    accounts = await get_user_accounts(msg.from_user.id)

    if not accounts:
        return await msg.answer("No accounts tracked")

    text = "\n".join([f"@{a[1]} | {a[3]}" for a in accounts])
    await msg.answer(text)


async def confirm_active(username):
    confirmations = 0

    for _ in range(3):
        await asyncio.sleep(random.uniform(2, 4))
        result = await check_account(username)

        if result == "active":
            confirmations += 1

    return confirmations >= 2


async def monitor():
    while True:
        try:
            print("🔍 Checking accounts...")
            accounts = await get_accounts()
            now = datetime.datetime.now()

            for acc in accounts:
                id, username, user_id, status, added_at, banned_at, last_checked, unbanned_at, notified = acc

                # delete after 7 days
                if added_at:
                    added_time = datetime.datetime.fromisoformat(added_at)
                    if (now - added_time).days >= 7:
                        await delete_account(id)
                        continue

                result = await check_account(username)
                await update_status(id, result)

                print(f"{username} → {result}")

                if status in ["banned", "unknown"] and result == "active" and not notified:

                    is_real = await confirm_active(username)

                    if is_real:
                        start_time = datetime.datetime.fromisoformat(banned_at) if banned_at else datetime.datetime.fromisoformat(added_at)

                        await send_unban(user_id, username, start_time)
                        await mark_unbanned(id)
                        await delete_account(id)

        except Exception as e:
            print("Monitor error:", e)

        await asyncio.sleep(CHECK_INTERVAL)


async def main():
    print("🔥 BOT STARTED")

    await init_db()

    await asyncio.gather(
        monitor(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print("CRASH:", e)
            asyncio.sleep(5)
