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