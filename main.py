import os
from flask import Flask
from threading import Thread
from pyrogram import Client

API_ID = os.environ.get("API_ID", "api_id")
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

    @bot.on_message()
    async def handler(client, message):
        await message.reply_text("Hello! Bot is working on Render.")

    bot.run()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
    
