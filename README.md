# 🎵 yt-to-channel-bot

A Telegram bot that downloads the audio from any YouTube link you send it and automatically posts it to a Telegram channel — with the video thumbnail as cover art.

---

## How it works

1. You send the bot a YouTube link in DM
2. The bot downloads the audio using `yt-dlp`
3. The audio is posted to your Telegram channel with the title, artist, and thumbnail

---

## Requirements

- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/botfather)
- Your bot added as an **admin** of your channel with "Post Messages" permission

---

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/yt-to-channel-bot.git
cd yt-to-channel-bot
```

**2. Install dependencies**
```bash
pip install python-telegram-bot==21.6 yt-dlp
```

**3. Configure the bot**

Open `mp3.py` and fill in the two constants at the top:

```python
BOT_TOKEN  = "your-bot-token-here"
CHANNEL_ID = "@your_channel"
```

**4. Run it**
```bash
python mp3.py
```

---

## Usage

Once the bot is running, open a DM with it on Telegram and send any YouTube link:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

The bot will reply with status updates and post the audio file to your channel automatically.

---

## Notes

- Files over **50 MB** are rejected (Telegram's bot API limit)
- Works with YouTube Shorts too
- Audio is downloaded in the best available format (MP3 or M4A) — no conversion needed, no ffmpeg required
- The YouTube thumbnail is attached as the audio cover art

---

## Dependencies

| Package | Purpose |
|---|---|
| `python-telegram-bot` | Telegram Bot API wrapper |
| `yt-dlp` | YouTube audio downloader |

---

## License

MIT
