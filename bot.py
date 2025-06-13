from telethon.sync import TelegramClient

API_ID = 26455325
API_HASH = 'c00851db310f6e3cdf29333ef312c219'

with TelegramClient('test_session', API_ID, API_HASH) as client:
    print("تم الاتصال بنجاح!")