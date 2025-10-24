# User の prompt

$1

# 指示

- repository のコードを読み、以下の例のようなディレクトリ構造のドキュメントをかけ
- ドキュメントをアウトプットする際、一切の曖昧さは残してはならない
- そのために足りない情報は user と質疑を行うことで解消せよ
- 質疑の際、数が多くなると引用して書くのが携帯だと大変なので、質問は一覧化したうえで、回答は選択肢を提示し、入力しやすくせよ

````md
# ディレクトリ構造の規約の例

# 実装規約（DIP ベース・Web アプリ共通）

## 0. 原則

1. 依存は内向き（Domain ← Usecase ← Adapters）。逆流禁止。
2. 契約はコードで表現（インターフェース/型/スキーマ/テスト）。
3. 単一責務。ファイル冒頭に「責務: …」コメントを必須。
4. 例外は境界で正規化。HTTP/DB の都合を内側に持ち込まない。
5. 共有は語彙のみ。ロジック共有はしない。

---

## 1. フォルダ構成と責務コメント

```md
.
├── backend/
│ └── core/
│ ├── domain/ # ビジネスルールの中心。不変条件と概念モデルを定義。
│ │ ├── entities/ # エンティティ。状態遷移と整合性を保持。
│ │ ├── values/ # 値オブジェクト。不変条件を担保。
│ │ ├── services/ # 複数エンティティ横断の純粋ロジック。
│ │ └── interfaces/ # 抽象契約（Repository / Gateway 等）。
│ ├── usecase/ # アプリ操作の編成。権限・Tx・エラー正規化を担当。
│ ├── adapters/ # DB・外部 API など外界アクセスの具象実装。
│ └── resolvers/ # DI 配線のみ（ロジック禁止）。
│
├── frontend/
│ └── core/
│ ├── domain/ # 表示・入力中心の軽量型群。
│ │ ├── values/ # 表示やフォーマット用の値。
│ │ ├── entities/ # 画面で扱うデータ形状の型。
│ │ └── interfaces/ # Query / Mutation 契約。
│ ├── usecase/ # ViewModel・状態管理・楽観更新。
│ ├── adapters/ # fetch・cache・ストレージ等の具象。
│ └── resolvers/ # DI 配線。
│
└── shared/
└── domain/ # 共通語彙のみ（列挙・軽いバリデーション）。
└── values/
```
````

---

## 2. 何をどこに書くか早見表（抽象版）

| 種別                           | 置き場                          | 責務の定義                                                       | 境界での扱い                                              |
| ------------------------------ | ------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------- |
| 値オブジェクト（Value）        | backend/core/domain/values      | 不変条件を持つ小概念。生成時に妥当性確定。値で等価。             | DTO 変換はマッパー経由。UI フォーマットはフロントへ委譲。 |
| エンティティ（Entity）         | backend/core/domain/entities    | 識別子を持つ概念。状態遷移と整合性を内包。                       | 再構築はリポジトリ/ファクトリ。永続化都合は漏らさない。   |
| ドメインサービス               | backend/core/domain/services    | 単一エンティティに閉じない純粋ロジック。                         | 外部 I/O なし。ユースケースから呼ぶ。                     |
| ドメイン用インターフェース     | backend/core/domain/interfaces  | 永続化・外部連携の抽象契約。                                     | 具象はアダプタ。ユースケースの唯一の依存先。              |
| ユースケース（アプリサービス） | backend/core/usecase            | 1 操作の業務フロー。権限/Tx/エラー正規化。                       | 入出力は DTO/Result。時刻/ID/Tx は注入。                  |
| インフラアダプタ               | backend/core/adapters           | DB/外部 API/メッセージングの具象。観測・リトライ・タイムアウト。 | 例外はインフラ系にラップ。マッピングはここで完結。        |
| 依存解決（DI）                 | backend/core/resolvers          | 具象選択と配線のみ。                                             | 環境差分はここで吸収。                                    |
| UI 値層（View Value）          | frontend/core/domain/values     | 表示・入力の軽量型、フォーマット、単位変換。                     | ビジネス判断は載せない。                                  |
| UI エンティティ型              | frontend/core/domain/entities   | 画面で扱うデータ形状の型定義。                                   | API DTO から最小マッピング。                              |
| UI サービス契約                | frontend/core/domain/interfaces | 取得/更新抽象（Query/Mutation）。                                | 具象はアダプタ差し替え。                                  |
| UI ユースケース/VM             | frontend/core/usecase           | 画面操作フロー、状態管理、楽観更新、エラー処理。                 | 失敗時ロールバック必須。                                  |
| UI アダプタ                    | frontend/core/adapters          | HTTP/キャッシュ/ストレージ具象。                                 | デコレータで戦略付与。                                    |
| UI 依存解決                    | frontend/core/resolvers         | VM と実装の組み立て。                                            | 環境/フラグ切替。                                         |
| 共有語彙                       | shared/domain/values            | 列挙・プリミティブ型・軽バリデーション。                         | ルール/状態は入れない。                                   |

---

## 3. 命名・ファイル規約

- ファイル名: クラスは `PascalCase`、関数群は `camelCase`。
- 接尾辞: `Repository`, `Gateway`, `Service`(domain), `ViewModel`(FE), `Mapper`, `Dto`。
- `index.ts` 再エクスポートは使わない。
- すべてのファイル先頭に「責務: …」一行。

```

```
