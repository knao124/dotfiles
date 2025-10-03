#!/usr/bin/env bash

# コマンド失敗/未定義変数/パイプ中いずれか、で失敗したらfailする
set -euo pipefail

# エラー時に呼ばれる関数
error_handler() {
    echo "エラーが発生しました: 行 $1" >&2
    echo "コマンド: $2" >&2
    exit 1
}

# エラートラップを設定
trap 'error_handler $LINENO "$BASH_COMMAND"' ERR

# Simple, quiet copy of selected dotfiles from repo to $HOME
DOTFILES_REPO="${DOTFILES_REPO:-$HOME/dev/dotfiles}"

# 指定した各アイテムを順番に処理
SYNC_ITEMS=(
  ".zsh"
  ".zshrc"
  ".tmux.conf"
  ".claude"
  ".scripts"
)
for item in "${SYNC_ITEMS[@]}"; do
  echo "処理中: $item"
  # src: リポジトリ内のファイル
  src="$DOTFILES_REPO/$item"
  # dst: ホームディレクトリ内のファイル
  dst="$HOME/$item"
  
  # srcがディレクトリの場合
  if [[ -d "$src" ]]; then
    # dstディレクトリを作成
    mkdir -p "$dst"
    # rsyncが利用可能ならrsyncを使用、そうでなければcpを使用してsrcのディレクトリをdstにコピー
    if command -v rsync >/dev/null 2>&1; then
      rsync -a "$src/" "$dst/" >/dev/null 2>&1
    else
      cp -R "$src/." "$dst" >/dev/null 2>&1
    fi
  # ソースがファイルの場合
  elif [[ -f "$src" ]]; then
    # dstファイルの親ディレクトリを作成
    mkdir -p "$(dirname "$dst")"
    # srcのファイルをdstにコピー
    cp -f "$src" "$dst" >/dev/null 2>&1
  else
    echo "  警告: $src が見つかりません"
  fi
done

# Codexの設定をコピー
if [[ -d "$DOTFILES_REPO/.codex" ]]; then
  echo "処理中: .codex"
  mkdir -p "$HOME/.codex"
  cp -f "$DOTFILES_REPO/.codex/config.toml" "$HOME/.codex/config.toml" >/dev/null 2>&1
  if [[ -d "$DOTFILES_REPO/.codex/prompts" ]]; then
    mkdir -p $HOME/.codex/prompts
    cp -rp $DOTFILES_REPO/.codex/prompts/* $HOME/.codex/prompts/ >/dev/null 2>&1
  fi
fi

echo "以下の dotfiles を $HOME に配置しました。"
for item in "${SYNC_ITEMS[@]}"; do
  echo "  $item"
done
if [[ -d "$DOTFILES_REPO/.codex" ]]; then
  echo "  .codex"
fi