# -----------------------------
# Bot Configuration
# -----------------------------
API_ID = 1234567                    # Replace with your actual API_ID (integer)
API_HASH = "your_api_hash_here"     # Replace with your actual API_HASH
BOT_TOKEN = "1234567890:ABCDEF..."  # Replace with your actual BOT_TOKEN

# -----------------------------
# Imports
# -----------------------------
from pyrogram import Client, filters
import asyncio
import subprocess
import os
from urllib.parse import urlparse, parse_qs

# -----------------------------
# Bot Setup
# -----------------------------
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -----------------------------
# /start command
# -----------------------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Hello!\n\n"
        "Send me any .m3u8 lecture link and I will convert it to MKV and send it back to you.\n\n"
        "Format: LINK | filename | format | quality\n"
        "Example:\n"
        "`https://example.com/video.m3u8 | MyLecture | mkv | 720p`",
        parse_mode="markdown"
    )

# -----------------------------
# Handle user sent links
# -----------------------------
@app.on_message(filters.text & ~filters.command("start"))
async def download_mkv(client, message):
    try:
        # Parse input
        parts = [p.strip() for p in message.text.split("|")]
        if len(parts) != 4:
            return await message.reply_text("❌ Format invalid! Use: LINK | filename | format | quality")
        
        link, output_name, file_format, quality = parts
        output_file = f"{output_name}.{file_format}"

        # Parse link for BASE_URL, VIDEO_PATH, VIDEO_FILE, URLPrefix/Signature
        parsed_url = urlparse(link)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path_parts = parsed_url.path.split('/')
        video_path = '/' + '/'.join(path_parts[1:-1]) + '/'
        video_file = path_parts[-1]

        query = parse_qs(parsed_url.query)
        edge_token = query.get('edge-cache-token', [''])[0]
        if not edge_token:
            return await message.reply_text("❌ Invalid or expired link!")

        # Inform user download started
        sent = await message.reply_text(f"🔹 Downloading {output_file} ...")

        # FFmpeg command
        command = [
            "ffmpeg",
            "-i", link,
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            output_file,
            "-progress", "pipe:1",
            "-nostats"
        ]

        # Run FFmpeg asynchronously
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Read progress
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line = line.decode('utf-8').strip()
            if "out_time_ms=" in line:
                out_ms = int(line.split('=')[1])
                sec = out_ms / 1000000
                # Optional: update every few seconds
                await sent.edit(f"🔹 Downloading {output_file} ... {sec:.0f}s processed")

        await process.wait()

        if os.path.exists(output_file):
            await client.send_video(
                chat_id=message.chat.id,
                video=output_file,
                caption=f"✅ Here is your video: {output_file} ({quality})"
            )
            await sent.delete()
            os.remove(output_file)
        else:
            await sent.edit("❌ Conversion failed!")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# -----------------------------
# Run the bot
# -----------------------------
if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
            
