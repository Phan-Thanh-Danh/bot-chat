import discord
from discord.ext import commands
from core.database import Database
from core.groq_client import GroqClient
from core.role_config import ROLES
from utils.helpers import download_image, chunk_text, is_image_attachment

class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database, groq: GroqClient):
        self.bot = bot
        self.db = db
        self.groq = groq

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = self.bot.user in message.mentions
        
        if not (is_dm or is_mentioned):
            return

        discord_id = str(message.author.id)
        user = await self.db.get_or_create_user(discord_id)
        
        has_image_attachment = False
        image_bytes = None
        image_mime = None
        if message.attachments:
            for attachment in message.attachments:
                if is_image_attachment(attachment):
                    has_image_attachment = True
                    image_bytes = await download_image(attachment.url)
                    image_mime = attachment.content_type
                    break

        content = message.content
        if is_mentioned:
            content = content.replace(f'<@{self.bot.user.id}>', '').strip()
            content = content.replace(f'<@!{self.bot.user.id}>', '').strip()

        if not content and not has_image_attachment:
            return

        if not content and has_image_attachment and not image_bytes:
            content = "Hãy mô tả và phân tích ảnh này cho tôi."

        await self.db.add_message(discord_id, content, is_bot=False)
        new_intimacy = await self.db.increment_intimacy(discord_id, points=1)
        history = await self.db.get_history(discord_id)
        
        current_role = user['current_role']
        role_config = ROLES.get(current_role, ROLES['default'])
        
        async with message.channel.typing():
            try:
                response_text = await self.groq.chat(
                    user_id=discord_id,
                    message=content,
                    role_config=role_config,
                    history=history,
                    intimacy_score=new_intimacy,
                    image_bytes=image_bytes,
                    mime_type=image_mime
                )
                
                chunks = chunk_text(response_text)
                for chunk in chunks:
                    await message.reply(chunk)
                    
                await self.db.add_message(discord_id, response_text, is_bot=True)
                
            except Exception as e:
                await message.reply(str(e))

def setup(bot):
    pass
