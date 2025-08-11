# config.py
import os

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'PUT_YOUR_TOKEN_HERE')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '123456789'))  # replace with your Telegram id
DATABASE = os.environ.get('DATABASE', 'aizen.db')