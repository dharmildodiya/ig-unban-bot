from aiogram import Bot
from config import BOT_TOKEN
import datetime
import pytz

bot = Bot(token=BOT_TOKEN)

async def send_unban(user_id, username, start_time):
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(IST)

    duration = now - start_time

    message = f"""🏆 <b>ACCOUNT RECOVERED</b> ✅

👤 <b>@{username}</b>

⏱ <b>Time Taken:</b> {str(duration).split('.')[0]}

🕒 <b>Unbanned At:</b> {now.strftime('%I:%M %p | %d %b %Y')}

🔗 https://instagram.com/{username}
"""

    await bot.send_message(user_id, message, parse_mode="HTML")
