# サ飯パスポート

## 概要

「サ飯パスポート」は、サウナ後の食事（サ飯）選びをサポートするStreamlitアプリケーションです。
お気に入りのサウナ施設を選択すると、その施設に関連付けられた飲食店のメニューから、おすすめの「サ飯」の組み合わせをランダムに提案する「サ飯ガチャ」機能を提供します。

![ロゴ](sameshi_logo.png)

## 機能

*   **サウナ施設の選択:** Google スプレッドシートに登録されたサウナ施設リストから選択できます。
*   **サ飯ガチャ:** 選択されたサウナ施設に関連する飲食店のメニュー（メイン1品、ドリンク2品）をランダムに提案します。
*   **メニュー詳細表示:** 提案された各メニューの料金、説明、関連タグを表示します。
*   **周辺飲食店検索 (内部機能):** Google Maps API を利用して、サウナ施設周辺の特定のキーワード（ラーメン、牛丼など）に合致する評価の高い飲食店を検索します（現在はUIには直接表示されていません）。
*   **パスポート風UI:** ダークテーマを基調とした、パスポートのようなデザインを採用しています。

## 技術スタック

*   Python
*   Streamlit
*   Pandas
*   gspread (Google Sheets連携)
*   googlemaps (Google Maps Platform連携)
*   Google Cloud Platform (Sheets API, Maps API)

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <リポジトリURL>
cd <リポジトリ名>
```

### 2. 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. Google Cloud Platform (GCP) の設定

1.  **GCPプロジェクトの作成:** Google Cloud Console で新しいプロジェクトを作成または既存のプロジェクトを選択します。
2.  **APIの有効化:**
    *   Google Sheets API
    *   Google Maps Platform (Places API, Geocoding API など、`find_nearby_good_food` 関数で使用する可能性のあるAPI)
3.  **サービスアカウントの作成:**
    *   GCP Console でサービスアカウントを作成します。
    *   必要なロール（例: Sheets APIへのアクセス権限、Maps APIへのアクセス権限）を付与します。
    *   サービスアカウントキー（JSON形式）を作成し、ダウンロードします。

### 4. Google スプレッドシートの準備

1.  **スプレッドシートの作成:** 以下のシート構成でGoogle スプレッドシートを作成します。
    *   `Saunas`: サウナ情報 (id, name, latitude, longitude など)
    *   `Restaurants`: 飲食店情報 (id, sauna_id, name など)
    *   `Menu`: メニュー情報 (id, restaurant_id, name, price, description, category (`main` または `drink`))
    *   `MenuTags`: タグ情報 (id, name)
    *   `MenuTagRelation`: メニューとタグの関連付け情報 (id, menuitemid, tag_id)
2.  **スプレッドシートIDの確認:** スプレッドシートのURLからIDをコピーします (`https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`)。
3.  **サービスアカウントへの共有:** 作成したサービスアカウントのメールアドレスに対して、スプレッドシートの編集権限を付与します。

### 5. 設定ファイルの準備

1.  **`.streamlit/secrets.toml` の作成:**
    *   ダウンロードしたGCPサービスアカウントキー(JSON)の内容を `[gcp_service_account]` セクションにコピーします。
    *   Google Maps APIキーを `[env]` セクションの `GOOGLE_API_KEY` に設定します。
    ```toml
    [gcp_service_account]
    type = "service_account"
    project_id = "YOUR_PROJECT_ID"
    private_key_id = "YOUR_PRIVATE_KEY_ID"
    private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
    client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
    client_id = "YOUR