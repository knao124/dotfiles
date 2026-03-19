#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from email import message_from_bytes
from email.message import Message
from email.policy import default
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        raise SystemExit(proc.returncode)
    return proc.stdout


def default_account() -> str:
    output = run_command(["gog", "auth", "list", "--check"])
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 5 and parts[4].strip().lower() == "true":
            return parts[0].strip()
    raise SystemExit("No active gog account found. Pass --account explicitly.")


def credentials_path() -> Path:
    output = run_command(["gog", "auth", "status"])
    for line in output.splitlines():
        if line.startswith("credentials_path\t"):
            return Path(line.split("\t", 1)[1].strip())
    raise SystemExit("Could not determine gog credentials_path.")


def refresh_token_for(account: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        token_path = Path(td) / "token.json"
        run_command(
            [
                "gog",
                "auth",
                "tokens",
                "export",
                account,
                "--out",
                str(token_path),
                "--overwrite",
            ]
        )
        token = json.loads(token_path.read_text())
    return token["refresh_token"]


def access_token(account: str) -> str:
    creds = json.loads(credentials_path().read_text())
    payload = urllib.parse.urlencode(
        {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": refresh_token_for(account),
            "grant_type": "refresh_token",
        }
    ).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=payload)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["access_token"]


def decode_part(part: Message) -> str:
    try:
        return part.get_content()
    except Exception:
        payload = part.get_payload(decode=True) or b""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")


def html_to_text(value: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", value)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"(?s)<[^>]+>", "", text)
    return html.unescape(text).strip()


def extract_body(msg: Message) -> str:
    plain_parts: list[str] = []
    html_parts: list[str] = []
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            continue
        content_type = part.get_content_type()
        if content_type == "text/plain":
            text = decode_part(part).strip()
            if text:
                plain_parts.append(text)
        elif content_type == "text/html":
            text = html_to_text(decode_part(part))
            if text:
                html_parts.append(text)
    if plain_parts:
        return "\n\n".join(plain_parts).strip()
    if html_parts:
        return "\n\n".join(html_parts).strip()
    return ""


def fetch_message(message_id: str, token: str) -> dict[str, str]:
    req = urllib.request.Request(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=raw",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as resp:
        payload = json.loads(resp.read().decode())
    raw = payload["raw"]
    mime_bytes = base64.urlsafe_b64decode(raw + ("=" * (-len(raw) % 4)))
    msg = message_from_bytes(mime_bytes, policy=default)
    return {
        "id": message_id,
        "subject": str(msg.get("Subject", "")),
        "from": str(msg.get("From", "")),
        "date": str(msg.get("Date", "")),
        "body": extract_body(msg),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and decode Gmail message bodies using gog auth."
    )
    parser.add_argument("message_ids", nargs="+", help="Gmail message IDs")
    parser.add_argument("--account", help="Account email for gog auth")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    account = args.account or default_account()
    token = access_token(account)
    data = [fetch_message(message_id, token) for message_id in args.message_ids]
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
