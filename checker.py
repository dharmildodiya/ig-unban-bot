import aiohttp
import asyncio
import random
from proxy_manager import ProxyManager

proxy_manager = ProxyManager()

HEADERS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 13)"
]

def analyze_response(status, text):
    score = 0

    if status == 200:
        score += 3

    if '"username"' in text:
        score += 3

    if '"profile_pic_url"' in text:
        score += 2

    if "profilePage" in text:
        score += 2

    if "Sorry, this page isn't available" in text:
        score -= 6

    if "Page Not Found" in text:
        score -= 6

    if "login" in text.lower():
        score -= 2

    if status == 404:
        return "not_found"

    if status == 429:
        return "rate_limited"

    if score >= 6:
        return "active"
    elif score <= -3:
        return "banned"
    else:
        return "uncertain"


async def check_account(username):
    url = f"https://www.instagram.com/{username}/"
    proxy = proxy_manager.get_proxy()

    headers = {
        "User-Agent": random.choice(HEADERS_LIST),
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                url,
                headers=headers,
                proxy=proxy,
                allow_redirects=True
            ) as res:

                text = await res.text()

                print(f"[{username}] status: {res.status} proxy: {proxy}")

                return analyze_response(res.status, text)

    except Exception as e:
        print(f"[{username}] ERROR:", e)
        return "error"
