#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# リポジトリ内から実行した場合はそのリポジトリ、~/.scripts から実行した場合は ghq レイアウトの既定パスを使う
DOTFILES_REPO="${DOTFILES_REPO:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$(git config --get ghq.root || echo "$HOME/dev")/github.com/knao124/dotfiles")}"
BREWFILE_PATH="$DOTFILES_REPO/Brewfile"

if ! command -v brew >/dev/null 2>&1; then
  echo "brew が見つかりません。" >&2
  exit 1
fi

if [[ ! -f "$BREWFILE_PATH" ]]; then
  echo "Brewfile が見つかりません: $BREWFILE_PATH" >&2
  exit 1
fi

bundle_args=(install --file "$BREWFILE_PATH" --no-upgrade)
for arg in "$@"; do
  if [[ "$arg" == "--upgrade" ]]; then
    bundle_args=(install --file "$BREWFILE_PATH")
    break
  fi
done

brew bundle "${bundle_args[@]}" "$@"
