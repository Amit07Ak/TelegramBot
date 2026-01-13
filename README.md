# 🤖 Automated Telegram Moderation Bot (Python automation)

A **professional, fully automated Telegram moderation bot** built with **Python** using the **`python-telegram-bot` v20+ async API**.

This bot is **event-driven and rule-based** — once added to a group, it moderates automatically.  
Admins **do not need to type commands** for daily moderation.

---

## 🚀 What This Bot Does (Automatically)

- 🚫 Deletes links sent by non-admin users
- 🔇 Detects spam and auto-mutes spammers
- 👋 Welcomes new members
- 🧹 Removes command messages silently
- 🛡️ Ignores admins (admin immunity)
- ⏱️ Applies time-based restrictions

This design matches **real-world professional moderation bots** used in large Telegram communities.

---

## 🧠 How It Works

- Listens to **Telegram events**, not commands
- Applies **predefined rules** automatically
- Uses **rate-limiting** for spam detection
- Uses **temporary restrictions** instead of permanent bans
- Keeps the chat clean without human intervention

---

## 🛠️ Tech Stack

- Python 3.8+
- `python-telegram-bot` ≥ 20.0 (async)
- `python-dotenv`
- Polling-based execution

---

## 📂 Project Structure
TelegramBot/
├── bot.py # Automated moderation logic
├── requirements.txt # Dependencies
├── README.md # Documentation
├── .env # Environment variables (NOT committed)
├── .gitignore


---

## 🤖 Create a Telegram Bot

1. Open Telegram → **@BotFather**
2. Run `/newbot`
3. Save the **Bot Token**
4. Disable privacy mode:


---

## 🔐 Required Bot Permissions

Add the bot to your group and promote it as **Administrator** with:

- ✅ Delete messages
- ✅ Restrict members
- ✅ Ban users (optional)
- ✅ Pin messages (optional)

---

## ⚙️ Environment Setup

### Create `.env` file
```env
TELEGRAM_TOKEN=your_telegram_bot_token_here

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py

Windows powershell

python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py


Configuration (Inside bot.py)

SPAM_MSG_LIMIT = 5
SPAM_TIME_WINDOW = 10  # seconds
MUTE_DURATION = 300   # seconds
BLOCK_LINKS = True

