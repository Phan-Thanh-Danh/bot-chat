# Discord Gemini Bot

A Discord bot built with Python that integrates the Gemini API. It features multi-personalities, per-user memory, image reading, channel summarization, an intimacy system, and scheduled active messaging.

## Setup Instructions

1. Clone the repository and create a virtual environment:
   ```bash
   git clone <repo_url> discord-gemini-bot
   cd discord-gemini-bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys and configuration values:
   ```bash
   cp .env.example .env
   ```
4. Obtain your Discord Token from the [Discord Developer Portal](https://discord.com/developers/applications) and your Gemini API Key from [Google AI Studio](https://aistudio.google.com/). Fill these in your `.env` file.
5. Run the bot:
   ```bash
   python bot.py
   ```

## Build Windows EXE

1. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Install PyInstaller and build the EXE:
   ```powershell
   .\build_exe.ps1
   ```
3. The executable will be created in the `dist` folder.
4. The `.env` file is bundled into the EXE, so you can send a single executable file. The bot will also store its database in the same folder as the EXE.

## Direct download

Click the link below to download the single `discord-gemini-bot.exe` executable. This link is a Downloads (release asset) URL — when you upload `discord-gemini-bot.exe` to a GitHub Release (for example `v1.0`), clicking this will immediately download the file.

- Release asset (recommended): https://github.com/Phan-Thanh-Danh/bot-chat/releases/download/v1.0/discord-gemini-bot.exe

Fallback (if you commit the file to `main` — not recommended for large binaries):

- Raw file: https://raw.githubusercontent.com/Phan-Thanh-Danh/bot-chat/main/dist/discord-gemini-bot.exe

To upload the executable as a release asset (recommended), run:

```bash
# create release and upload in one step
gh release create v1.0 dist/discord-gemini-bot.exe --title "v1.0" --notes "Stable build"

# or, if release exists, upload the asset
gh release upload v1.0 dist/discord-gemini-bot.exe
```

If you want, I can run the `gh` commands from here (requires `gh` logged-in on this machine) or generate a drop-in GitHub Actions workflow to publish builds automatically.

## Available Commands

- `!setrole <role_name>`: Change the bot's personality for you.
- `!roles`: List all available personalities.
- `!me`: View your current profile, intimacy score, and chat statistics.
- `!summary [n]`: Summarize the last `n` messages in the channel (default 50).
- `!reset`: Clear your chat history with the bot.
