import aiosqlite
import hashlib
from datetime import datetime, timedelta

from config import DATABASE_NAME, KEEP_DAYS


async def init_database():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT NOT NULL,
            media_id TEXT,
            message_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_hash
        ON messages(hash)
        """)

        await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_media
        ON messages(media_id)
        """)

        await db.commit()


def calculate_hash(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


async def exists_hash(hash_value: str):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute(
            "SELECT id FROM messages WHERE hash=? LIMIT 1",
            (hash_value,)
        )

        row = await cursor.fetchone()

        return row is not None


async def exists_media(media_id: str):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute(
            "SELECT id FROM messages WHERE media_id=? LIMIT 1",
            (media_id,)
        )

        row = await cursor.fetchone()

        return row is not None


async def save_hash(hash_value: str, message_type: str):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute(
            """
            INSERT INTO messages
            (hash, media_id, message_type, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                hash_value,
                None,
                message_type,
                datetime.utcnow().isoformat()
            )
        )

        await db.commit()


async def save_media(media_id: str, message_type: str):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute(
            """
            INSERT INTO messages
            (hash, media_id, message_type, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                "",
                media_id,
                message_type,
                datetime.utcnow().isoformat()
            )
        )

        await db.commit()


async def clean_old_messages():
    limit = (
        datetime.utcnow() -
        timedelta(days=KEEP_DAYS)
    ).isoformat()

    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute(
            "DELETE FROM messages WHERE created_at < ?",
            (limit,)
        )

        await db.commit()
