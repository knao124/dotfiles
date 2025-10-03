#!/bin/zsh

# コマンド失敗/未定義変数/パイプ中いずれか、で失敗したらfailする
set -euo pipefail

DF_REPO_PATH="$HOME/dev/dotfiles"

# claude
cp ~/.claude/settings.json $DF_REPO_PATH/.claude/
cp ~/.claude/CLAUDE.md $DF_REPO_PATH/.claude/
cp ~/.claude/commands/* $DF_REPO_PATH/.claude/commands/ 2>/dev/null || true
cp ~/.claude/agents/* $DF_REPO_PATH/.claude/agents/ 2>/dev/null || true

# codex (only the public config, not private projects)
mkdir -p $DF_REPO_PATH/.codex
cp ~/.codex/config.toml $DF_REPO_PATH/.codex/ 2>/dev/null || true
if [[ -d ~/.codex/prompts ]]; then
  cp -rp ~/.codex/prompts/* $DF_REPO_PATH/.codex/prompts/ 2>/dev/null || true
fi

# scripts
cp -rp ~/.scripts/ $DF_REPO_PATH/.scripts

# zsh
cp ~/.zsh/alias.zsh $DF_REPO_PATH/.zsh/
cp ~/.zshrc $DF_REPO_PATH/

# tmux
cp ~/.tmux.conf $DF_REPO_PATH/


echo "$HOME の dotfiles を $DF_REPO_PATH にコピーしました。"
