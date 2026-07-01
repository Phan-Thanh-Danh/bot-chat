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

## Direct downloads

Clicking the links below will start a direct download when the files are hosted as release assets or served over HTTP.

| Platform | Architecture | Download |
|---|---:|---|
| Windows | x64 (64-bit) | [Download (win-x64) — release asset](https://github.com/OWNER/REPO/releases/download/vX.Y/discord-gemini-bot-windows-x64.exe) |
| Windows | x86 (32-bit) | [Download (win-x86) — release asset](https://github.com/OWNER/REPO/releases/download/vX.Y/discord-gemini-bot-windows-x86.exe) |

If you don't use GitHub Releases, you can link directly to a file in the repository raw path (not recommended for large binaries):

- Example raw link: https://github.com/OWNER/REPO/raw/main/dist/discord-gemini-bot.exe

Notes:
- Recommended: upload the executable as a GitHub Release asset and use the Releases URL format shown above — clicking the asset link downloads the file immediately.
- If you're serving the project directory over HTTP (for local testing), the included `download.html` page will auto-trigger a download when opened via `http://`.

For help creating a GitHub Release or uploading assets, tell me and I can generate the exact commands and a sample release description.

## Available Commands

- `!setrole <role_name>`: Change the bot's personality for you.
- `!roles`: List all available personalities.
- `!me`: View your current profile, intimacy score, and chat statistics.
- `!summary [n]`: Summarize the last `n` messages in the channel (default 50).
- `!reset`: Clear your chat history with the bot.
