from aiogram import Bot
from config import BOT_TOKEN
import datetime

bot = Bot(token=BOT_TOKEN)

async def send_unban(user_id, username, start_time):
    now = datetime.datetime.now()
    duration = now - start_time

    message = f"""Account Recovered | @{username} 🏆✅
⏱ Time Taken: {str(duration).split('.')[0]}
Unbanned at {now.strftime('%Y-%m-%d %H:%M:%S IST')}
https://instagram.com/{username}"""

    await bot.send_message(user_id, message)
