import os
import subprocess
from pyrogram import Client, filters

API_ID = os.environ.get("API_ID", "api_id")
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Client("m3u8_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command(["start"]))
async def start(client, message):
    await message.reply("👋 Send me any `.m3u8` link with `edge-cache-token` and I will download it.")

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_video(client, message):
    url = message.text.strip()

    # Validate link
    if not url.startswith("http") or ".m3u8" not in url or "edge-cache-token" not in url:
        await message.reply("❌ Invalid link. Please send a proper signed `.m3u8` link.")
        return

    await message.reply("📥 Downloading... please wait.")

    try:
        output_file = "video.mp4"
        subprocess.run(["ffmpeg", "-i", url, "-c", "copy", output_file], check=True)

        await message.reply_video(output_file, caption="✅ Download complete!")
        os.remove(output_file)
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

app.run()
    
