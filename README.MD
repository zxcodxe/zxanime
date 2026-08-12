ZX Anime File Store Bot

A simple Telegram Anime File Store Bot.

🚀 Deploy on Heroku

""Deploy" (https://www.herokucdn.com/deploy/button.svg)" (https://heroku.com/deploy?template=https://github.com/zxcodxe/zxanime)

📦 Repository

"GitHub Repository" (https://github.com/zxcodxe/zxanime)

⚙️ Configuration

The bot configuration is loaded from "setup.json".

The configuration includes:

- "session"
- "token"
- "api_id"
- "api_hash"
- "workers"
- "db_uri"
- "db_name"
- "fsubs"
- "db"
- "auto_del"
- "messages"
- "admins"
- "disable_btn"
- "protect"

Important

Fill in the required values in "setup.json" before starting the bot.

Do not publish your Telegram bot token, API credentials, or MongoDB credentials publicly.

▶️ Run

The project starts with:

python3 main.py

The Heroku process is:

web: python3 main.py

🗄️ Database

A MongoDB connection is required for the bot's database functionality.

Set the correct "db_uri" and "db_name" in "setup.json".

🔐 Telegram

You need:

- Telegram Bot Token
- Telegram API ID
- Telegram API Hash
- Admin/Owner configuration
- Database channel configuration
- Force-subscription channels, if required

⚠️ Current Repository Configuration

Make sure all required configuration values are valid before deployment.

👑 Credits

ZXCODE

---

Repository

https://github.com/zxcodxe/zxanime
