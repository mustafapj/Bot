from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# توكن البوت الخاص بك
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"

# دالة الرد على /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا بك في البوت!")

# دالة التشغيل
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()