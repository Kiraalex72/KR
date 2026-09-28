import os
import traceback
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Read secrets from environment variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

# Connect to MongoDB
# (If MONGO_URI is missing, we catch it at the bottom before connecting)
if MONGO_URI:
    client = MongoClient(MONGO_URI)
    db = client["luciddreams_db"]
    journals = db["journals"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Lucid Dreamer Bot!\n\n"
        "Commands:\n"
        "/rc - Trigger a Reality Check\n"
        "/journal <text> - Save a dream entry\n"
        "/dreams - View your saved dreams"
    )

async def reality_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "REALITY CHECK TIME!\n\n"
        "1. Look at your hands. Count your fingers.\n"
        "2. Try pushing your index finger through your opposite palm.\n"
        "3. Pinch your nose and try to breathe.\n\n"
        "Are you dreaming right now?"
    )

async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    entry_text = " ".join(context.args)

    if not entry_text:
        await update.message.reply_text(
            "Usage: `/journal I was flying over mountains.`",
            parse_mode="Markdown",
        )
        return

    journals.insert_one({"user_id": user_id, "entry": entry_text})
    await update.message.reply_text("Dream entry saved!")

async def view_dreams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    entries = list(journals.find({"user_id": user_id}))

    if not entries:
        await update.message.reply_text("No dreams recorded yet.")
        return

    msg = "Your Dream Journal:\n\n"
    for idx, item in enumerate(entries, 1):
        msg += f"{idx}. {item['entry']}\n"

    await update.message.reply_text(msg)

if __name__ == "__main__":
    try:
        print("Connecting to Telegram...")
        # Check if variables actually exist
        if not TOKEN:
            raise ValueError("TELEGRAM_TOKEN is missing or empty! Check Render Environment Variables.")
        if not MONGO_URI:
            raise ValueError("MONGO_URI is missing or empty! Check Render Environment Variables.")

        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("rc", reality_check))
        app.add_handler(CommandHandler("journal", journal))
        app.add_handler(CommandHandler("dreams", view_dreams))

        print("Bot is running...")
        app.run_polling()
    except Exception as e:
        print("==========================")
        print("🚨 BOT CRASHED 🚨")
        print(traceback.format_exc())
        print("==========================")