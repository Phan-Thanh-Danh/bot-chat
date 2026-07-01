import logging
import os
import sys

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


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("discord").setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.WARNING)


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resolve_dotenv_path(app_dir):
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.extend(
            [
                os.path.join(app_dir, ".env"),
                os.path.join(getattr(sys, "_MEIPASS", app_dir), ".env"),
                os.path.join(os.getcwd(), ".env"),
            ]
        )
    else:
        candidates.extend(
            [
                os.path.join(app_dir, ".env"),
                os.path.join(os.getcwd(), ".env"),
            ]
        )

    for path in candidates:
        if path and os.path.isfile(path):
            return path

    return os.path.join(app_dir, ".env")


configure_logging()
logger = logging.getLogger("bot")

APP_DIR = get_app_dir()
os.chdir(APP_DIR)

# Load environment variables from the bundled .env if available, otherwise fall back to the app folder
DOTENV_PATH = resolve_dotenv_path(APP_DIR)
load_dotenv(dotenv_path=DOTENV_PATH)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DISCORD_TOKEN or not GROQ_API_KEY:
    logger.error("DISCORD_TOKEN and GROQ_API_KEY must be set in %s", DOTENV_PATH)
    sys.exit(1)

# Initialize Database and Groq
os.makedirs(os.path.join(APP_DIR, "data"), exist_ok=True)
db_path = os.path.join(APP_DIR, "data", "bot.db")
db = Database(db_path=db_path)
groq = GroqClient(api_key=GROQ_API_KEY)

logger.info("App directory: %s", APP_DIR)
logger.info("Database path: %s", db_path)

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
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    logger.info("Connected to %d guilds", len(bot.guilds))

    # Load custom roles from DB into ROLES dict
    custom_roles = await db.load_custom_roles()
    ROLES.update(custom_roles)
    if custom_roles:
        logger.info("Loaded %d custom role(s) from database: %s", len(custom_roles), list(custom_roles.keys()))

    # Load cogs
    await bot.add_cog(Chat(bot, db, groq))
    await bot.add_cog(Roles(bot, db))
    await bot.add_cog(Utility(bot, db, groq))
    await bot.add_cog(Scheduler(bot, db, groq))
    logger.info("All cogs loaded successfully.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    logger.error("Command error: %s", error)
    await ctx.reply("Xin lỗi, đã có lỗi xảy ra khi thực hiện lệnh này.")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
