# Guidelines

Codex と共通の指示は `~/.codex/AGENTS.md`（dotfiles リポジトリ直下の `AGENTS.md`）で管理する。
このファイルには Claude Code 固有の指示だけを書く。

@~/.codex/AGENTS.md

## Top-Level Rules

- To maximize efficiency, **if you need to execute multiple independent processes, invoke those tools concurrently, not sequentially**.
- **You must think exclusively in English**.
- **シェルコマンド実行時**: zsh と bash の互換性問題を避けるため、複雑なコマンド置換やパイプラインを使う場合は `/bin/bash -c '...'` で明示的に bash を使用する
- **パッケージ仕様の調査優先順位**: LSP（コード） → Context7 MCP → Web 検索の順で調べる
  1. まず LSP（goToDefinition, hover）で型定義・実装を確認（コードが最も正確）
  2. 不足する場合は Context7 MCP でライブラリの公式ドキュメントを取得
  3. それでも不明な場合のみ Web 検索を使用
- For temporary notes for design, create a markdown in `.tmp` and save it.
- **After using Write or Edit tools, ALWAYS verify the actual file contents using the Read tool**, regardless of what the system-reminder says. The system-reminder may incorrectly show "(no content)" even when the file has been successfully written.
- Please respond critically and without pandering to my opinions, but please don't be forceful in your criticism.

## Programming Rules

- Avoid hard-coding values unless absolutely necessary.
- Do not use `any` or `unknown` types in TypeScript.
- You must not use a TypeScript `class` unless it is absolutely necessary (e.g., extending the `Error` class for custom error handling that requires `instanceof` checks).
