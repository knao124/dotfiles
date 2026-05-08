#!/usr/bin/env bash

set -euo pipefail

DOTFILES_REPO="${DOTFILES_REPO:-$HOME/dev/dotfiles}"
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
