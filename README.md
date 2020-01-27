# timetree-events-to-slack

TimeTree で参加している予定を Slack に通知します。通知する時間より後に予定されている予定と、終日予定が通知されます。

## 前提

- [TimeTree API を利用しています](https://developers.timetreeapp.com/ja/docs/api)
- GCP を利用しています。

## 準備

### ソフトウェアインストール

- [Serverless framework](https://github.com/serverless/serverless#quick-start) をインストールしてください。

### TimeTree パーソナルアクセストークンの発行

- [API ドキュメント](https://developers.timetreeapp.com/ja/docs/api) の パーソナルアクセストークンの発行 からトークンを発行してください。

### GCP

- [サービスアカウントを発行して Key を作成してください。](https://serverless.com/framework/docs/providers/google/guide/credentials/)

### 環境変数

- GOOGLE_CREDENTIALS
  - GCP で発行したキーファイルの場所を設定してください。
  - 例） ~/.gcloud/keyfile.json
- PROJECT_ID
  - GCP のプロジェクト ID です。

### Cloud Datastore

- 種類

  - User

- エンティティ
  - id
    - Slack ユーザーを設定してください
  - プロパティ
    - | name              | type   | value                                                                         |
      | :---------------- | :----- | :---------------------------------------------------------------------------- |
      | days              | 整数   | 1 - 7                                                                         |
      | slack_channel     | 文字列 | チャンネル名 (@miu とか)                                                      |
      | slack_webhook_url | 文字列 | Slack で発行した Webhook URL                                                  |
      | time_zone         | 文字列 | Asia/Tokyo                                                                    |
      | timetree_token    | 文字列 | [TimeTree](https://timetreeapp.com/personal_access_tokens) で発行したトークン |

### トリガー

- [Cloud Pub/Sub](https://cloud.google.com/pubsub/?hl=ja) を利用するようになっています。
- アプリケーションをデプロイする前に作成しておく必要があります。
  - terraform ディレクトリにサンプルがありますのでよかったら見てみてください。

## デプロイ

- `sls deploy`

## スケジュール実行

- [Cloud Scheduler](https://cloud.google.com/scheduler/?hl=ja) サンプルが Terraform ディレクトリにありますのでよかったら見てみてください。
