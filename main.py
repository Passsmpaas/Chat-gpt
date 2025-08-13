import os
import re
import subprocess
from pyrogram import Client, filters

# ------------------ CONFIG ------------------
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = Client("m3u8_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Regex to detect m3u8 links
M3U8_PATTERN = r'https?://[^\s]+\.m3u8[^\s]*'


# ------------------ COMMANDS ------------------
@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "**👋 Welcome!**\n"
        "Send me any signed `.m3u8` link (with `edge-cache-token`) and I will download it for you.\n\n"
        "Example:\nhttps://example.com/path/master.m3u8?edge-cache-token=..."
    )

@bot.on_message(filters.command("upload"))
async def upload_cmd(_, message):
    await message.reply_text("📤 Upload command detected! Please send me the m3u8 link to upload.")

# ------------------ AUTO DOWNLOAD HANDLER ------------------
@bot.on_message(filters.regex(M3U8_PATTERN))
async def download_video(_, message):
    link = re.search(M3U8_PATTERN, message.text).group()
    file_name = "video.mp4"
    await message.reply_text("📥 Downloading your video, please wait...")

    try:
        subprocess.run(
            ["ffmpeg", "-i", link, "-c", "copy", file_name],
            check=True
        )
        await message.reply_video(video=file_name)
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# ------------------ RUN BOT ------------------
bot.run()
    
