# app.py
from flask import Flask
import threading
import bot

app = Flask(__name__)

@app.route('/')
def index():
    return 'Aizen Bot is running.'

if __name__ == '__main__':
    # run bot in a separate thread (bot.main() starts polling and is blocking)
    t = threading.Thread(target=bot.main, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)
    from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Apna bot token yaha daalo
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Admin ka chat ID yaha daalo
ADMIN_ID = 123456789   # Replace with your Telegram user ID

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome To Aizen Bot ⚡\n"
        "Please Use this /redeem Command For Get Prime video 👨‍💻\n"
        "For Premium use This Command /premium"
    )

# /redeem command
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide your redeem details. Example:\n/redeem email@example.com key123")
        return
    
    # User input
    redeem_data = " ".join(context.args)
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "NoUsername"

    # User ko reply
    await update.message.reply_text("✅ Your redeem request has been sent to the admin!")

    # Extra details admin ko bhejna
    msg_for_admin = (
        f"💎 Premium user redeemed:\n"
        f"ID: {user_id}\n"
        f"Username: @{username}\n"
        f"Message: /redeem {redeem_data}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg_for_admin)

    # Original message forward karna
    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem))

    app.run_polling()

if __name__ == "__main__":
    main()
