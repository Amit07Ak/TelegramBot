# 🧩 Minimal Telegram Moderation Bot (Python)

A clean and minimal **Telegram bot** built with **Python** using the **`python-telegram-bot` v20+ async API**.

This project is designed as a **starter template** for:
- Educational groups
- Coaching / classes
- Small communities
- Early-stage business or admin automation

It demonstrates **basic user interaction** and **essential group moderation features** that can be extended easily.

---

## 🚀 Features

### Basic Commands
- `/start` — Welcome message
- `/help` — Show available commands
- `/echo <text>` — Echo user text  
  *(Also echoes normal non-command messages)*

### Admin / Moderation Commands  
> ⚠️ The bot **must be an admin** in the chat with required permissions.

- `/pin` — Pin a replied message
- `/delete` — Delete a replied message
- `/block` — Ban a user (reply required)
- `/unblock` — Unban a user
- `/mute` — Restrict a user from sending messages
- `/unmute` — Restore messaging permissions
- `/announce <text>` — Send an announcement to the chat

---

## 📂 Project Structure


---

## 🛠️ Tech Stack

- **Python 3.8+**
- **python-telegram-bot ≥ 20.0**
- Async / asyncio-based polling

---

## 🤖 Create a Telegram Bot (BotFather)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name and username
4. Copy the **Bot Token**
5. Keep the token **secret**

The token will be stored in an **environment variable**.

---

## 🔐 Bot Permissions (Important)

For moderation features to work:

1. Add the bot to your group
2. Promote it as **Administrator**
3. Enable permissions:
   - Delete messages
   - Pin messages
   - Ban users
   - Restrict users

### Disable Privacy Mode (Recommended)

By default, bots do not receive all group messages.

In **BotFather**:


This allows the bot to receive **non-command messages**.

---

## 🧪 Run the Bot Locally

---

### 🐧 Linux / 🍎 macOS

```bash
# 1. Create virtual envpythozironment
python3 -m venv .venv
# 2. Activate it
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set bot token
export TELEGRAM_TOKEN="<your-telegram-bot-token>"

# 5. Run the bot
python bot.py


# 1. Set token (current session)
$env:TELEGRAM_TOKEN = "<your-telegram-bot-token>"

# 2. Create virtual environment
python -m venv .venv

# 3. Activate environment
. .\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the bot
python bot.py


:: Set token
set TELEGRAM_TOKEN=<your-telegram-bot-token>

:: Create virtual environment
python -m venv .venv

:: Activate environment
\.venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Run the bot
python bot.py



