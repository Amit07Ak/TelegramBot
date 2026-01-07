# 🤖 Automated Telegram Moderation Bot (Python)

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

