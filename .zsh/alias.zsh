# core
alias ls='gls --color=auto'
alias l='ls'
alias ll='ls -l'
alias rm='rm -i'

# git
export PATH="/usr/local/git/bin:$PATH"  # xcodeではなくhomebrewでgitを管理する
alias gs='git status'
alias gl='git log --graph'
alias gio='git checkout'
alias gm='git pull origin master'
alias gma='git pull origin main'
alias ds='hub pull-request -b deploy/staging -m "Deploy Staging"'
alias dp='hub pull-request -b deploy/production -m "Deploy Production"'
alias dm='hub pull-request -b master -e'

# pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
export PATH="$PYENV_ROOT/shims:$PATH"
eval "$(pyenv init -)"

# rails
alias srake='spring rake'