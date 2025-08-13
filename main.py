import os
import m3u8
import requests
from urllib.parse import urljoin
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Output folder
OUTPUT_DIR = "downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_m3u8(m3u8_url, output_filename):
    print(f"[INFO] Fetching playlist: {m3u8_url}")
    m3u8_obj = m3u8.load(m3u8_url)

    # Get all segments
    segments = m3u8_obj.segments
    print(f"[INFO] Total segments: {len(segments)}")

    # Create a temporary file to store downloaded ts file list
    ts_list_file = os.path.join(OUTPUT_DIR, "ts_list.txt")

    with open(ts_list_file, "w") as f:
        for i, segment in enumerate(segments, start=1):
            segment_url = urljoin(m3u8_url, segment.uri)
            ts_filename = os.path.join(OUTPUT_DIR, f"seg_{i}.ts")

            # Download segment
            r = requests.get(segment_url, stream=True)
            with open(ts_filename, "wb") as ts_file:
                ts_file.write(r.content)

            f.write(f"file '{ts_filename}'\n")
            print(f"[INFO] Downloaded segment {i}/{len(segments)}")

    # Merge using ffmpeg
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    subprocess.run(
        ["ffmpeg", "-f", "concat", "-safe", "0", "-i", ts_list_file, "-c", "copy", output_path]
    )

    print(f"[SUCCESS] Video saved as {output_path}")


if __name__ == "__main__":
    # Example: replace with your link
    m3u8_link = input("Enter m3u8 link: ").strip()
    download_m3u8(m3u8_link, "output.mp4")
            
async def download_video(url: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"video_{timestamp}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': output_file,
        'quiet': True
    }
  
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
  
return output_file

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = update.message.text.strip()
  
  if text.startswith("http") and ".m3u8" in text:
    await update.message.reply_text("📥 Downloading your video... Please wait!")
    try:
      file_path = await download_video(text)
      await update.message.reply_video(video=open(file_path, 'rb'))
      os.remove(file_path)
    except Exception as e:
      await update.message.reply_text(f"❌ Error: {e}")
    else:
      await update.message.reply_text("Send me a valid `.m3u8` link with edge-cache-token.")
      def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
    
    if __name__ == "__main__":
      main()
  
