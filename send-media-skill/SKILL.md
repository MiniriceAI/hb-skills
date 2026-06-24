# send-media-skill

Idempotent file delivery to Feishu/Telegram via gateway MEDIA: mechanism.

## Usage

```bash
python3 /root/.openclaw/workspace/skills/send-media-skill/scripts/send_media.py /path/to/file.pdf "optional caption"
```

Deduplicates per file path + calendar date (CST). Safe to call multiple times — only sends once per day.

## Output

- `MEDIA:/path/to/file` → copy this line verbatim into your reply (gateway sends the file)
- `SKIP — already sent today: filename` → already sent, do NOT write MEDIA: in reply
