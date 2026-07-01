$ErrorActionPreference = 'Stop'

if (-not (Test-Path .venv)) {
    py -3.12 -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip pyinstaller
pyinstaller --noconfirm --onefile --console --name discord-gemini-bot --icon icon.ico --add-data "data;data" --add-data ".env;." --distpath dist --workpath build --specpath . bot.py
Write-Host "Build complete. EXE is in dist/discord-gemini-bot.exe"
