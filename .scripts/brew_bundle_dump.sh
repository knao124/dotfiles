#!/usr/bin/env bash

set -euo pipefail

DOTFILES_REPO="${DOTFILES_REPO:-$HOME/dev/dotfiles}"
BREWFILE_PATH="$DOTFILES_REPO/Brewfile"

if ! command -v brew >/dev/null 2>&1; then
  echo "brew が見つかりません。" >&2
  exit 1
fi

mkdir -p "$(dirname "$BREWFILE_PATH")"

brew bundle dump \
  --file "$BREWFILE_PATH" \
  --force \
  --no-vscode \
  --no-go \
  --no-cargo \
  --no-uv \
  --no-flatpak \
  --no-krew \
  --no-npm \
  --no-restart \
  "$@"
