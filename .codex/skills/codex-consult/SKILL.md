---
description: Use for consultation, discussion, critique, or review with another Codex or DeepSeek Flash. Trigger on "deepseekつかって", "ディープシークつかって", "dsつかって", their case/spacing variants and "使って" forms, "DeepSeekにレビューしてもらって", "Codex同士で相談して", "別Codexに聞いて", or requests for multiple review rounds. Call DeepSeek only with inspected, credential-free text through the bundled API sender; keep the main model unchanged. Do not trigger for explanations of DeepSeek, dataset abbreviations, or implementation delegation.
license: MIT
metadata:
    github-path: skills/codex-consult
    github-ref: refs/heads/main
    github-repo: https://github.com/knao124/agent-skills
    github-tree-sha: 7041aa64f5dfcb5be3495e67b668f2adf6bccccc
name: codex-consult
---
# Codex Consult

## 概要

指示役Codexが、別のCodexまたはDeepSeek Flashにセカンドオピニオンを求める。通常のCodexにはCodex CLIを使い、DeepSeekには検査した文章だけを同梱の送信スクリプトから渡す。指示役のモデルと普段の接続設定は変えない。相談役の生出力をそのまま返さず、指示役が検証し、同意・反論・補完・採用判断を統合して報告する。

## DeepSeekを使う前の必読事項

**DeepSeekは再学習に利用され得る外部サービスとして扱う。送信経路はセキュリティホールになり得る。認証情報・秘密情報をモデルへ絶対に送らない。**

DeepSeekを選ぶ場合は、必ず[外部送信と再学習に関する注意](references/deepseek-security.md)を先に読む。呼び出す前、各往復で情報を追加する前、回答を利用する前に確認する。料金を支払うことや、ローカルのターミナルから呼ぶことは、学習利用や情報漏えいを防ぐ根拠にならない。

## 相談先の選択

- 「deepseekつかって」「ディープシークつかって」「dsつかって」、大小文字・空白の違い、「使って」表記、DeepSeekを指定した議論やレビューではDeepSeek Flashを選ぶ。作業中なら、その作業を相談対象として解釈する。対象を特定できない場合だけ確認する。
- DeepSeekは[DeepSeekへの相談](references/deepseek.md)に従い、同梱の `scripts/deepseek_consult.py` だけで呼ぶ。DeepSeekを使うCodex CLI・Harness・サブエージェントに、作業ツリーや認証ファイルを探索させない。
- 「別Codex」「Codex同士」などの従来の依頼では、DeepSeekプロファイルを付けず、通常のCodexを呼ぶ。元の依頼で別のモデルが指定されていれば、その指定を優先する。
- 「DeepSeekとは？」「dsという変数名を変えて」など、外部モデルへの相談を求めていない発言では発動しない。

## 基本ルール

- 1往復 = 選択した相談役を1回呼び、指示役Codexが出力を読んで次の論点を組み立てること。
- ユーザーが往復数を指定している場合は厳密にその回数を実行する。
- DeepSeekへの相談で往復数が未指定なら `2往復` で進める。通常のCodexへの相談では、未指定ならユーザーに確認する。対話できない場合だけ `2往復` をデフォルトにする。
- 最大3往復まで実行する。4往復以上を求められたら、実行前に確認する。
- 相談役Codexに実装やファイル編集をさせない。編集委譲が必要なら `codex-delegate` に切り替える。
- 指定観点は出発点であり制約ではない、と必ず相談役に伝える。
- 相談役の回答を鵜呑みにしない。誤読、探索不足、コマンド失敗、過剰設計を必ず疑う。
- 相談役には、別のエージェントや外部モデルを呼ばず、自分で調査・検討するよう伝える。相談の再帰的な委譲を避ける。

## 実行手順

1. 通常のCodexへの相談では `command -v codex` でCodex CLIの存在を確認する。見つからなければ、その不足を報告して終了する。DeepSeekの場合は専用手順に従う。
2. 相談対象を整理する。
   - 背景、目的、制約、評価観点を短くまとめる。
   - 指示役Codexの仮説を作る。初回プロンプトには必ず含める。
   - repo がある場合は `pwd`、`git status --short --branch`、必要な `AGENTS.md` などを確認し、重要なルールを要約する。
   - git repo 外で相談する場合は、`codex exec` に `--skip-git-repo-check` を付ける。
3. 各往復のプロンプトを一時ファイルに書き出す。通常のCodexには `codex exec` の標準入力で渡す。DeepSeekには、指示役による確認と送信スクリプトの検査を各往復で実施してから、必要最小限の文章だけを送る。認証情報・秘密情報はモデルへ絶対に送らない。
4. 各往復後、相談役の回答を要約し、次の往復に入れる。
5. 指定回数が終わったら統合レポートを返す。

## codex exec の呼び出し

この節は通常のCodexへの相談にだけ適用する。DeepSeekへの相談では[専用の送信手順](references/deepseek.md)を使う。

長いプロンプトの shell quoting 問題を避けるため、prompt file 経由で実行する。

```sh
tmpdir="$(mktemp -d)"
prompt="$tmpdir/codex-consult-prompt.md"
out="$tmpdir/codex-consult-output.md"
# prompt に依頼文を書く
codex exec --ephemeral --cd "$PWD" -s read-only -o "$out" - < "$prompt"
```

git repo 外で実行する場合だけ、同じコマンドに `--skip-git-repo-check` を追加する。

通常のCodexへの相談にGitHub、外部ドキュメント、ネットワーク取得が不可欠で、read-only sandboxで失敗した場合のみ、明示的に編集禁止をプロンプトへ入れたうえで再実行する。DeepSeekにはこの例外を適用しない。

```sh
codex exec --ephemeral --cd "$PWD" -s workspace-write \
  -c sandbox_workspace_write.network_access=true \
  -o "$out" - < "$prompt"
```

## 初回プロンプトの構成

```md
あなたは相談役Codexです。実装やファイル編集は行わず、設計・レビュー・反論に徹してください。

背景:
- ...

相談したいこと:
- ...

制約・既存ルール:
- ...

指示役Codexの仮説:
- ...

依頼:
- 指定観点は出発点であり制約ではありません。
- repo や文脈を自分で探索し、前提の誤り、漏れ抜け、代替案、運用リスクを積極的に指摘してください。
- 指示役Codexの仮説に反論できる点があれば明示してください。
- 実装やファイル編集はしないでください。
```

## 2往復目以降のプロンプト

`codex exec` はステートレスなので、前回の記憶がない前提で全文脈を再投入する。

```md
あなたは相談役Codexです。これは X 往復中の N 往復目です。

元の背景・目的・制約:
- ...

指示役Codexの初期仮説:
- ...

前回までの相談役Codexの主張:
- ...

指示役Codexの検証・反論・補完:
- ...

今回さらに掘る観点:
- ...

依頼:
- 前回回答の自己追認ではなく、前提を疑ってください。
- まだ探索されていない領域、過剰/不足な設計、壊れやすい運用を探してください。
- 実装やファイル編集はしないでください。
```

## 失敗検知と補正

相談役の出力に以下があれば、指示役Codexが自分で確認して補正する。

- `permission denied`、`not found`、`failed`、`取得できなかった`
- `gh`、`git`、`curl`、テスト、依存取得、ファイル参照の失敗
- repo を十分に探索していない推測ベースの断定

補正後の最終報告では、欠落情報、影響を受けた指摘、再評価結果を明示する。

## 最終報告

以下の構成で簡潔に報告する。

- 相談内容: 相談役Codexに何を何往復聞いたか。
- 使用モデル: 通常のCodexかDeepSeek Flashか。DeepSeekの呼び出しはDeepSeek側のAPI課金になること。
- 往復ごとの主要論点: 各往復で新しく分かったこと。
- 指示役Codexの見解: 同意、反論、補完、見落とし。
- 採用方針: どの案を採るべきか、何を避けるべきか。
- 次のアクション: 実装、追加調査、ユーザー確認のいずれが必要か。

相談役の長い生ログは貼らない。必要な場合だけ短く引用し、基本は指示役Codexの言葉で要約する。
