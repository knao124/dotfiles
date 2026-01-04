---
allowed-tools: Bash, Read, Write
description: セッションの議論内容を論点・質疑・結論形式でまとめる
argument-hint: [sessionId または project パス] (省略可 - 省略時は現在のプロジェクトの最新セッション)
---

## Your Task

指定されたセッション（または現在のプロジェクトの最新セッション）の会話を分析し、論点・質疑・結論形式でまとめてください。

### データソース

`~/.claude/projects/[encoded-project-path]/[sessionId].jsonl`

各行はJSONで以下の形式:
```json
// ユーザーメッセージ
{"type": "user", "message": {"role": "user", "content": "..."}}

// アシスタントメッセージ
{"type": "assistant", "message": {"content": [{"type": "text", "text": "..."}]}}
```

### 手順

1. **セッションファイルを特定**

   引数がない場合、現在のプロジェクトの最新セッションを使用:
   ```bash
   # プロジェクトパスをエンコード（/ を - に、先頭に - を追加）
   /bin/bash -c 'PROJECT_DIR=$(pwd | sed "s|/|-|g"); ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl 2>/dev/null | grep -v "agent-" | head -1'
   ```

   引数がある場合:
   - UUID形式なら sessionId として扱う
   - パス形式なら project パスとして扱う

2. **会話を抽出**
   ```bash
   /bin/bash -c 'cat [session.jsonl] | jq -r "select(.type == \"user\" or .type == \"assistant\") | if .type == \"user\" then \"USER: \" + (.message.content | if type == \"string\" then . else (. | map(select(.type == \"text\") | .text) | join(\"\")) end) else \"ASSISTANT: \" + (.message.content | map(select(.type == \"text\") | .text) | join(\"\")) end" 2>/dev/null'
   ```

3. **会話を分析して論点を抽出**

   会話全体を読み、以下を特定:
   - 議論された論点（トピック）
   - 各論点に対するユーザーの質問・疑問
   - 各論点に対する結論・決定事項
   - 作成・更新されたファイル

### 出力フォーマット

```markdown
# セッションサマリー

**プロジェクト**: [project name]
**セッションID**: [session id]
**日時**: [timestamp range]

## 論点まとめ

| #   | 論点 | 質疑 | 結論 |
|-----|------|------|------|
| 1   | [論点1] | [質問・議論の要約] | [決定事項・結論] |
| 2   | [論点2] | [質問・議論の要約] | [決定事項・結論] |
...

## 作成・更新したドキュメント

| ファイル | 内容 |
|----------|------|
| file1.md | 概要 |
...

## 未決定・持ち越し事項

- [ ] 項目1
- [ ] 項目2
```

### ガイドライン

1. **論点の粒度**: 1つの大きなトピックは1行。サブトピックは結論欄に含める
2. **質疑の要約**: ユーザーの発言を「」で引用しつつ簡潔に
3. **結論の明確化**: 決まったこと、採用されたアプローチを具体的に
4. **未決定事項**: 議論されたが結論が出なかったものは別セクションに
5. **ファイル操作の追跡**: Write/Edit ツールの使用からファイル操作を抽出
6. **日本語で出力**

### 注意事項

- tool_use や tool_result は内容理解の補助に使うが、出力には含めない
- thinking ブロックは無視
- 長いセッションの場合、主要な論点に絞る（10項目程度を上限）
