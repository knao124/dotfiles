---
name: gmail-search-gog
description: Search Gmail mailboxes with the `gog` CLI when the user asks to search email, Gmail, inbox, threads, or messages, including Japanese requests such as `メールを検索して`, `Gmailを調べて`, `受信メールを探して`, or `特定のメールを見つけて`.
---

# Gmail Search Gog

## Overview

Use this skill for Gmail search and inspection tasks. Prefer the locally installed `gog` CLI (Homebrew formula `gogcli`, binary `gog`) whenever the user asks to find emails, inspect matching messages, or summarize Gmail results.

## Preconditions

- Confirm `gog` is available on `PATH`.
- Check auth state with `gog auth list --check` and `gog auth status` before assuming search can run.
- If there is no usable token or no active account, stop and explain the missing setup. Do not invent mail results.

## Read-Only Default

- Default to read-only Gmail commands.
- Do not send, archive, trash, relabel, or otherwise modify mail unless the user explicitly asks.

## Workflow

1. Translate the user's request into Gmail query syntax.
2. Prefer thread search first:
   `gog gmail search '<query>' --max 10 --json --results-only`
3. Use message search when the user needs individual messages or body text:
   `gog gmail messages search '<query>' --max 10 --json --results-only`
4. Add `--include-body` only when the user needs body content.
5. If `gog` reports `missing --account`, ask which mailbox to search or use `-a <email>` when the account is already known.
6. Summarize matches in Japanese with sender, subject, time, and why each result matched.

## Query Patterns

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
gog gmail search 'from:alice@example.com newer_than:30d' --max 10 --json --results-only

# Search individual messages
gog gmail messages search 'subject:"請求書" has:attachment' --max 20 --json --results-only

# Include body text when needed
gog gmail messages search 'from:vendor@example.com newer_than:14d' --max 10 --include-body --json --results-only
```

## Output Rules

- Show the exact Gmail query used.
- State when results are truncated because of `--max`.
- Say clearly when there are no matches.
- Avoid dumping raw JSON unless the user explicitly asks for it.

## Setup Fallback

If `gog` is installed but Gmail auth is not configured, guide the user through:

```bash
gog auth credentials /path/to/client_secret.json
gog auth add you@example.com
```

If a default account is still not set, tell the user future searches should include `-a you@example.com` or set a default account in `gog`.
