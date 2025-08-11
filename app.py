from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# ----------------------------
# CONFIG
# ----------------------------
BOT_TOKEN = "7293333413:AAEirkQf1KH9NW45g1Tv5fwXthLJLvVNVK8"  # yahan apna bot token daalo
ADMIN_ID = 6324825537          # yahan apna admin Telegram ID daalo
PORT = int(os.environ.get("PORT", 5000))

# ----------------------------
# FLASK APP
# ----------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# ----------------------------
# TELEGRAM BOT HANDLERS
# ----------------------------

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Redeem 🎁", callback_data="redeem")],
        [InlineKeyboardButton("Premium 💎", callback_data="premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚡ Welcome To Aizen Bot ⚡\nChoose an option below:",
        reply_markup=reply_markup
    )

# Callback button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "redeem":
        await query.message.reply_text(
            "❌ Please provide your redeem details.\nExample:\n/redeem email@example.com key123"
        )
    elif query.data == "premium":
        await query.message.reply_text(
            "💎 Please enter your premium key.\nExample:\n/premium ABCD1234"
        )

# /redeem command
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide your redeem details.\nExample:\n/redeem email@example.com key123"
        )
        return
    
    redeem_data = " ".join(context.args)
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "NoUsername"

    await update.message.reply_text("✅ Your redeem request has been sent to the admin!")

    msg_for_admin = (
        f"💎 Premium user redeemed:\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{username}\n"
        f"📩 Message: /redeem {redeem_data}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg_for_admin)

    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

# /premium command
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "💎 Please enter your premium key.\nExample:\n/premium ABCD1234"
        )
        return
    
    premium_key = " ".join(context.args)
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "NoUsername"

    await update.message.reply_text("✅ Your premium key request has been sent to the admin!")

    msg_for_admin = (
        f"💎 Premium key request:\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{username}\n"
        f"🔑 Key: {premium_key}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg_for_admin)

# ----------------------------
# BOT RUNNER
# ----------------------------
def run_bot():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(button_handler))
    app_telegram.add_handler(CommandHandler("redeem", redeem))
    app_telegram.add_handler(CommandHandler("premium", premium))

    app_telegram.run_polling()

# ----------------------------
# THREAD START
# ----------------------------
if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=PORT)
