---
allowed-tools: Bash, Read, Write
description: 今日のClaude Codeセッション履歴から日報を生成する
argument-hint: [出力先パス] (省略可 - 省略時はターミナルに出力)
---

## Your Task

Claude Codeの今日のセッション履歴を分析し、日報を生成してください。

### データソース

`~/.claude/history.jsonl` - 各行がJSONで以下の形式:
```json
{
  "display": "ユーザーの入力",
  "timestamp": 1234567890123,
  "project": "/path/to/project",
  "sessionId": "uuid"
}
```

### 手順

1. **今日のセッションを抽出**
   ```bash
   /bin/bash -c 'TODAY_START=$(date -j -f "%Y-%m-%d %H:%M:%S" "$(date +%Y-%m-%d) 00:00:00" +%s)000; cat ~/.claude/history.jsonl | jq -r "select(.timestamp >= $TODAY_START)"'
   ```

2. **プロジェクトごとにグループ化**
   - プロジェクトパスから最後の2階層を抽出（例: `ridgebull/ai-ocr-agent`）
   - 各プロジェクトの入力内容を時系列で整理

3. **日報形式で整理**
   - プロジェクトごとのセクション
   - 何をしたかを箇条書きで要約
   - コマンド（`/`で始まる入力）は除外または別枠

### 出力フォーマット

```markdown
# 日報 YYYY-MM-DD

## サマリー
- 作業プロジェクト数: N
- 主な作業: [最も入力が多かったプロジェクト]

## プロジェクト別作業内容

### [org/project-name]
- 作業1の概要
- 作業2の概要
...

### [org/project-name2]
...
```

### ガイドライン

1. **入力内容を分析**: ユーザーの入力から何をしていたかを推測・要約
2. **重複排除**: 似た入力はまとめる
3. **時系列順**: 各プロジェクト内は時系列で整理
4. **日本語で出力**
5. **コマンド除外**: `/resume`, `/clear`, `/plugin` などのメタコマンドは内容から除外

引数で出力先パスが指定されていればファイルに保存。なければターミナルに出力してください。
