---
name: gmail-search-gog
description: Search Gmail mailboxes with the `gog` CLI when the user asks to search email, Gmail, inbox, threads, or messages, or to check recent or important mail. Use for Japanese requests such as `メールを検索して`, `Gmailを調べて`, `受信メールを探して`, `特定のメールを見つけて`, `重要なメールある？`, `直近1時間で重要なメール`, or `メールの原文を見せて`.
---

# Gmail Search Gog

## Overview

Use this skill for Gmail search, recent-mail triage, and message inspection tasks. Prefer the locally installed `gog` CLI (Homebrew formula `gogcli`, binary `gog`) whenever the user asks to find emails, inspect matching messages, summarize Gmail results, or check whether important mail has arrived.

## Preconditions

- Confirm `gog` is available on `PATH`.
- Check auth state with `gog auth list --check` and `gog auth status` before assuming search can run.
- If there is no usable token or no active account, stop and explain the missing setup. Do not invent mail results.

## Read-Only Default

- Default to read-only Gmail commands.
- Do not send, archive, trash, relabel, or otherwise modify mail unless the user explicitly asks.

## Workflow

1. Translate the user's request into Gmail query syntax.
2. Check the current local time with `date` when the request depends on "recent", "today", "last hour", or similar. Report the exact cutoff time you use.
3. Prefer thread search first:
   `gog gmail search '<query>' --max 10 --json`
4. Use message search when the user needs individual message times, labels, or body text:
   `gog gmail messages search '<query>' --max 10 --json`
5. For important-mail checks, combine `label:important`, `label:inbox`, `is:unread`, and `newer_than:` as needed. Distinguish unread matches from already-read matches.
6. If the user asks what the email says, or asks whether important mail has arrived, show the newly added original text for each matching important message. Omit long quoted history unless the user asks for the full chain.
7. Add `--include-body` only when quick body access is enough. If Japanese text is garbled or MIME placeholders make the body unreadable, use `scripts/fetch_message_bodies.py` with the message IDs from the search results.
8. If `gog` reports `missing --account`, ask which mailbox to search or use `-a <email>` when the account is already known.
9. Summarize matches in Japanese with sender, subject, time, and why each result matched.

## Query Patterns

- Important: `label:important`
- Inbox: `label:inbox`
- Sender: `from:alice@example.com`
- Recipient: `to:bob@example.com`
- Subject: `subject:"請求書"`
- Unread: `is:unread`
- Attachment: `has:attachment`
- Time filter: `newer_than:7d`
- Label: `label:inbox`

Combine filters with spaces and quote exact phrases when needed.

## Command Patterns

```bash
# Search matching threads
gog gmail search 'from:alice@example.com newer_than:30d' --max 10 --json

# Search individual messages
gog gmail messages search 'subject:"請求書" has:attachment' --max 20 --json

# Check recent important inbox mail
gog gmail messages search 'label:important label:inbox newer_than:1d' --max 20 --json

# Include body text when needed
gog gmail messages search 'from:vendor@example.com newer_than:14d' --max 10 --include-body --json

# Fetch decoded bodies when --include-body is unreadable
python3 scripts/fetch_message_bodies.py 19d0507d88c44627 19d05015e33c0917
```

## Output Rules

- Show the exact Gmail query used.
- State when results are truncated because of `--max`.
- Say clearly when there are no matches.
- For recent-mail requests, include the current time and cutoff time in absolute form.
- When showing message text, label each block with sender, subject, and received time.
- Avoid dumping raw JSON unless the user explicitly asks for it.

## Setup Fallback

If `gog` is installed but Gmail auth is not configured, guide the user through:

```bash
gog auth credentials /path/to/client_secret.json
gog auth add you@example.com
```

If a default account is still not set, tell the user future searches should include `-a you@example.com` or set a default account in `gog`.
