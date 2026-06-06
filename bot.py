import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
keep_alive()
from core.database import Database
from core.groq_client import GroqClient

from cogs.chat import Chat
from cogs.roles import Roles
from cogs.utility import Utility
from cogs.scheduler import Scheduler
from core.role_config import ROLES

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DISCORD_TOKEN or not GROQ_API_KEY:
    print("Error: DISCORD_TOKEN and GROQ_API_KEY must be set in .env file.")
    exit(1)

# Initialize Database and Groq
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data", "bot.db")
db = Database(db_path=db_path)
groq = GroqClient(api_key=GROQ_API_KEY)

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    # Initialize database when bot is ready
    await db.init_db()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Connected to {len(bot.guilds)} guilds")

    # Load custom roles from DB into ROLES dict
    custom_roles = await db.load_custom_roles()
    ROLES.update(custom_roles)
    if custom_roles:
        print(f"Loaded {len(custom_roles)} custom role(s) from database: {list(custom_roles.keys())}")
    
    # Load cogs
    await bot.add_cog(Chat(bot, db, groq))
    await bot.add_cog(Roles(bot, db))
    await bot.add_cog(Utility(bot, db, groq))
    await bot.add_cog(Scheduler(bot, db, groq))
    print("All cogs loaded successfully.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Command Error: {error}")
    await ctx.reply("Xin lỗi, đã có lỗi xảy ra khi thực hiện lệnh này.")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
