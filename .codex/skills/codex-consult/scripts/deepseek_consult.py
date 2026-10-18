#!/usr/bin/env python3
"""Send only inspected text to DeepSeek; never give the model local tools."""

import argparse
import base64
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import ssl
import sys
import unicodedata
from urllib.parse import unquote

HOST = "api.deepseek.com"
MAX_INPUT = 64 * 1024
DEFAULT_KEY_FILE = Path.home() / ".config/deepseek/api-key"
WARNING = (
    "警告: DeepSeekは再学習に利用され得る外部サービスです。"
    "送信経路はセキュリティホールになり得ます。"
    "認証情報・秘密情報をモデルへ絶対に送らないでください。"
    "自動検査は安全を保証しません。Codexによる内容確認が必要です。"
)
INSTRUCTIONS = (
    "あなたは設計相談・議論・コードレビューの相談役です。"
    "提示された資料だけを検討し、事実と推測、未確認事項を区別してください。"
    "指定された観点に限らず、前提の誤りと具体的な代替案も指摘してください。"
    "ローカルファイルや環境変数へアクセスする手段はありません。"
    "認証情報、秘密ファイル、非公開データの提出を要求しないでください。"
    "コマンド実行や別エージェントへの委譲はせず、日本語で回答してください。"
)
SENSITIVE_NAME = re.compile(r"(?:^|_)(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIALS?|COOKIE|AUTH)(?:_|$)", re.I)
PATTERNS = [
    ("秘密鍵", r"-----BEGIN (?:[A-Z0-9 ]*PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----"),
    ("既知のトークン形式", r"\b(?:sk-[A-Za-z0-9_-]{12,}|(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{12,}|xox[baprs]-[A-Za-z0-9-]{10,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{30,})\b"),
    ("JWT", r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    ("認証ヘッダー", r"\b(?:authorization|proxy-authorization|cookie|set-cookie)\b[\"']?\s*[:=]"),
    ("認証方式と値", r"\b(?:bearer|basic)\s+[A-Za-z0-9+/_.=-]{8,}"),
    ("認証値の代入", r"\b(?:[A-Z0-9_]*(?:API[_-]?KEY|ACCESS[_-]?KEY|SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*|pwd|client_secret|private_key)\b[\"']?\s*[:=]"),
    ("日本語の認証値", r"(?:APIキー|パスワード|秘密鍵|アクセストークン|認証情報)\s*[:=：]"),
    ("認証付きURL", r"[a-z][a-z0-9+.-]*://[^\s/@]+:[^\s/@]+@"),
    ("署名付きURL", r"[?&](?:x-amz-signature|x-goog-signature|signature|sig|access_token|api_key|token|password|key)="),
    ("秘密ファイルのパス", r"(?:^|[/\\\s\"'`])(?:\.env(?:\.[\w.-]+)?|(?:credentials|secrets?|tokens?|passwords?|keys?)(?:\.[\w.-]+)?|id_(?:rsa|ed25519)|[^\s/\\]+\.(?:pem|p12|pfx))(?=$|[/\\\s\"'`:])|[.]codex[/\\]auth[.]json"),
]


class UnsafeInput(ValueError):
    pass


def inspect_text(text, known_values=()):
    """Reject rather than redact. Never include matched values in errors."""
    normalized = unicodedata.normalize("NFKC", text)
    variants = [normalized, unquote(normalized)]
    for label, pattern in PATTERNS:
        if any(re.search(pattern, v, re.I | re.M) for v in variants):
            raise UnsafeInput("送信禁止: " + label + "を検出しました。内容は表示しません。")
    values = list(known_values)
    values.extend(v for k, v in os.environ.items() if SENSITIVE_NAME.search(k) and len(v) >= 4)
    for value in values:
        if not value:
            continue
        encoded = value.encode()
        forms = [value, base64.b64encode(encoded).decode(), base64.urlsafe_b64encode(encoded).decode(), encoded.hex()]
        if any(form in variant for form in forms for variant in variants):
            raise UnsafeInput("送信禁止: 認証用の値を検出しました。内容は表示しません。")


def read_prompt(path):
    # Resolve symlinks so a harmless alias cannot conceal a known secret path.
    inspect_text(str(path.resolve()))
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT + 1)
    if not raw.strip() or len(raw) > MAX_INPUT:
        raise ValueError("入力は空ではない64KiB以下の文章にしてください。")
    text = raw.decode("utf-8")
    inspect_text(text)
    return text


def read_api_key(key_file):
    source = key_file or os.environ.get("DEEPSEEK_API_KEY_FILE")
    if not source and not os.environ.get("DEEPSEEK_API_KEY") and DEFAULT_KEY_FILE.is_file():
        source = DEFAULT_KEY_FILE
    if source:
        with Path(source).expanduser().open("r", encoding="utf-8") as stream:
            key = stream.read(4097).strip()
        if key.startswith("export "):
            key = key[7:].strip()
        if key.startswith("DEEPSEEK_API_KEY="):
            key = key.split("=", 1)[1].strip()
        key = key.strip("\"'")
    else:
        key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key or len(key) > 4096 or any(c in key for c in "\r\n"):
        raise ValueError("DeepSeek専用APIキーを環境変数かローカルファイルに設定してください。")
    return key


def send(text, key):
    inspect_text(text, [key])
    payload = {
        "model": "deepseek-flash",
        "instructions": INSTRUCTIONS,
        "input": text,
        "max_output_tokens": 4096,
        "reasoning": {"effort": "high"},
        "store": False,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    inspect_text(INSTRUCTIONS, [key])
    # http.client does not consume HTTP(S)_PROXY or follow redirects.
    connection = http.client.HTTPSConnection(HOST, 443, timeout=120, context=ssl.create_default_context())
    try:
        connection.request("POST", "/responses", body=body, headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        })
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("DeepSeek APIでHTTP " + str(response.status) + "。本文は表示せず停止しました。")
        raw = response.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("API応答が上限を超えたため停止しました。")
    finally:
        connection.close()
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("API応答の形式が不正なため停止しました。")
    if result.get("status") != "completed":
        raise ValueError("応答が完了していません。自動再試行せず停止しました。")
    output = "\n".join(
        part.get("text", "")
        for item in result.get("output", []) if item.get("type") == "message"
        for part in item.get("content", []) if part.get("type") == "output_text"
    )
    if not output.strip():
        raise ValueError("文章の応答がありません。ツール呼び出しは実行しません。")
    inspect_text(output, [key])
    usage = result.get("usage", {})
    # Print only numeric usage fields, never arbitrary server error/log content.
    summary = {k: usage[k] for k in ("input_tokens", "output_tokens", "total_tokens") if type(usage.get(k)) is int}
    print("DeepSeek使用量: " + json.dumps(summary), file=sys.stderr)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=WARNING)
    parser.add_argument("--input", required=True, type=Path, help="Codexが選別・確認した相談文")
    parser.add_argument("--send", action="store_true", help="検査後に送信。未指定ならローカル検査のみ")
    parser.add_argument("--key-file", help="認証専用のローカルファイルのパス。キーの値は指定しない")
    args = parser.parse_args(argv)
    print(WARNING, file=sys.stderr)
    try:
        text = read_prompt(args.input)
        if not args.send:
            # If configured, also check the exact authentication key locally.
            if args.key_file or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY_FILE") or DEFAULT_KEY_FILE.is_file():
                inspect_text(text, [read_api_key(args.key_file)])
            digest = hashlib.sha256(text.encode()).hexdigest()
            print("ローカル検査通過。外部送信なし。SHA256=" + digest)
            return 0
        key = read_api_key(args.key_file)
        print(send(text, key))
        return 0
    except (UnsafeInput, ValueError) as error:
        # ValueError messages above are fixed, with no content or credential values.
        if isinstance(error, (json.JSONDecodeError, UnicodeError)):
            print("入力または応答の形式が不正です。内容は表示せず停止しました。", file=sys.stderr)
        else:
            print(str(error), file=sys.stderr)
        return 1
    except (OSError, http.client.HTTPException):
        print("ファイルまたは通信の処理に失敗しました。詳細を表示せず停止しました。", file=sys.stderr)
        return 1
    except Exception:
        # Malformed remote responses must not produce a traceback containing data.
        print("処理に失敗しました。内容を表示せず停止しました。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
