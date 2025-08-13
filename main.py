import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Environment variables
API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

# Create Pyrogram bot
bot = Client(
    "m3u8_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Download function
async def download_m3u8(url: str, output: str):
    cmd = [
        "ffmpeg",
        "-i", url,
        "-c", "copy",
        "-bsf:a", "aac_adtstoasc",
        output
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    return os.path.exists(output)

# /start command
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "👋 नमस्ते!\n\n"
        "मुझे कोई भी signed `.m3u8` लिंक `/upload LINK` के साथ भेजें,\n"
        "मैं उसे डाउनलोड करके आपको वीडियो भेज दूँगा।\n\n"
        "उदाहरण:\n`/upload https://example.com/master.m3u8`"
    )

# /upload command
@bot.on_message(filters.command("upload") & filters.private)
async def upload_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ कृपया एक m3u8 लिंक दें!\n\nउदाहरण:\n`/upload https://example.com/master.m3u8`")
        return

    url = message.command[1]
    filename = "video.mp4"

    status_msg = await message.reply_text("📥 Download शुरू हो रहा है...")

    success = await download_m3u8(url, filename)

    if success:
        await status_msg.edit("✅ Download पूरा! Upload हो रहा है...")
        await message.reply_video(filename, caption="🎥 यह रहा आपका वीडियो!")
        os.remove(filename)
    else:
        await status_msg.edit("❌ Download विफल हुआ, कृपया लिंक चेक करें।")

print("🚀 Bot Started...")
bot.run()
        
