---
name: gws-save-google-docs
description: Save the current conversation, summary, or deliverable to Google Docs with the `gws` CLI when the user asks to save something to Google Docs, create a Google Doc from the current interaction, or append notes to an existing Google Docs document. Trigger on requests such as `Google Docsに保存して`, `このやりとりをDocsに残して`, `この内容をドキュメントに追記して`, or `Googleドキュメント化して`.
---

# Gws Save Google Docs

## Overview

Use this skill when the user wants to save the current conversation, its key points, or the resulting deliverable to Google Docs. Prefer the locally configured `gws` CLI and save a concise, structured note by default.

Only save a near-verbatim transcript when the user explicitly asks for `会話をそのまま保存`, `全文を残して`, or an equivalent instruction. Never include hidden reasoning, secrets, tokens, or raw credential material.

## Preconditions

- Confirm `gws` is available on `PATH`.
- Check `gws auth status` before writing anything.
- If `gws` auth is missing or invalid, stop and explain what is not configured.
- Prefer `gws docs documents create` for new docs and `gws docs +write` for plain-text append.

## Target Document Decision

1. If the user provides a Google Docs URL or document ID, append to that document.
2. If the user says `追記して`, `append`, or `既存のDocsに保存` and the target is already known in the current turn, append there.
3. If no target is given, create a new document.
4. If the user gives a title, use it. Otherwise default to `Codex Notes YYYY-MM-DD HH:mm JST`.

If the target is a URL, extract the document ID from the segment between `/d/` and the next `/`.

## Save Format

Default to a compact structure like this:

```text
<title>

保存日時: 2026-03-19 19:30 JST
依頼:
<user request>

要点:
- key point
- key point

回答:
<final answer or deliverable summary>

補足:
- commands used
- relevant file paths
- relevant links
```

Formatting rules:

- Prefer concise notes over a full transcript.
- Preserve user wording only when precision matters.
- Include file paths, commands, document URLs, or IDs only when they help the user later.
- Exclude chain-of-thought, raw tool output dumps, auth codes, refresh tokens, client secrets, and unrelated noise.

## Workflow

1. Determine whether to append to an existing doc or create a new one.
2. Build the text to save from the current conversation:
   - Default: summarize the user request, important constraints, and the final result.
   - Explicit full-log request: save a speaker-labeled transcript using `User:` and `Assistant:`.
3. Create the doc when needed:

```bash
TITLE="Codex Notes 2026-03-19 19:30 JST"
DOC_ID="$(
  gws docs documents create \
    --json "$(jq -nc --arg title "$TITLE" '{title:$title}')" \
  | jq -r '.documentId'
)"
```

4. Append the prepared text:

```bash
gws docs +write --document "$DOC_ID" --text "$BODY"
```

5. Build the editable link:

```text
https://docs.google.com/document/d/<DOC_ID>/edit
```

6. In the user-facing final response, paste that URL explicitly. Prefer a standalone Markdown link plus a short note saying whether the document was created or appended.

## Command Patterns

```bash
# 認証状態確認
gws auth status

# 新規作成
gws docs documents create --json '{"title":"Codex Notes 2026-03-19 19:30 JST"}'

# 本文追記
gws docs +write --document DOC_ID --text $'依頼:\n...\n\n回答:\n...'

# 既存ドキュメント取得
gws docs documents get --params '{"documentId":"DOC_ID"}'
```

## Output Rules

- Final responseでは保存先の Google Docs URL を必ず貼る。URL omission is not allowed.
- Prefer this shape in the final response:

```markdown
[Google Docs](https://docs.google.com/document/d/<DOC_ID>/edit)
```

- 新規作成か追記かを明示する。
- 保存した内容は 1-3 行で要約する。
- 失敗した場合は、どの前提が欠けていたかだけを簡潔に伝える。

## Example Triggers

- `このやりとりをGoogle Docsに保存して`
- `この回答をDocsに残して`
- `この内容をこのGoogle Docsに追記して https://docs.google.com/document/d/.../edit`
- `今日の作業内容をGoogleドキュメント化して`
