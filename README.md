# dotfiles

## 使い方

dotfiles を home ディレクトリにコピー

```bash
./.scripts/copy_to_home.sh
```

home ディレクトリの dotfiles をリポジトリに反映

```bash
./.scripts/copy_to_repo.sh
```

Homebrew で管理するパッケージを `Brewfile` に反映

```bash
./.scripts/brew_bundle_dump.sh
```

`Brewfile` に書かれたパッケージを install

```bash
./.scripts/brew_bundle_apply.sh
```

upgrade も含めて反映したい場合

```bash
./.scripts/brew_bundle_apply.sh --upgrade
```

## direnv

`direnv` がインストールされている場合だけ、`.zshrc` から `direnv hook zsh` を読み込む。

```bash
brew install direnv
```

repo ごとに gcloud の configuration を切り替える場合は、対象 repo の `.envrc` に書く。

```bash
export CLOUDSDK_ACTIVE_CONFIG_NAME=<config-name>
export GOOGLE_CLOUD_PROJECT=<project-id>
export GCLOUD_PROJECT=<project-id>
```

`.envrc` を確認したうえで有効化する。

```bash
direnv allow
```
