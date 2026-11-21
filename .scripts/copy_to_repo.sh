#!/bin/zsh

# コマンド失敗/未定義変数/パイプ中いずれか、で失敗したらfailする
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# リポジトリ内から実行した場合はそのリポジトリ、~/.scripts から実行した場合は ghq レイアウトの既定パスを使う
DF_REPO_PATH="${DOTFILES_REPO:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$(git config --get ghq.root || echo "$HOME/dev")/github.com/knao124/dotfiles")}"

# claude
cp ~/.claude/settings.json $DF_REPO_PATH/.claude/
cp ~/.claude/CLAUDE.md $DF_REPO_PATH/.claude/
cp ~/.claude/commands/* $DF_REPO_PATH/.claude/commands/ 2>/dev/null || true
cp ~/.claude/agents/* $DF_REPO_PATH/.claude/agents/ 2>/dev/null || true

# codex (only the public config, not private projects)
mkdir -p $DF_REPO_PATH/.codex
cp ~/.codex/config.toml $DF_REPO_PATH/.codex/ 2>/dev/null || true
if [[ -f "$HOME/.codex/AGENTS.md" ]]; then
  cp "$HOME/.codex/AGENTS.md" "$DF_REPO_PATH/AGENTS.md"
fi
if [[ -d ~/.codex/prompts ]]; then
  mkdir -p $DF_REPO_PATH/.codex/prompts
  cp -rp ~/.codex/prompts/* $DF_REPO_PATH/.codex/prompts/ 2>/dev/null || true
fi
if [[ -d ~/.codex/skills ]]; then
  mkdir -p $DF_REPO_PATH/.codex/skills
  cp -rp ~/.codex/skills/* $DF_REPO_PATH/.codex/skills/ 2>/dev/null || true
fi

# 個人用Agent Skills（ロックファイルなどの端末固有情報は含めない）
if [[ -d "$HOME/.agents/skills" ]]; then
  mkdir -p "$DF_REPO_PATH/.agents/skills"
  cp -rp "$HOME/.agents/skills/." "$DF_REPO_PATH/.agents/skills/"
fi

# scripts
cp -rp ~/.scripts/ $DF_REPO_PATH/.scripts

# zsh
mkdir -p $DF_REPO_PATH/.zsh
if command -v rsync >/dev/null 2>&1; then
  rsync -a ~/.zsh/ $DF_REPO_PATH/.zsh/ >/dev/null 2>&1
else
  cp -R ~/.zsh/. $DF_REPO_PATH/.zsh
fi
cp ~/.zshrc $DF_REPO_PATH/

# tmux
cp ~/.tmux.conf $DF_REPO_PATH/


echo "$HOME の dotfiles を $DF_REPO_PATH にコピーしました。"
