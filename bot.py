import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from datetime import datetime

# إعدادات البوت
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
CHANNEL_ID = "-1002797492991"
ADMIN_IDS = [5367866254]  # ضع هنا آيديات المدراء

# تسجيل الأحداث
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إدارة اليوزرات
class UsernameHunter:
    def __init__(self):
        self.checked_usernames = set()
        self.available_usernames = set()
        self.reserved_usernames = set()
        self.load_progress()

    def load_progress(self):
        try:
            with open('checked.txt', 'r') as f:
                self.checked_usernames = set(line.strip() for line in f)
        except FileNotFoundError:
            pass
        try:
            with open('available.txt', 'r') as f:
                self.available_usernames = set(line.strip() for line in f)
        except FileNotFoundError:
            pass
        try:
            with open('reserved.txt', 'r') as f:
                self.reserved_usernames = set(line.strip() for line in f)
        except FileNotFoundError:
            pass

    def save_progress(self):
        with open('checked.txt', 'w') as f:
            f.write('\n'.join(self.checked_usernames))
        with open('available.txt', 'w') as f:
            f.write('\n'.join(self.available_usernames))
        with open('reserved.txt', 'w') as f:
            f.write('\n'.join(self.reserved_usernames))

hunter = UsernameHunter()

# دالة بدء البوت
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("❌ ليس لديك صلاحية استخدام هذا البوت.")
        return

    keyboard = [
        [InlineKeyboardButton("📬 اليوزرات المتاحة", callback_data='list_available')],
        [InlineKeyboardButton("🔒 اليوزرات المحجوزة", callback_data='list_reserved')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🦅 مرحبًا بك في بوت إدارة اليوزرات!",
        reply_markup=reply_markup
    )

# التعامل مع الضغط على الأزرار
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if user_id not in ADMIN_IDS:
        query.message.reply_text("❌ لا تملك صلاحية.")
        return

    if query.data == 'list_available':
        list_available(query, context)
    elif query.data == 'list_reserved':
        list_reserved(query, context)

# عرض اليوزرات المتاحة
def list_available(update, context: CallbackContext):
    count = len(hunter.available_usernames)
    if count == 0:
        update.message.reply_text("لا توجد يوزرات متاحة حالياً.")
        return

    usernames = list(hunter.available_usernames)
    chunk_size = 50
    for i in range(0, len(usernames), chunk_size):
        chunk = usernames[i:i + chunk_size]
        update.message.reply_text(
            f"📬 اليوزرات المتاحة ({count}):\n\n" + "\n".join(chunk)
        )

# عرض اليوزرات المحجوزة
def list_reserved(update, context: CallbackContext):
    count = len(hunter.reserved_usernames)
    if count == 0:
        update.message.reply_text("لا توجد يوزرات محجوزة حالياً.")
        return

    usernames = list(hunter.reserved_usernames)
    chunk_size = 50
    for i in range(0, len(usernames), chunk_size):
        chunk = usernames[i:i + chunk_size]
        update.message.reply_text(
            f"🔒 اليوزرات المحجوزة ({count}):\n\n" + "\n".join(chunk)
        )

# تشغيل البوت
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("available", list_available))
    dp.add_handler(CommandHandler("reserved", list_reserved))

    updater.start_polling()
    logger.info("✅ Bot started successfully")
    updater.idle()

if __name__ == '__main__':
    main()