---
name: gh-pr-ja
description: Draft or revise GitHub pull request titles and bodies in Japanese. Use when the user asks to create a PR, rewrite a PR body, add context from incidents or reviews, or normalize multiple PRs to the same Japanese structure and tone.
---

# Gh Pr Ja

## Overview

Use this skill when creating or editing GitHub PR titles and bodies in Japanese for engineering work. The default body structure is fixed so reviewers can scan the incident, the actual problem, the chosen approach, and the concrete changes without guessing.

## When To Use

- The user asks to create a PR or rewrite an existing PR body.
- The user asks to add context such as monitoring results, Cloud Logging links, review feedback, or latest incident timestamps to a PR.
- Multiple PRs need to be aligned to the same Japanese structure and tone.

## Default Body Structure

Use these sections in this order unless the user explicitly asks for a different structure:

1. `背景`
2. `問題`
3. `対策の方針`
4. `実際にやったこと`
5. `実行したコマンド`
6. `結果`

If a section has no content, omit it. Keep the first four sections whenever they are relevant.

## Writing Rules

- Write in Japanese plain form. Do not use polite endings such as `〜ました`, `〜です`, or `〜ます`.
- Keep bullets flat and short. One bullet should contain one point.
- In `背景`, explain the trigger for the PR. If the change came from monitoring or incident investigation, include the latest confirmed timestamp with timezone and a direct link such as Cloud Logging or the alert URL when available.
- In `問題`, describe the broken behavior, missing guardrail, or operational risk. Focus on what was wrong before the change.
- In `対策の方針`, explain the design choice and the guardrails being introduced. Separate benign cases from real errors when that distinction matters.
- In `実際にやったこと`, list concrete code, query, config, or test changes. Do not repeat rationale here.
- In `実行したコマンド`, list the exact verification commands and whether each succeeded.
- In `結果`, state the current state such as `成功`, remaining risk, or follow-up.

## Workflow

1. Sync the branch with the latest base branch before opening or updating the PR:
   identify the base branch, run `git fetch origin`, and rebase or merge the working branch onto the latest `origin/<base>` using the repository's standard flow. If conflicts appear, resolve them before drafting the PR body or running `gh pr create`. If the base branch advances again while the PR is open, repeat this step before finalizing the PR.
2. Gather the evidence needed to justify the PR:
   `git diff`, tests, CI results, review comments, incident logs, monitoring links, and latest occurrence timestamps.
3. Decide the title:
   keep it short, in Japanese, and consistent with the repository's commit or PR prefix conventions such as `fix:` or `feat:` when those conventions exist.
4. Draft the body using the default section order.
5. Remove fluff:
   do not narrate the work process; keep only reviewer-useful facts.
6. If the user asks to revise an existing PR:
   preserve the facts, but rewrite the structure and tone to match this skill.

## Example Skeleton

```md
## 背景
- Demo 環境のアラート調査で `...` が継続的に発生していた
- 最新確認: 2026年3月12日 09:40:55 JST（`...Z` / `revision-name`）
- Cloud Logging: [Log Explorer](https://console.cloud.google.com/logs/query;query=...)

## 問題
- ...

## 対策の方針
- ...

## 実際にやったこと
- ...

## 実行したコマンド
- `...` : 成功

## 結果
- 成功
```
