```markdown
# Tokyo Core Bot 🤖 | [Русский](README.ru.md)

A Japanese cyberpunk-themed Telegram bot with a progression system, ranks, and dynamic profile generation. Users compete for leaderboard positions using "Volts".

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-green?logo=telegram)

## 🌟 Features
- **Neon profile generation** (Pillow)
- **Custom rank hierarchy** (Novice → Digital Tensei)
- **Interactive buttons** for quick actions
- Auto-backup system (JSON)
- Dynamic progress bar with glitch effects
- Top-10 leaderboard with Markdown formatting

## ⚙️ Configuration (main.py)
```python
# ========== CONFIGURATION ==========
TOKEN = "YOUR_BOT_TOKEN"       # Bot token from @BotFather
ADMIN_ID = 7992580700          # Your Telegram ID
DB_NAME = "TokyoCore.db"       # Database name
RANKS = {
    "user": "Apprentice",      # Custom ranks
    "admin": "Administrator",  # (edit here)
    # ...
}
# ===================================
```

## 🛠️ Installation
1. Clone the repository:
```bash
git clone https://github.com/angelshy0/tokyocorebot.git
```

2. Install dependencies:
```bash
pip install python-telegram-bot pillow python-dotenv
```

3. In `main.py`:
- Replace `TOKEN` with your bot token
- Set your `ADMIN_ID`
- Configure ranks in the `RANKS` dictionary

4. Add to project folder:
- `core_bg.png` (1280x720px background)
- `cyber.ttf` (cyberpunk font)

## 🕹️ Commands
| Action                | Description                          |
|-----------------------|--------------------------------------|
| `/start`              | Initialize profile                  |
| `⚡ CHARGE CORE`       | +1 Volts (gamification)          |
| `🎖️ CYBER RANKING`    | Show top-10 players                 |
| `admin` command       | System status (admin-only)          |

## 🖼️ Profile Generation Example
```python
# Generates profile image with:
# - Username
# - Volt counter
# - Rank with shadow effect
# - Auto-number formatting
def generate_volts_image():
    ...
```

## 📦 Dependencies
- `python-telegram-bot` v20.x
- `Pillow` for image processing
- `sqlite3` for database

## 🔄 Auto Backup
```python
# Backups every 30 seconds:
def backup_data(context):
    ...
    context.bot.send_document(ADMIN_ID, "backup.json")
```

## 📜 License
MIT License © 2024 [angelshy0]  
*Developed with [DeepSeek-R1](https://www.deepseek.com) — AI assistant for developers.*

---

⚠️ **Important**: All configurations are edited directly in `main.py`. Remember to:
1. Set your Telegram ID in `ADMIN_ID`
2. Add font and background files
3. Configure the `RANKS` dictionary

[Switch to Russian Version](README.ru.md)
``` 
