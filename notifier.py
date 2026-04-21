from aiogram import Bot
from config import BOT_TOKEN
import datetime
import pytz

bot = Bot(token=BOT_TOKEN)

async def send_unban(user_id, username, start_time):
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(IST)

    if start_time.tzinfo is None:
        start_time = IST.localize(start_time)

    duration = now - start_time

    message = f"""Account Recovered | @{username} 🏆✅
⏱ Time Taken: {str(duration).split('.')[0]}
Unbanned at {now.strftime('%Y-%m-%d %I:%M:%S %p IST')}
https://instagram.com/{username}"""

    await bot.send_message(user_id, message)
