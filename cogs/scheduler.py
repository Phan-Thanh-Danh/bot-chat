import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from core.database import Database
from core.groq_client import GroqClient
from core.role_config import ROLES

class Scheduler(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database, groq: GroqClient):
        self.bot = bot
        self.db = db
        self.groq = groq
        self.scheduler = AsyncIOScheduler()

    async def cog_load(self):
        """Start scheduler when cog loads."""
        self.scheduler.add_job(self.send_morning_message, 'cron', hour=9, minute=0)
        self.scheduler.add_job(self.send_evening_message, 'cron', hour=22, minute=0)
        self.scheduler.start()

    async def cog_unload(self):
        """Shutdown scheduler when cog unloads."""
        self.scheduler.shutdown()

    async def _send_broadcast(self, prompt_instruction: str):
        active_users = await self.db.get_all_active_users(days=3)
        for discord_id in active_users:
            user = await self.db.get_or_create_user(discord_id)
            current_role = user['current_role']
            role_config = ROLES.get(current_role, ROLES['default'])
            
            system_prompt = f"{role_config['system_prompt']}\n\n{prompt_instruction}"
            try:
                response_text = await self.groq.generate("Generate message", system_instruction=system_prompt)
                
                discord_user = await self.bot.fetch_user(int(discord_id))
                if discord_user:
                    await discord_user.send(response_text)
                    
            except Exception:
                pass
                
            await asyncio.sleep(1)

    async def send_morning_message(self):
        """Send morning greetings."""
        prompt = "Hãy gửi một tin nhắn chào buổi sáng ngắn gọn, thân thiện, tự nhiên. Hỏi thăm ngày hôm nay của họ. Tối đa 2 câu. Theo đúng tính cách của role."
        await self._send_broadcast(prompt)

    async def send_evening_message(self):
        """Send evening greetings."""
        prompt = "Hãy gửi một tin nhắn hỏi thăm buổi tối ngắn gọn. Hỏi hôm nay của họ thế nào, có gì vui không. Tối đa 2 câu. Theo đúng tính cách của role."
        await self._send_broadcast(prompt)

def setup(bot):
    pass
