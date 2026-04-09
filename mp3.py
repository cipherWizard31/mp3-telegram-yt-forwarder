import logging
import os
import re
import tempfile
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import yt_dlp

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN  = "BOT_TOKEN"
CHANNEL_ID = "@channel_link_or_username"
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

YOUTUBE_RE = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)"
    r"[\w\-]+"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Send me a YouTube link and I'll post the audio to the channel!"
    )


async def handle_yt_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    url = msg.text.strip()

    if not YOUTUBE_RE.search(url):
        await msg.reply_text("⚠️ That doesn't look like a YouTube link. Try again!")
        return

    status = await msg.reply_text("⏳ Downloading audio…")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            ydl_opts = {
                "format": "bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio",
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
                "writethumbnail": True,   # download the thumbnail
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title    = info.get("title", "audio")
                artist   = info.get("artist") or info.get("uploader", "")
                duration = info.get("duration")

            # Find the audio file and thumbnail separately
            audio_file = None
            thumb_file = None
            image_exts = {".jpg", ".jpeg", ".png", ".webp"}

            for fname in os.listdir(tmpdir):
                fpath = os.path.join(tmpdir, fname)
                ext = os.path.splitext(fname)[1].lower()
                if ext in image_exts:
                    thumb_file = fpath
                else:
                    audio_file = fpath

            if not audio_file:
                await status.edit_text("❌ Download failed — no audio file found.")
                return

            file_size = os.path.getsize(audio_file)
            if file_size > 50 * 1024 * 1024:
                await status.edit_text("❌ File is too large for Telegram (over 50 MB).")
                return

            await status.edit_text("📤 Uploading to channel…")

            # Send with thumbnail if we have one
            if thumb_file:
                with open(audio_file, "rb") as af, open(thumb_file, "rb") as tf:
                    await context.bot.send_audio(
                        chat_id=CHANNEL_ID,
                        audio=af,
                        thumbnail=tf,
                        title=title,
                        performer=artist,
                        duration=duration,
                        filename=os.path.basename(audio_file),
                    )
            else:
                with open(audio_file, "rb") as af:
                    await context.bot.send_audio(
                        chat_id=CHANNEL_ID,
                        audio=af,
                        title=title,
                        performer=artist,
                        duration=duration,
                        filename=os.path.basename(audio_file),
                    )

            await status.edit_text(f"✅ Posted!\n🎵 {title}")
            logger.info("Posted '%s' to %s", title, CHANNEL_ID)

    except yt_dlp.utils.DownloadError as e:
        logger.error("yt-dlp error: %s", e)
        await status.edit_text(
            "❌ Couldn't download that video.\n"
            "It may be age-restricted, region-blocked, or unavailable."
        )
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        await status.edit_text(f"❌ Something went wrong:\n{e}")


def main() -> None:
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(120)
        .write_timeout(120)
        .connect_timeout(30)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_yt_link,
    ))
    logger.info("Bot is running…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()