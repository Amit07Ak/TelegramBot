import os
import time
import logging
from collections import defaultdict
# dotenv to store token and some personal ids
from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

load_dotenv()

# ================== CONFIG =================#

SPAM_MSG_LIMIT = 5
SPAM_TIME_WINDOW = 10
MUTE_DURATION = 300          # 5 minutes
MAX_WARNINGS = 2             # after this → ban

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# =======================================#

user_message_times = defaultdict(list)
user_warnings = defaultdict(int)


# ================= ADMIN CHECK =================#

async def is_admin(chat_id, user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False


# ================= WELCOME ================= #

async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n"
            "No spam • No links • Be respectful"
        )


# ================ MAIN MODERATION =================#

async def auto_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.lower()
    now = time.time()

    # ---------- ADMIN IMMUNITY ----------#
    if await is_admin(chat_id, user.id, context):
        try:
            await context.bot.pin_chat_message(chat_id, update.message.message_id)
        except:
            pass
        return

    # ---------- COMMAND CLEANUP ----------
    if text.startswith("/"):
        await update.message.delete()
        return

    # ---------- HELP / URGENT ----------
    if any(k in text for k in ["help", "urgent", "important", "admin", "serious"]):
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id,
                f"🆘 {user.first_name}, please DM admin: "
                f"<a href='tg://user?id={ADMIN_ID}'>Admin</a>",
                parse_mode="HTML"
            )

    # ---------- LINK DETECTION ----------
    if "http://" in text or "https://" in text or "t.me/" in text:
        await handle_violation(update, context, "Link sharing")
        return

    # ---------- SPAM DETECTION ----------
    user_message_times[user.id].append(now)
    user_message_times[user.id] = [
        t for t in user_message_times[user.id]
        if now - t <= SPAM_TIME_WINDOW
    ]

    if len(user_message_times[user.id]) >= SPAM_MSG_LIMIT:
        user_message_times[user.id].clear()
        await handle_violation(update, context, "Spamming")


# ================= VIOLATION HANDLER =================#

async def handle_violation(update, context, reason):
    chat_id = update.effective_chat.id
    user = update.effective_user

    user_warnings[user.id] += 1

    try:
        await update.message.delete()
    except:
        pass

    if user_warnings[user.id] <= MAX_WARNINGS:
        await context.bot.restrict_chat_member(
            chat_id,
            user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=int(time.time() + MUTE_DURATION),
        )
        await context.bot.send_message(
            chat_id,
            f"⚠️ {user.first_name} muted for {reason}. "
            f"Warning {user_warnings[user.id]}/{MAX_WARNINGS}"
        )
    else:
        await context.bot.ban_chat_member(chat_id, user.id)
        await context.bot.send_message(
            chat_id,
            f"🚫 {user.first_name} banned for repeated violations."
        )
        user_warnings[user.id] = 0


# ================= MAIN =================

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_TOKEN not set")

    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    app.add_handler(MessageHandler(filters.TEXT, auto_moderation))

    app.run_polling()


if __name__ == "__main__":
    main()
