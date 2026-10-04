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

## Agent Skills

`.codex/skills` と `.agents/skills` は、上記のスクリプトで保存・復元する。
`.agents` は `skills` のみを同期し、端末固有のロックファイルは含めない。

### yomiyasu

AIが生成した日本語を推敲する [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) を
`.agents/skills/yomiyasu` に収録する。復元後は `$yomiyasu` を指定して利用できる。

- バージョン: 1.0.5
- 取り込み元: `1890e67c497bf3b13df853719d7ca9af4ea37710` の `skills/yomiyasu`
- ライセンス: MIT（同梱の `LICENSE` を参照）

更新時は配布元の `skills/yomiyasu` とリポジトリ直下の `LICENSE` を取り込み、
ここに記載したバージョン・リビジョンも更新する。

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
