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

# ================= ENV =================
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))

if not TELEGRAM_TOKEN:
    raise SystemExit("TELEGRAM_TOKEN not set")

# ================= CONFIG =================
SPAM_MSG_LIMIT = 5
SPAM_TIME_WINDOW = 10
MUTE_DURATION = 300          # 5 minutes
MAX_WARNINGS = 2             # after this → ban
# ========================================

# ================= STATE =================
user_message_times = defaultdict(list)
user_warnings = defaultdict(int)

content_queue = []           # 🔴 FIXED: was missing
posting_enabled = False
scheduled_job = None
# ========================================


# ================= ADMIN CHECK =================
async def is_admin(chat_id, user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


# ================= WELCOME =================
async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n"
            "No spam • No links • Be respectful"
        )


# ================= MAIN MODERATION =================
async def auto_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.lower()
    now = time.time()

    # ---------- ADMIN IMMUNITY ----------
    if await is_admin(chat_id, user.id, context):
        try:
            await context.bot.pin_chat_message(chat_id, update.message.message_id)
        except Exception:
            pass
        return

    # ---------- COMMAND CLEANUP ----------
    if text.startswith("/"):
        try:
            await update.message.delete()
        except Exception:
            pass
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


# ================= VIOLATION HANDLER =================
async def handle_violation(update, context, reason):
    chat_id = update.effective_chat.id
    user = update.effective_user

    user_warnings[user.id] += 1

    try:
        await update.message.delete()
    except Exception:
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


# ================= CONTENT COLLECTOR =================
async def collect_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global posting_enabled, scheduled_job

    msg = update.channel_post
    if not msg:
        return

    text = (msg.text or "").lower()
    logging.info("Channel post received: %s", text)

    # START
    if text == "#start":
        if not posting_enabled:
            posting_enabled = True
            scheduled_job = context.job_queue.run_repeating(
                send_next_content,
                interval=30,
                first=10
            )
            logging.info("Auto-posting STARTED")
        return

    # STOP
    if text == "#stop":
        posting_enabled = False
        if scheduled_job:
            scheduled_job.schedule_removal()
            scheduled_job = None
        logging.info("Auto-posting STOPPED")
        return

    # NORMAL CONTENT
    content_queue.append(msg)
    logging.info("Content queued. Queue size=%s", len(content_queue))


# ================= SENDER =================
async def send_next_content(context: ContextTypes.DEFAULT_TYPE):
    if not posting_enabled or not content_queue:
        return

    if TARGET_CHAT_ID == 0:
        logging.warning("TARGET_CHAT_ID not set")
        return

    message = content_queue.pop(0)

    await context.bot.copy_message(
        chat_id=TARGET_CHAT_ID,
        from_chat_id=message.chat_id,
        message_id=message.message_id
    )

    logging.info("Forwarded message %s", message.message_id)

# ================= MAIN =================
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Group moderation
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.ChatType.CHANNEL, auto_moderation))

    # Channel content collection  🔴 FIXED: handler was missing
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, collect_content))

    app.run_polling(allowed_updates=Update.ALL_TYPES)
 
    

    # app.add_handler(MessageHandler(filters.ALL, debug_all))


if __name__ == "__main__":
    main()
