# direnv
# repo ごとの環境変数は .envrc に寄せる。未インストール環境では何もしない。
if (( $+commands[direnv] )) && [[ -z "${__DOTFILES_DIRENV_HOOK_LOADED:-}" ]]; then
  eval "$(direnv hook zsh)"
  __DOTFILES_DIRENV_HOOK_LOADED=1
fi
