import aiosqlite
import datetime

DB = "data.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            username TEXT,
            user_id INTEGER,
            status TEXT,
            added_at TEXT,
            banned_at TEXT,
            last_checked TEXT,
            unbanned_at TEXT,
            notified INTEGER DEFAULT 0
        )
        """)
        await db.commit()


async def add_account(username, user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT INTO accounts (username, user_id, status, added_at)
        VALUES (?, ?, 'unknown', ?)
        """, (username, user_id, str(datetime.datetime.now())))
        await db.commit()


async def remove_account(username, user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM accounts WHERE username=? AND user_id=?", (username, user_id))
        await db.commit()


async def delete_account(id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM accounts WHERE id=?", (id,))
        await db.commit()


async def get_accounts():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute("SELECT * FROM accounts")
        return await cursor.fetchall()


async def get_user_accounts(user_id):
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute("SELECT * FROM accounts WHERE user_id=?", (user_id,))
        return await cursor.fetchall()


async def update_status(id, status):
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute("SELECT status, banned_at FROM accounts WHERE id=?", (id,))
        row = await cursor.fetchone()

        current_status, banned_at = row
        now = str(datetime.datetime.now())

        # ✅ only mark banned_at when it FIRST becomes banned
        if status == "banned" and current_status != "banned":
            await db.execute("""
            UPDATE accounts 
            SET status=?, banned_at=?, last_checked=? 
            WHERE id=?
            """, (status, now, now, id))

        else:
            await db.execute("""
            UPDATE accounts 
            SET status=?, last_checked=? 
            WHERE id=?
            """, (status, now, id))

        await db.commit()


async def mark_unbanned(id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        UPDATE accounts SET unbanned_at=?, notified=1 WHERE id=?
        """, (str(datetime.datetime.now()), id))
        await db.commit()
