---
name: send_email
version: "2.0.0"
description: "Send an email to Bo Huang. Use when user says 'send to email', 'email me', 'send this document to my mailbox', or similar. Supports plain text and markdown-to-HTML conversion. Default recipient: minirice2017@gmail.com. IDEMPOTENT: same subject sent only once per day."
argument-hint: 'send_email subject="Report Title" file=/root/report.md | send_email subject="Hello" body="Message content"'
allowed-tools: Bash, Read
user-invocable: true
metadata:
  openclaw:
    emoji: "📧"
---

# send_email Skill

Send HTML-formatted emails to Bo Huang's default mailbox. **Idempotent**: same subject sent only once per day (CST). Duplicate calls are silently ignored.

## Trigger phrases
- "发邮件"
- "发到我邮箱"
- "把这个文档发我邮箱"
- "email me"
- "send to my email"
- "邮件发送"

## Usage

```bash
# Send a file (markdown auto-converted to HTML)
python3 ~/.openclaw/workspace/skills/send-email-skill/scripts/send_email.py \
  --subject "Report Title" \
  --file /root/document.md

# Send plain text content
python3 ~/.openclaw/workspace/skills/send-email-skill/scripts/send_email.py \
  --subject "Quick Message" \
  --body "Your content here"

# Send to a custom recipient
python3 ~/.openclaw/workspace/skills/send-email-skill/scripts/send_email.py \
  --subject "Title" \
  --file /root/doc.md \
  --to other@gmail.com

# Force resend even if already sent today
python3 ~/.openclaw/workspace/skills/send-email-skill/scripts/send_email.py \
  --subject "Title" \
  --file /root/doc.md \
  --force
```

## Configuration
- Default sender: minirice2017@gmail.com
- Default recipient: minirice2017@gmail.com
- SMTP: Gmail (configured via ~/.msmtprc)
- Dedup lock files: /tmp/email_sent_<hash>.lock (auto-cleared daily on reboot/restart)

## CRITICAL Instructions for Claude

1. **Call this script EXACTLY ONCE per task.** The script handles deduplication internally.
2. **NEVER call msmtp directly.** Always use this script.
3. **NEVER send a test email first.** Just send the real content.
4. **If the script says "SKIP — already sent today", that means success — do NOT retry.**
5. **Do not create inline Python email scripts.** Only use this script.
