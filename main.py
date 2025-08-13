from pyrogram import Client, filters
import asyncio
import subprocess
import os
from urllib.parse import urlparse, parse_qs
import re

# -----------------------------
# Bot setup
# -----------------------------
app = Client("my_bot", bot_token="YOUR_BOT_TOKEN_HERE")

# /start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Hello!\n\n"
        "Send me any .m3u8 lecture link in the format:\n"
        "`LINK | filename | format | quality`\n\n"
        "Example:\n"
        "`https://example.com/video.m3u8 | MyLecture | mkv | 720p`"
    )

# Handle user sent links
@app.on_message(filters.text & ~filters.command("start"))
async def download_mkv(client, message):
    try:
        # Parse input
        parts = [p.strip() for p in message.text.split("|")]
        if len(parts) != 4:
            return await message.reply_text("❌ Format invalid! Use: LINK | filename | format | quality")
        
        link, output_name, file_format, quality = parts
        output_file = f"{output_name}.{file_format}"

        # Parse link to check token expiry
        parsed_url = urlparse(link)
        query = parse_qs(parsed_url.query)
        edge_token = query.get('edge-cache-token', [''])[0]
        if not edge_token:
            return await message.reply_text("❌ Invalid or expired link!")

        # Initial message
        sent = await message.reply_text(f"🔹 Starting download for {output_file} ...")

        # FFmpeg command
        command = [
            "ffmpeg",
            "-i", link,
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            output_file,
            "-progress", "pipe:1",  # stdout progress
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
                # Convert to seconds
                sec = out_ms / 1000000
                # Optional: update message every few seconds
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

# Run the bot
app.run()
        
