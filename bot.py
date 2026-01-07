import os
import time
import logging
from collections import defaultdict

from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

# ================= CONFIG =================

SPAM_MSG_LIMIT = 5          # messages
SPAM_TIME_WINDOW = 10       # seconds
MUTE_DURATION = 300         # seconds (5 minutes)
BLOCK_LINKS = True

# ==========================================

user_activity = defaultdict(list)


async def is_admin(chat_id: int, user_id: int, context) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


# ---------- AUTO WELCOME ----------

async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n"
            "Please read the group rules and avoid spam."
        )


# ---------- AUTO LINK BLOCK ----------

async def auto_block_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    if await is_admin(chat_id, user.id, context):
        return

    text = update.message.text.lower()

    if BLOCK_LINKS and ("http://" in text or "https://" in text or "t.me/" in text):
        await update.message.delete()


# ---------- AUTO SPAM DETECTION ----------

async def auto_spam_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    if await is_admin(chat_id, user.id, context):
        return

    now = time.time()
    user_activity[user.id].append(now)

    # keep messages in time window
    user_activity[user.id] = [
        t for t in user_activity[user.id]
        if now - t <= SPAM_TIME_WINDOW
    ]

    if len(user_activity[user.id]) >= SPAM_MSG_LIMIT:
        await context.bot.restrict_chat_member(
            chat_id,
            user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=int(now + MUTE_DURATION)
        )

        user_activity[user.id].clear()

        await context.bot.send_message(
            chat_id,
            f"🔇 {user.first_name} muted for spam (5 minutes)."
        )


# ---------- AUTO COMMAND CLEANUP ----------

async def delete_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text.startswith("/"):
        try:
            await update.message.delete()
        except Exception:
            pass


# ================= MAIN =================

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_TOKEN not set")

    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(token).build()

    # Welcome handler
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))

    # Core moderation handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_block_links))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_spam_control))

    # Cleanup commands silently
    app.add_handler(MessageHandler(filters.COMMAND, delete_commands))

    app.run_polling()


if __name__ == "__main__":
    main()
