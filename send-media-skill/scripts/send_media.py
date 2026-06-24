#!/usr/bin/env python3
"""
send_media.py — idempotent media sender for openclaw agents.

Deduplication: once a file with the same path is sent today (CST),
subsequent calls with the same path are silently skipped (exit 0).
Lock file: /tmp/media_sent_<sha256_of_abspath_date>.lock

Usage:
  python3 send_media.py /path/to/file.pdf [caption]
  python3 send_media.py /path/to/file.pdf [caption] --resend   # force resend (user explicitly says not received)

Output:
  If not yet sent today → print caption (if any), then print MEDIA:/path/to/file
  If already sent today → print SKIP — already sent today: <filename>

The caller (agent) must copy the MEDIA: line verbatim into its reply text.
The gateway will pick up MEDIA: from the agent's reply and deliver the file.
"""

import argparse
import datetime
import hashlib
import os
import sys

LOCK_DIR = "/tmp"
CST = datetime.timezone(datetime.timedelta(hours=8))


def dedup_key(path: str) -> str:
    today = datetime.datetime.now(CST).strftime("%Y-%m-%d")
    raw = f"{os.path.abspath(path)}|{today}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def lock_path(path: str) -> str:
    return os.path.join(LOCK_DIR, f"media_sent_{dedup_key(path)}.lock")


def already_sent(path: str) -> bool:
    return os.path.exists(lock_path(path))


def mark_sent(path: str):
    with open(lock_path(path), "w") as f:
        f.write(datetime.datetime.now(CST).isoformat())


def clear_lock(path: str):
    lp = lock_path(path)
    if os.path.exists(lp):
        os.remove(lp)


def main():
    parser = argparse.ArgumentParser(description="Idempotent media sender")
    parser.add_argument("filepath", help="Path to file to send")
    parser.add_argument("caption", nargs="?", default="", help="Optional caption text")
    parser.add_argument("--resend", action="store_true",
                        help="Force resend even if already sent today (only when user explicitly says not received)")
    args = parser.parse_args()

    filepath = args.filepath
    caption = args.caption.strip()

    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    if args.resend:
        clear_lock(filepath)

    if already_sent(filepath):
        print(f"SKIP — already sent today: {os.path.basename(filepath)}")
        sys.exit(0)

    mark_sent(filepath)
    if caption:
        print(caption)
    print(f"MEDIA:{filepath}")
    sys.exit(0)


if __name__ == "__main__":
    main()
