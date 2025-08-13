import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
  
