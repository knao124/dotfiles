# 環境変数
export LANG=ja_JP.UTF-8
export KCODE=u           # KCODEにUTF-8を設定

## 色を使用出来るようにする
autoload -Uz colors
colors

## 補完機能を有効にする
autoload -Uz compinit
compinit

## タブ補完時に大文字小文字を区別しない
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

## 日本語ファイル名を表示可能にする
setopt print_eight_bit

## ヒストリの設定
HISTFILE=~/.zsh_history
HISTSIZE=1000000
SAVEHIST=1000000

## PROMPT
# vcs_infoロード    
autoload -Uz vcs_info    

# PROMPT変数内で変数参照する    
setopt prompt_subst    

# vcsの表示    
zstyle ':vcs_info:*' enable git svn hg bzr
zstyle ':vcs_info:*' check-for-changes true
zstyle ':vcs_info:*' stagedstr "+"
zstyle ':vcs_info:*' unstagedstr "*"
zstyle ':vcs_info:*' formats '(%b%c%u)'    
zstyle ':vcs_info:*' actionformats '(%b(%a)%c%u)'    

# プロンプト表示直前にvcs_info呼び出し    
precmd () {
    psvar=()
    LANG=en_US.UTF-8 vcs_info
    [[ -n "$vcs_info_msg_0_" ]] && psvar[1]="$vcs_info_msg_0_"
}    
#add-zsh-hook precmd _update_vcs_info_msg
PROMPT="%{${fg[green]}%}%n%{${reset_color}%}@%F{blue}localhost%f:%1(v|%F{red}%1v%f|) $ "
RPROMPT='[%F{green}%d%f]'

# nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
nvm use default

# brew info tcl-tk. for python : https://qiita.com/saki-engineering/items/92b7ec12ed07338929a3
export PATH="/usr/local/opt/tcl-tk/bin:$PATH"
export LDFLAGS="-L/usr/local/opt/tcl-tk/lib"
export CPPFLAGS="-I/usr/local/opt/tcl-tk/include"
export PKG_CONFIG_PATH="/usr/local/opt/tcl-tk/lib/pkgconfig"

export PYTHONPATH="/Users/knao124/dev/trade/rudolph-cq/src:$PYTHONPATH"

# zshrc
export ES_GPU_INSTANCE_ID=i-0011f31c68b715898
alias esstart='aws ec2 start-instances --instance-ids $ES_GPU_INSTANCE_ID'
alias esip='aws ec2 describe-instances --query "Reservations[0].Instances[0].{PublicIp:PublicIpAddress}" --instance-ids $ES_GPU_INSTANCE_ID'
alias esstop='aws ec2 stop-instances --instance-ids $ES_GPU_INSTANCE_ID'
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/knao124/dev/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/knao124/dev/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/knao124/dev/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/knao124/dev/google-cloud-sdk/completion.zsh.inc'; fi

# Poetryのpath
export PATH="/Users/knao124/.local/bin:$PATH"

# zshのcompletionとかを動かすためのmoduleが格納されているpathを読み込む
fpath+=~/.zfunc
autoload -Uz compinit && compinit

# JAVA_HOME
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home


# . /opt/homebrew/opt/asdf/libexec/asdf.sh
# . ~/.asdf/plugins/golang/set-env.zsh

# go asdf
# export GOPATH=$(go env GOPATH)
# export PATH=$PATH:$GOPATH/bin

# go spc(supreme systemのcli)
# export PATH=$PATH:/Users/knao124/dev/supreme/spcutils-go

# liquidabase
# https://docs.liquibase.com/workflows/liquibase-community/homebrew-installation-for-macos.html
export LIQUIBASE_HOME=$(brew --prefix)/opt/liquibase/libexec


# phpの設定 2024-03-21 -> 2025-07-31 final fixed v3
# https://qiita.com/gyu_outputs/items/60b75e1acc98ca03c092
export PATH="/opt/homebrew/opt/php@8.2/bin:$PATH"
export PATH="/opt/homebrew/opt/php@8.2/sbin:$PATH"
# homebrewになんかいわれた 2024/05/29
export LIQUIBASE_HOME=/opt/homebrew/opt/liquibase/libexec 

# Flutterの設定
export PATH="/Users/knao124/dev/flutter/bin:$PATH"

ssh-add ~/.ssh/keys/id_rsa_github

## [Completion]
## Completion scripts setup. Remove the following line to uninstall
[[ -f /Users/knao124/.dart-cli-completion/zsh-config.zsh ]] && . /Users/knao124/.dart-cli-completion/zsh-config.zsh || true
## [/Completion]

# sqlite
export PATH="/opt/homebrew/opt/sqlite/bin:$PATH"

source $HOME/.zsh/alias.zsh