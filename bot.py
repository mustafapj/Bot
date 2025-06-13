import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from telethon import TelegramClient, sync
import asyncio
import itertools
import string
import os
from datetime import datetime

# تكوين الإعدادات من البيانات المقدمة
API_ID = 26455325
API_HASH='c00851db310f5e3c0f29333ef312c219'
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
CHANNEL_ID = "@mmmmmuyter"
ADMIN_IDS = [5367866254]  # آيدي المسؤول

# إعداد MTProto servers
MT_PROTO_SERVERS = {
    'test': '149.154.167.40:443',
    'production': '149.154.167.50:443'
}

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UsernameHunter:
    def __init__(self):
        self.client = TelegramClient(
            'username_hunter',
            API_ID,
            API_HASH,
            system_version="4.16.30",
            device_model="Firstaidkit",
            app_version="10.2.0"
        )
        self.checked_usernames = set()
        self.available_usernames = set()
        self.reserved_usernames = set()
        self.load_progress()

    def load_progress(self):
        """تحميل التقدم المحرز من الملفات"""
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
        """حفظ التقدم المحرز في الملفات"""
        with open('checked.txt', 'w') as f:
            f.write('\n'.join(self.checked_usernames))
        
        with open('available.txt', 'w') as f:
            f.write('\n'.join(self.available_usernames))
        
        with open('reserved.txt', 'w') as f:
            f.write('\n'.join(self.reserved_usernames))

    async def check_username(self, username):
        """فحص إذا كان اليوزر متاحًا"""
        if username in self.checked_usernames:
            return username in self.available_usernames

        try:
            await self.client.get_entity(username)
            self.checked_usernames.add(username)
            return False
        except ValueError:
            self.checked_usernames.add(username)
            self.available_usernames.add(username)
            return True
        except Exception as e:
            logger.error(f"Error checking @{username}: {e}")
            return False

    async def reserve_username(self, username):
        """حجز اليوزر"""
        try:
            await self.client.create_channel(
                title=username,
                about="قناة مؤقتة لحجز اليوزر",
                megagroup=False
            )
            self.reserved_usernames.add(username)
            self.available_usernames.remove(username)
            self.save_progress()
            
            # إرسال إشعار للقناة
            await send_to_channel(f"🎉 تم حجز اليوزر الجديد: @{username}")
            return True
        except Exception as e:
            logger.error(f"Error reserving @{username}: {e}")
            await send_to_channel(f"❌ فشل حجز اليوزر: @{username}\nالخطأ: {str(e)}")
            return False

    def generate_usernames(self, length, chars=None):
        """توليد يوزرات بالطول المطلوب"""
        if chars is None:
            chars = string.ascii_lowercase + string.digits + '_'
        return [''.join(combo) for combo in itertools.product(chars, repeat=length)]

hunter = UsernameHunter()

async def send_to_channel(message):
    """إرسال رسالة إلى القناة المحددة"""
    try:
        await updater.bot.send_message(chat_id=CHANNEL_ID, text=message)
    except Exception as e:
        logger.error(f"فشل إرسال الرسالة للقناة: {e}")

async def start_hunting(update: Update, length: int):
    """بدء عملية الصيد"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية استخدام هذا البوت.")
        return

    usernames = hunter.generate_usernames(length)
    total = len(usernames)
    checked = 0
    available = 0
    reserved = 0

    progress_msg = await update.message.reply_text(
        f"🚀 بدء صيد اليوزرات {length}-حرفية\n"
        f"📊 العدد الإجمالي: {total}\n"
        f"⏳ جاري البدء..."
    )

    for username in usernames:
        checked += 1
        if await hunter.check_username(username):
            available += 1
            if await hunter.reserve_username(username):
                reserved += 1
            
        if checked % 100 == 0:
            await progress_msg.edit_text(
                f"🚀 جاري صيد اليوزرات {length}-حرفية\n"
                f"📊 التقدم: {checked}/{total}\n"
                f"✅ المتاحة: {available}\n"
                f"🛡 المحجوزة: {reserved}\n"
                f"⏱ آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"
            )
            await asyncio.sleep(5)  # تجنب حظر التليجرام

    final_report = (
        f"🏁 انتهى الصيد!\n"
        f"🔍 تم فحص: {checked}\n"
        f"✅ المتاحة: {available}\n"
        f"🛡 المحجوزة: {reserved}\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await progress_msg.edit_text(final_report)
    await send_to_channel(final_report)

async def start(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية استخدام هذا البوت.")
        return

    keyboard = [
        [InlineKeyboardButton("صيد يوزرات ثنائية", callback_data='hunt_2')],
        [InlineKeyboardButton("صيد يوزرات ثلاثية", callback_data='hunt_3')],
        [InlineKeyboardButton("صيد يوزرات رباعية", callback_data='hunt_4')],
        [InlineKeyboardButton("اليوزرات المتاحة", callback_data='list_available')],
        [InlineKeyboardButton("اليوزرات المحجوزة", callback_data='list_reserved')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🦅 مرحبًا بكم في بوت صياد اليوزرات!\n"
        "اختر نوع اليوزرات التي تريد صيدها:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'hunt_2':
        await start_hunting(update, 2)
    elif query.data == 'hunt_3':
        await start_hunting(update, 3)
    elif query.data == 'hunt_4':
        await start_hunting(update, 4)
    elif query.data == 'list_available':
        await list_available(update, context)
    elif query.data == 'list_reserved':
        await list_reserved(update, context)

async def list_available(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية استخدام هذا البوت.")
        return

    count = len(hunter.available_usernames)
    if count == 0:
        await update.message.reply_text("لا توجد يوزرات متاحة حالياً.")
        return

    usernames = list(hunter.available_usernames)
    chunk_size = 50
    for i in range(0, len(usernames), chunk_size):
        chunk = usernames[i:i + chunk_size]
        await update.message.reply_text(
            f"اليوزرات المتاحة ({count}):\n\n" + "\n".join(chunk)
        )

async def list_reserved(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية استخدام هذا البوت.")
        return

    count = len(hunter.reserved_usernames)
    if count == 0:
        await update.message.reply_text("لا توجد يوزرات محجوزة حالياً.")
        return

    usernames = list(hunter.reserved_usernames)
    chunk_size = 50
    for i in range(0, len(usernames), chunk_size):
        chunk = usernames[i:i + chunk_size]
        await update.message.reply_text(
            f"اليوزرات المحجوزة ({count}):\n\n" + "\n".join(chunk)
        )

def main():
    global updater
    # بدء عميل Telethon
    hunter.client.start()

    # بدء بوت التليجرام
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("available", list_available))
    dispatcher.add_handler(CommandHandler("reserved", list_reserved))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    logger.info("Bot started successfully with all configurations")
    updater.idle()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")