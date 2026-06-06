import discord
import os
from discord.ext import commands
from core.database import Database
from core.role_config import ROLES

class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database):
        self.bot = bot
        self.db = db

    # ─────────────────── !help ───────────────────
    @commands.command(name="help")
    async def help(self, ctx: commands.Context):
        """Hiển thị danh sách lệnh."""
        embed = discord.Embed(
            title="📖 Danh sách lệnh",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="💬 Chat",
            value=(
                "`@bot <tin nhắn>` — Chat với bot trong server\n"
                "`DM` — Chat riêng với bot"
            ),
            inline=False
        )
        embed.add_field(
            name="🎭 Nhân cách",
            value=(
                "`!roles` — Xem danh sách nhân cách\n"
                "`!setrole <mã>` — Đổi nhân cách\n"
                "`!me` — Xem hồ sơ của bạn"
            ),
            inline=False
        )

        owner_id = os.getenv("OWNER_ID")
        if owner_id and str(ctx.author.id) == owner_id:
            embed.add_field(
                name="🔧 Quản trị (Owner only)",
                value=(
                    "`!addpersonality <mã> <tên> | <mô tả>` — Thêm nhân cách mới\n"
                    "`!delpersonality <mã>` — Xóa nhân cách"
                ),
                inline=False
            )

        embed.set_footer(text="Bot bởi CHAT • Dùng !roles để đổi nhân cách")
        await ctx.reply(embed=embed)

    # ─────────────────── !setrole ───────────────────
    @commands.command(name="setrole")
    async def setrole(self, ctx: commands.Context, role_name: str = None):
        """Set your bot personality."""
        if role_name not in ROLES:
            await ctx.reply("Role không hợp lệ. Các role có sẵn: " + ", ".join(ROLES.keys()))
            return

        discord_id = str(ctx.author.id)
        await self.db.get_or_create_user(discord_id)
        await self.db.update_role(discord_id, role_name)

        greeting = ROLES[role_name]["greeting"]
        await ctx.reply(greeting)

    # ─────────────────── !roles ───────────────────
    @commands.command(name="roles")
    async def roles(self, ctx: commands.Context):
        """List all available personalities."""
        discord_id = str(ctx.author.id)
        user = await self.db.get_or_create_user(discord_id)
        current_role = user["current_role"]

        embed = discord.Embed(title="🎭 Danh sách nhân cách", color=discord.Color.blue())
        for key, role in ROLES.items():
            name = role["name"]
            if key == current_role:
                name = f"✅ {name}"
            desc = role["system_prompt"].split(".")[0] + "."
            embed.add_field(name=name, value=f"Key: `{key}`\n{desc}", inline=False)

        embed.set_footer(text="Dùng !setrole <tên> để đổi nhân cách")
        await ctx.reply(embed=embed)

    # ─────────────────── !me ───────────────────
    @commands.command(name="me")
    async def me(self, ctx: commands.Context):
        """View your profile."""
        discord_id = str(ctx.author.id)
        user = await self.db.get_or_create_user(discord_id)

        score = user["intimacy_score"]
        if score <= 50:
            intimacy_level = "Mới quen"
        elif score <= 200:
            intimacy_level = "Khá thân"
        else:
            intimacy_level = "Thân thiết"

        current_role = user["current_role"]
        role_name = ROLES.get(current_role, ROLES["default"])["name"]

        import aiosqlite
        async with aiosqlite.connect(self.db.db_path) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM messages WHERE discord_id = ?', (discord_id,))
            row = await cursor.fetchone()
            msg_count = row[0] if row else 0

        embed = discord.Embed(title=f"Hồ sơ của {ctx.author.display_name}", color=discord.Color.green())
        embed.set_thumbnail(url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        embed.add_field(name="Nhân cách hiện tại", value=role_name, inline=True)
        embed.add_field(name="Điểm thân mật", value=str(score), inline=True)
        embed.add_field(name="Cấp độ", value=intimacy_level, inline=True)
        embed.add_field(name="Tin nhắn lưu trữ", value=str(msg_count), inline=True)

        await ctx.reply(embed=embed)

    # ─────────────────── !addpersonality ───────────────────
    @commands.command(name="addpersonality")
    async def addpersonality(self, ctx: commands.Context, key: str = None, *, rest: str = None):
        """Add a new personality (Owner only). Format: !addpersonality <key> <name> | <system_prompt>"""
        owner_id = os.getenv("OWNER_ID")
        if not owner_id or str(ctx.author.id) != owner_id:
            await ctx.reply("Lệnh này chỉ dành cho Owner.")
            return

        if not key or not rest or "|" not in rest:
            await ctx.reply("Sai cú pháp. Cú pháp: `!addpersonality <mã> <tên> | <mô tả tính cách>`")
            return

        name, system_prompt = [x.strip() for x in rest.split("|", 1)]
        greeting = f"Xin chào, tôi là {name}!"

        # Lưu vào DB (vĩnh viễn, không mất khi restart)
        await self.db.save_custom_role(key, name, system_prompt, greeting)

        # Cập nhật ROLES trong memory ngay lập tức
        ROLES[key] = {
            "name": name,
            "system_prompt": system_prompt,
            "greeting": greeting
        }

        # Tự động kích hoạt nhân cách mới cho người dùng
        discord_id = str(ctx.author.id)
        await self.db.get_or_create_user(discord_id)
        await self.db.update_role(discord_id, key)

        embed = discord.Embed(
            title="✅ Thêm nhân cách thành công!",
            color=discord.Color.green()
        )
        embed.add_field(name="Mã", value=f"`{key}`", inline=True)
        embed.add_field(name="Tên", value=name, inline=True)
        embed.add_field(name="Trạng thái", value="🟢 Đang hoạt động", inline=True)
        embed.add_field(name="Mô tả", value=system_prompt[:200] + ("..." if len(system_prompt) > 200 else ""), inline=False)
        embed.set_footer(text="Nhân cách đã được kích hoạt và lưu vĩnh viễn • Dùng !delpersonality để xóa")
        await ctx.reply(embed=embed)

    # ─────────────────── !delpersonality ───────────────────
    @commands.command(name="delpersonality")
    async def delpersonality(self, ctx: commands.Context, key: str = None):
        """Remove a personality (Owner only). Format: !delpersonality <key>"""
        owner_id = os.getenv("OWNER_ID")
        if not owner_id or str(ctx.author.id) != owner_id:
            await ctx.reply("Lệnh này chỉ dành cho Owner.")
            return

        if not key:
            await ctx.reply("Vui lòng nhập mã nhân cách cần xóa. Cú pháp: `!delpersonality <mã>`")
            return

        if key == "default":
            await ctx.reply("❌ Không thể xóa nhân cách mặc định (`default`).")
            return

        if key not in ROLES:
            await ctx.reply(f"❌ Không tìm thấy nhân cách nào có mã: `{key}`\nDùng `!roles` để xem danh sách.")
            return

        # Xóa khỏi DB
        await self.db.delete_custom_role(key)

        # Xóa khỏi ROLES trong memory
        role_name = ROLES[key]["name"]
        del ROLES[key]

        # Nếu ai đang dùng role này → reset về default
        embed = discord.Embed(
            title="🗑️ Đã xóa nhân cách",
            color=discord.Color.red()
        )
        embed.add_field(name="Mã đã xóa", value=f"`{key}`", inline=True)
        embed.add_field(name="Tên", value=role_name, inline=True)
        embed.set_footer(text="Người dùng đang dùng nhân cách này sẽ tự động về mặc định")
        await ctx.reply(embed=embed)

def setup(bot):
    pass
