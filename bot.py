# bot.py
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
from config import TOKEN, ADMIN_ID
import db, utils
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WELCOME = (
    "Welcome To Aizen Bot ⚡️\n"
    "Please Use this /redeem Command For Get Prime video 🧑‍💻\n"
    "For Premium use This Command /premium <KEY>"
)

PROCESSING = "Processing 🔑"
PURCHASE_PROMPT = "Please Purchase Premium Key For Use 🗝️"


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    db.ensure_user(user.id, user.username)
    if db.is_banned(user.id):
        update.message.reply_text("You are banned.")
        return
    update.message.reply_text(WELCOME)


def redeem(update: Update, context: CallbackContext):
    user = update.effective_user
    db.ensure_user(user.id, user.username)

    if db.is_banned(user.id):
        update.message.reply_text("You are banned.")
        return

    # Premium user — unlimited redeem
    if db.is_premium(user.id):
        update.message.reply_text(PROCESSING)
        context.bot.send_message(
            ADMIN_ID,
            f"💎 Premium user redeemed:\n"
            f"ID: {user.id}\nUsername: @{user.username or 'N/A'}\n"
            f"Message: {update.message.text}"
        )
        try:
            context.bot.forward_message(
                ADMIN_ID,
                chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
        except Exception as e:
            context.bot.send_message(ADMIN_ID, f"(Could not forward: {e})")
        return

    # Free user — limit check
    if db.has_redeemed_free(user.id):
        update.message.reply_text(PURCHASE_PROMPT)
        return

    # First time redeem
    db.set_redeemed_free(user.id)
    update.message.reply_text(PROCESSING)

    # Notify admin
    context.bot.send_message(
        ADMIN_ID,
        f"🆓 Free user redeemed:\n"
        f"ID: {user.id}\nUsername: @{user.username or 'N/A'}\n"
        f"Message: {update.message.text}"
    )
    try:
        context.bot.forward_message(
            ADMIN_ID,
            chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
    except Exception as e:
        context.bot.send_message(ADMIN_ID, f"(Could not forward: {e})")


def genk(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id != ADMIN_ID:
        update.message.reply_text("Only admin can use this.")
        return
    args = context.args
    if not args:
        update.message.reply_text("Usage: /genk <days> [count]")
        return
    try:
        days = int(args[0])
        count = int(args[1]) if len(args) > 1 else 1
    except ValueError:
        update.message.reply_text("numbers only")
        return
    keys = []
    for _ in range(count):
        k = utils.gen_key()
        db.add_key(k, days, user.id)
        keys.append(k)
    update.message.reply_text("Generated keys:\n" + "\n".join(keys))


def premium_cmd(update: Update, context: CallbackContext):
    user = update.effective_user
    db.ensure_user(user.id, user.username)
    if db.is_banned(user.id):
        update.message.reply_text("You are banned.")
        return
    args = context.args
    if not args:
        update.message.reply_text("Usage: /premium <KEY>")
        return
    key = args[0]
    res = db.use_key(key, user.id)
    if res is None:
        update.message.reply_text("Invalid key.")
        return
    if res is False:
        update.message.reply_text("Key already used.")
        return
    db.activate_premium(user.id, res)
    update.message.reply_text("Premium Activated ⚡️")
    context.bot.send_message(
        ADMIN_ID,
        f"User {user.id} activated premium for {res} days using key {key}"
    )


def reply_user(update: Update, context: CallbackContext):
    user = update.effective_user
    db.ensure_user(user.id, user.username)
    if db.is_banned(user.id):
        update.message.reply_text("You are banned.")
        return
    if not context.args:
        update.message.reply_text("Usage: /reply <your message>")
        return
    text = " ".join(context.args)
    context.bot.send_message(
        ADMIN_ID,
        f"Personal message from {user.id} ({user.username}):\n{text}"
    )
    update.message.reply_text("Your message was sent to admin.")


def replyto(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Only admin can reply to users")
        return
    if len(context.args) < 2:
        update.message.reply_text("Usage: /replyto <user_id> <message>")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        update.message.reply_text("bad user id")
        return
    text = " ".join(context.args[1:])
    try:
        context.bot.send_message(uid, f"Admin: {text}")
        update.message.reply_text("Sent.")
    except Exception as e:
        update.message.reply_text(f"Failed: {e}")


def ban(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Only admin")
        return
    if not context.args:
        update.message.reply_text("Usage: /ban <user_id>")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        update.message.reply_text("bad id")
        return
    db.ensure_user(uid)
    db.ban_user(uid)
    update.message.reply_text(f"Banned {uid}")
    try:
        context.bot.send_message(uid, "You are banned.")
    except:
        pass


def unban(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Only admin")
        return
    if not context.args:
        update.message.reply_text("Usage: /unban <user_id>")
        return
    uid = int(context.args[0])
    db.unban_user(uid)
    update.message.reply_text(f"Unbanned {uid}")


def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Only admin")
        return
    if not context.args:
        update.message.reply_text("Usage: /broadcast <message>")
        return
    text = " ".join(context.args)
    users = db.get_all_users()
    sent = 0
    for uid in users:
        try:
            context.bot.send_message(uid, f"Broadcast from admin:\n{text}")
            sent += 1
        except Exception as e:
            logger.warning(f"Failed sending to {uid}: {e}")
    update.message.reply_text(f"Broadcast sent to {sent} users")


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Unknown command")


def main():
    db.init_db()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('redeem', redeem))
    dp.add_handler(CommandHandler('genk', genk))
    dp.add_handler(CommandHandler('premium', premium_cmd))
    dp.add_handler(CommandHandler('reply', reply_user))
    dp.add_handler(CommandHandler('replyto', replyto))
    dp.add_handler(CommandHandler('ban', ban))
    dp.add_handler(CommandHandler('unban', unban))
    dp.add_handler(CommandHandler('broadcast', broadcast))

    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
