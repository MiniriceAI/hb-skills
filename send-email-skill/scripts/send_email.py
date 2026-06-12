#!/usr/bin/env python3
"""
send_email.py — idempotent email sender for openclaw agents.

Deduplication: once an email with the same subject is sent today (CST),
subsequent calls with the same subject are silently skipped (exit 0).
Lock file: /tmp/email_sent_<sha256_of_subject_date>.lock

Usage:
  python3 send_email.py --subject "Title" --file /path/to/report.md
  python3 send_email.py --subject "Title" --body "content text"
  python3 send_email.py --subject "Title" --file report.md --to other@example.com
"""

import argparse
import hashlib
import os
import smtplib
import subprocess
import sys
import datetime

# ─── Config ───────────────────────────────────────────────────────────────────
DEFAULT_TO   = "minirice2017@gmail.com"
DEFAULT_FROM = "minirice2017@gmail.com"
LOCK_DIR     = "/tmp"
CST          = datetime.timezone(datetime.timedelta(hours=8))

# ─── Helpers ──────────────────────────────────────────────────────────────────

def dedup_key(subject: str) -> str:
    today = datetime.datetime.now(CST).strftime("%Y-%m-%d")
    raw = f"{subject.strip()}|{today}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def lock_path(subject: str) -> str:
    return os.path.join(LOCK_DIR, f"email_sent_{dedup_key(subject)}.lock")

def already_sent(subject: str) -> bool:
    return os.path.exists(lock_path(subject))

def mark_sent(subject: str):
    with open(lock_path(subject), "w") as f:
        f.write(datetime.datetime.now(CST).isoformat())

def md_to_html(text: str) -> str:
    """Best-effort markdown → HTML via python-markdown or pandoc fallback."""
    try:
        import markdown
        return markdown.markdown(text, extensions=["extra", "nl2br"])
    except ImportError:
        pass
    try:
        result = subprocess.run(
            ["pandoc", "--from=markdown", "--to=html"],
            input=text.encode(), capture_output=True, timeout=15
        )
        if result.returncode == 0:
            return result.stdout.decode()
    except Exception:
        pass
    # Plaintext fallback wrapped in <pre>
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"<pre style='font-family:sans-serif;white-space:pre-wrap'>{escaped}</pre>"

def build_message(subject: str, body_html: str, to_addr: str) -> str:
    import email.mime.multipart
    import email.mime.text
    msg = email.mime.multipart.MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = DEFAULT_FROM
    msg["To"]      = to_addr
    msg.attach(email.mime.text.MIMEText(body_html, "html", "utf-8"))
    return msg.as_string()

def send_via_msmtp(raw_message: str, to_addr: str) -> bool:
    try:
        result = subprocess.run(
            ["msmtp", "--", to_addr],
            input=raw_message.encode(),
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True
        print(f"msmtp error: {result.stderr.decode()[:300]}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("msmtp not found — is it installed?", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("msmtp timed out", file=sys.stderr)
        return False

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Send HTML email via msmtp (idempotent)")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--file",    help="Markdown or HTML file to send as body")
    parser.add_argument("--body",    help="Plain text / markdown body")
    parser.add_argument("--to",      default=DEFAULT_TO, help="Recipient email")
    parser.add_argument("--force",   action="store_true", help="Ignore dedup lock")
    args = parser.parse_args()

    # ── Dedup check ────────────────────────────────────────────────────────────
    if not args.force and already_sent(args.subject):
        today = datetime.datetime.now(CST).strftime("%Y-%m-%d")
        print(f"[send_email] SKIP — '{args.subject}' already sent today ({today}). Use --force to override.")
        sys.exit(0)

    # ── Load body ──────────────────────────────────────────────────────────────
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            raw_body = fh.read()
    elif args.body:
        raw_body = args.body
    else:
        print("Error: --file or --body required", file=sys.stderr)
        sys.exit(1)

    body_html = md_to_html(raw_body)

    # ── Build and send ─────────────────────────────────────────────────────────
    raw_msg = build_message(args.subject, body_html, args.to)
    print(f"[send_email] Sending '{args.subject}' to {args.to} ...")
    if send_via_msmtp(raw_msg, args.to):
        mark_sent(args.subject)
        print(f"[send_email] Sent OK.")
    else:
        print("[send_email] FAILED to send email.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
