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
リポジトリ直下の `AGENTS.md` は、`~/.codex/AGENTS.md` として保存・復元する。

### yomiyasu

AIが生成した日本語を推敲する [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) を
`.agents/skills/yomiyasu` に収録する。復元後は `$yomiyasu` を指定して利用できる。
共通指示では、日本語の回答・進捗報告・作成する文章に毎回適用する。
通常の回答には推敲した本文だけを返す。設定変更後は、新しい会話から共通指示が読み込まれる。

- バージョン: 1.0.5
- 取り込み元: `1890e67c497bf3b13df853719d7ca9af4ea37710` の `skills/yomiyasu`
- ライセンス: MIT（同梱の `LICENSE` を参照）

更新時は配布元の `skills/yomiyasu` とリポジトリ直下の `LICENSE` を取り込み、
ここに記載したバージョン・リビジョンも更新する。

### codex-consult

別のCodexやDeepSeek Flashに、設計相談・議論・レビューを依頼する。
「deepseekつかって」「ディープシークつかって」「dsつかって」でDeepSeekを選ぶ。
DeepSeekの往復数が未指定なら2往復で進め、指示役Codexが結果を検証してまとめる。

DeepSeekには、Codexが選別・検査した文章だけを同梱のAPI送信スクリプトから渡す。
DeepSeek側には作業ツリーの探索やコマンド実行をさせない。
APIキーは環境変数か端末内の保存ファイルから認証ヘッダーにだけ使用し、リポジトリには含めない。
普段のCodexのモデルや接続設定は変更しない。

**DeepSeekは再学習に利用され得る外部サービスとして扱う。情報漏えいの経路となり、セキュリティホールになり得る。認証情報・秘密情報はモデルへ絶対に送らない。**
送信前・各往復・回答利用時の注意は、スキル同梱の
[注意事項](.codex/skills/codex-consult/references/deepseek-security.md)を参照する。

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
