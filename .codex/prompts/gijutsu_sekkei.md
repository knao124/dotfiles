# 指示

- user と質疑を繰り返し、以下の規約に従った技術設計書をかけ
- ドキュメントをアウトプットする際、一切の曖昧さは残してはならない
- そのために足りない情報は user と質疑を行うことで解消せよ
- 質疑の際、数が多くなると引用して書くのが携帯だと大変なので、一気に聞くのではなく、step by step で回答を引き出せ。同時にきく質問は 3 つまでにし、選択肢を提示せよ
- 最初に、要件定義書の提出を user には求めろ

# 技術設計書の規約

要件定義で「何を作るか（What）」が確定したあと、
技術設計書は「どのように実装するか（How）」を定義する文書である。

- 対象は バックエンド・フロントエンド双方。
- 実装と同精度で「DB・API・処理フロー・ユースケース・UI 構造」を言語化し、設計書のみで同一成果物を再現できる状態を目標とする。

章の順序は以下の通りとする

- 1. DB 設計
- 2. API 設計
- 3. シーケンス図
- 4. Usecase 設計
- 5. UI Component 設計

以降、各章の記述規約を示す。

---

## 1. DB 設計

- 目的は永続化構造の確定とアプリ層制約の明文化である。
- テーブルごとに「目的 → カラム → インデックス → 制約 → 備考」をこの順で記載する。
- 例の再現性を担保するため、表の列名と順序を固定する。

1. 記述順序

   1. 目的（このテーブルが存在する理由を一文で）
   2. カラム定義（表形式）
   3. インデックス（名称とキー、並び順を明記）
   4. 制約（FK/ON DELETE, CHECK/ENUM, UNIQUE など）
   5. 備考（冗長保持の理由、変更不可項目など）

2. 命名規約
   テーブルはスネークケース複数形、外部キーは `_id`。日時は `*_at`、日付は `*_date`。列挙値は CHECK または ENUM で DB 側に明記し、コード側の enum と一致させる。

3. 書式（テンプレート）

```md
### 1) `table_name`（目的の要約）

- 目的: 〜〜を保持する正本データ

**カラム**
| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | uuid | PK | 主キー |
| related_id | uuid | FK → related_table.id ON DELETE RESTRICT | 関連 |
| status | varchar(16) | CHECK IN ('DRAFT','OCR_DONE','SAVED','ERROR') | 状態 |
| created_at | timestamptz | NOT NULL DEFAULT now() | 登録日時 |

**インデックス**

- `idx_table_related_created` ON (related_id, created_at DESC)

**制約**

- 外部キー整合、論理削除の有無、変更禁止項目の扱い

**備考**

- 冗長列の保持理由（監査・表示キャッシュ等）
```

---

## 第 2 章 API 設計

- 目的は外部 I/F の完全定義である。
- 各エンドポイントを「Operation/Method/Path/Params/Request/Response/Errors/副作用」の順に記載する。
- 日時は ISO8601、エラーは RFC7807 で統一する。
- 例と同じ粒度で本文を埋める。

1. 共通ルール

   - 認証要件、ヘッダ、日付形式、エラー形式、`operationId` 付与。
   - `id` は UUID、配列は要素型を明記。

2. 記述順序と書式（テンプレート）

````md
### N) 機能名

- **Operation**: `operationId`
- **Method/Path**: `POST /api/...`
- **Params**
  - Path: `resource_id: uuid`
  - Query: `page?: number`, `ttl?: number`
- **Request Body**

```json
{ ... }
```

- **Response 200|201**

```json
{ ... }
```

- **Errors**

  - 400 validation-error（具体例）
  - 403 forbidden（具体例）
  - 409 conflict（整合不一致の条件）
  - 502 bad-gateway（外部 I/F 失敗）

- **副作用**
  - DB 更新・ステータス遷移・ストレージ書き込み等を明記
````

3. 値域・相関制約
   - ボディの相関条件（例: `end_date >= start_date`）は Errors と副作用の直前で一行明記し、DB 制約との対応を示す。

---

## 第 3 章 シーケンス図

- 目的は処理の時系列と境界の責務分担を固定化すること。
- 処理の流れを擬似コードではなくシーケンス図と箇条書きで明示。
- 各処理は「責務・入出力・副作用」を明確化。
- 1 処理単位＝ 1 トランザクション単位を原則とする。
- 書く順序：
  - 処理の概要
  - トランザクション粒度（rollback 単位）
  - 正常系フロー（時系列）
  - 例外系フロー（validation, conflict, 外部 I/F 失敗など）
  - シーケンス図（mermaid 推奨）

### 作図ルール

- 参加者は実体ごとに固定名を使う（例: `FE` フロント、`API` サーバ、`DB` Repository、`OCR` 外部サービス、`ST` ストレージ）。
- フローは正常系を先に、例外分岐は `alt`/`else` を使用する。

### 書式（テンプレート）

```mermaid
sequenceDiagram
  autonumber
  participant U as ユーザー
  participant FE as フロント
  participant API as APIサーバ
  participant DB as DB
  participant ST as ストレージ
  participant OCR as OCRサービス

  U->>FE: 操作（例：ファイル選択）
  FE->>API: POST /api/... { ... }
  API->>DB: INSERT/UPDATE ...
  alt 条件（例：エラー行あり）
    API->>ST: エラーCSVアップロード
  end
  API-->>FE: 結果JSON（件数/URL）
  FE->>U: 画面更新（例：件数表示）
```

3. 番号対応
   - 見出しに「3-N. 機能名（→ 2 章 API N, → 1 章 テーブル名）」のように参照を付す。

---

## 第 4 章 Usecase 設計

- フロントエンド・バックエンド両方について、 各ユースケースを「クラス名・役割・入力・出力」の 4 項目で定義する。
- 各 Usecase は原則単一責務とし、他の Usecase に依存しない構造を前提とする。
- 命名原則
  - クラス名: PascalCase（例：RunOcrUsecase）
  - 入出力: CamelCase または DTO 形式で表現（例：documentId: UUID）

### 書式（テンプレート）

```md
`RunOcrUsecase`

- 役割: 指定ドキュメントに対して OCR を実行し、結果を DB に保存
- 入力: `{ documentId: UUID }`
- 出力: `{ blocks: OcrBlock[], status: 'OCR_DONE' }`
```

---

## 5. UI Component 設計

- コンポーネント構造を階層図（Tree 形式）＋説明文で記述。
- 各コンポーネントの「責務・状態管理・通信処理」を明記する。
- イベント発火や Usecase 呼び出しのトリガー点を明確化する。
- 画面状態は、Store または Reducer による一貫管理を前提とする。

### 書式（テンプレート）

```md
DocumentPage
├─ Toolbar
├─ ContentSplit
│ ├─ PreviewPane
│ └─ PeopleFormPane
│ └─ PersonCard × N
└─ ErrorSummary
```

- `DocumentPage`: 画面コンテナ。状態管理と Usecase 呼出しの起点。
- `Toolbar`: [ファイル追加][OCR実行][保存] の操作を集約。押下時のイベント名を明記。
- `PreviewPane`: 署名 URL でプレビュー。失効時の再取得処理を明記。
- `PeopleFormPane`: 人ごとのフォーム配列の保持と検証。
- `PersonCard`: 単一人物の 10 項目。OCR 補完は表示属性で区別する。
- `ErrorSummary`: RFC7807 の `errors[]` からフィールド別に集計し、スクロール連携。
