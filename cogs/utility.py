import discord
from discord.ext import commands
import aiosqlite
from core.database import Database
from core.groq_client import GroqClient
from utils.helpers import format_history_for_summary

class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database, groq: GroqClient):
        self.bot = bot
        self.db = db
        self.groq = groq

    @commands.command(name="summary")
    async def summary(self, ctx: commands.Context, n: int = 50):
        """Summarize the last n messages in the channel."""
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.reply("❌ Lệnh `!summary` chỉ hoạt động trong kênh server, không dùng trong DM.")
            return

        n = max(10, min(100, n))

        async with ctx.typing():
            messages = []
            async for msg in ctx.channel.history(limit=n):
                messages.append(msg)

            messages.reverse()
            formatted_history = format_history_for_summary(messages)

            prompt = f"Tóm tắt cuộc trò chuyện sau theo dạng bullet point ngắn gọn bằng tiếng Việt. Nêu các chủ đề chính và sự kiện nổi bật. Tối đa 10 bullet points. Bỏ qua các tin nhắn của bot.\n\n{formatted_history}"

            try:
                response_text = await self.groq.generate(prompt)

                embed = discord.Embed(
                    title=f"📋 Tóm tắt kênh #{ctx.channel.name}",
                    description=response_text,
                    color=0x3498db
                )
                embed.set_footer(text=f"Tóm tắt từ {n} tin nhắn gần nhất")
                await ctx.reply(embed=embed)
            except Exception:
                await ctx.reply("Xin lỗi, không thể tóm tắt lúc này.")

    @commands.command(name="reset")
    async def reset(self, ctx: commands.Context):
        """Clear your chat history."""
        discord_id = str(ctx.author.id)
        import aiosqlite
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute('DELETE FROM messages WHERE discord_id = ?', (discord_id,))
            await db.commit()
            
        await ctx.reply("✅ Đã xóa lịch sử trò chuyện. Chúng ta bắt đầu lại nhé!")

def setup(bot):
    pass
