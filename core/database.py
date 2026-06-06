import aiosqlite
import os

class Database:
    def __init__(self, db_path: str = "data/bot.db"):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    discord_id TEXT UNIQUE,
                    current_role TEXT DEFAULT 'default',
                    intimacy_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    discord_id TEXT,
                    role TEXT,
                    content TEXT,
                    is_bot INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS custom_roles (
                    key TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    system_prompt TEXT NOT NULL,
                    greeting TEXT NOT NULL
                )
            ''')
            await db.commit()

    async def get_or_create_user(self, discord_id: str) -> dict:
        """Get user record, create if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
            user = await cursor.fetchone()
            
            if not user:
                await db.execute('INSERT INTO users (discord_id) VALUES (?)', (discord_id,))
                await db.commit()
                cursor = await db.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
                user = await cursor.fetchone()
            
            return dict(user)

    async def get_user(self, discord_id: str) -> dict | None:
        """Get user record, return None if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
            user = await cursor.fetchone()
            return dict(user) if user else None

    async def update_role(self, discord_id: str, role: str) -> None:
        """Update current_role for user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('UPDATE users SET current_role = ? WHERE discord_id = ?', (role, discord_id))
            await db.commit()

    async def add_message(self, discord_id: str, content: str, is_bot: bool) -> None:
        """Insert new message and keep only the last 20 messages for the user."""
        async with aiosqlite.connect(self.db_path) as db:
            role = 'model' if is_bot else 'user'
            await db.execute(
                'INSERT INTO messages (discord_id, role, content, is_bot) VALUES (?, ?, ?, ?)',
                (discord_id, role, content, int(is_bot))
            )
            
            await db.execute('''
                DELETE FROM messages 
                WHERE discord_id = ? AND id NOT IN (
                    SELECT id FROM messages 
                    WHERE discord_id = ? 
                    ORDER BY id DESC 
                    LIMIT 20
                )
            ''', (discord_id, discord_id))
            
            await db.commit()

    async def get_history(self, discord_id: str) -> list[dict]:
        """Get 20 most recent messages, ordered oldest to newest."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT content, is_bot 
                FROM messages 
                WHERE discord_id = ? 
                ORDER BY id DESC 
                LIMIT 20
            ''', (discord_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in reversed(rows)]

    async def increment_intimacy(self, discord_id: str, points: int = 1) -> int:
        """Increment intimacy_score and return new value."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users 
                SET intimacy_score = intimacy_score + ? 
                WHERE discord_id = ?
            ''', (points, discord_id))
            await db.commit()
            
            cursor = await db.execute('SELECT intimacy_score FROM users WHERE discord_id = ?', (discord_id,))
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_all_active_users(self, days: int = 3) -> list[str]:
        """Get discord_ids of users who sent a message in the last n days."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT DISTINCT discord_id 
                FROM messages 
                WHERE is_bot = 0 AND created_at >= datetime('now', ?)
            ''', (f'-{days} days',))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def load_custom_roles(self) -> dict:
        """Load all custom roles from DB and return as ROLES-format dict."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM custom_roles')
            rows = await cursor.fetchall()
            return {
                row['key']: {
                    'name': row['name'],
                    'system_prompt': row['system_prompt'],
                    'greeting': row['greeting']
                }
                for row in rows
            }

    async def save_custom_role(self, key: str, name: str, system_prompt: str, greeting: str) -> None:
        """Save or update a custom role in DB."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO custom_roles (key, name, system_prompt, greeting) VALUES (?, ?, ?, ?)',
                (key, name, system_prompt, greeting)
            )
            await db.commit()

    async def delete_custom_role(self, key: str) -> bool:
        """Delete a custom role from DB. Returns True if deleted, False if not found."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM custom_roles WHERE key = ?', (key,))
            await db.commit()
            return cursor.rowcount > 0
