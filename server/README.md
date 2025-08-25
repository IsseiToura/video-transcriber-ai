# Video Transcriber AI Backend Server

FastAPI ベースのバックエンドサーバーで、動画の文字起こし、要約、AI チャット機能を提供します。

## 機能

- **ユーザー認証**: JWT ベースの認証システム
- **動画管理**: 動画のアップロード、削除、状態管理
- **文字起こし**: 動画の音声を文字に変換
- **AI 要約**: 動画内容の自動要約
- **チャット機能**: 動画内容に関する質問への AI 回答
- **ファイル管理**: 動画ファイルの安全な保存と管理

## 技術スタック

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT + Passlib
- **File Storage**: ローカルファイルシステム
- **Migration**: Alembic
- **Task Queue**: Celery + Redis (将来の拡張用)

## セットアップ

### 前提条件

- Python 3.11+
- PostgreSQL
- Redis (将来の拡張用)

### インストール

1. リポジトリをクローン

```bash
git clone <repository-url>
cd video-transriber-ai/server
```

2. 仮想環境を作成してアクティベート

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

3. 依存関係をインストール

```bash
pip install -r requirements.txt
```

4. 環境変数を設定

```bash
cp env.example .env
# .envファイルを編集して適切な値を設定
```

5. データベースを作成

```bash
createdb video_transcriber_ai
```

6. データベースマイグレーションを実行

```bash
alembic upgrade head
```

### 開発サーバーの起動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

または

```bash
python -m app.main
```

## API ドキュメント

サーバー起動後、以下の URL で API ドキュメントにアクセスできます：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 主要なエンドポイント

### 認証

- `POST /api/v1/auth/register` - ユーザー登録
- `POST /api/v1/auth/login` - ユーザーログイン
- `GET /api/v1/auth/me` - 現在のユーザー情報

### 動画管理

- `GET /api/v1/videos/` - 動画一覧取得
- `GET /api/v1/videos/{video_id}` - 動画詳細取得
- `POST /api/v1/videos/upload` - 動画アップロード
- `DELETE /api/v1/videos/{video_id}` - 動画削除

### チャット機能

- `GET /api/v1/videos/{video_id}/conversations` - 会話履歴取得
- `POST /api/v1/videos/{video_id}/conversations` - 新しい会話作成
- `GET /api/v1/videos/conversations/{conversation_id}` - 会話詳細取得
- `DELETE /api/v1/videos/conversations/{conversation_id}` - 会話削除

## プロジェクト構造

```
server/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── videos.py
│   │           └── conversations.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   ├── video.py
│   │   └── conversation.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── video.py
│   │   ├── conversation.py
│   │   └── auth.py
│   └── main.py
├── alembic/
│   ├── env.py
│   └── script.py.mako
├── requirements.txt
├── pyproject.toml
├── alembic.ini
└── README.md
```

## 開発

### コードフォーマット

```bash
# Blackでコードフォーマット
black .

# isortでインポート順序を整理
isort .

# flake8でリント
flake8 .

# mypyで型チェック
mypy .
```

### テスト

```bash
# テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=app
```

### データベースマイグレーション

```bash
# 新しいマイグレーションを作成
alembic revision --autogenerate -m "Description"

# マイグレーションを適用
alembic upgrade head

# マイグレーションを戻す
alembic downgrade -1
```

## 環境変数

| 変数名                        | 説明                             | デフォルト値                                                     |
| ----------------------------- | -------------------------------- | ---------------------------------------------------------------- |
| `DATABASE_URL`                | データベース接続 URL             | `postgresql://user:password@localhost:5432/video_transcriber_ai` |
| `SECRET_KEY`                  | JWT 署名用の秘密鍵               | `your-secret-key-here`                                           |
| `UPLOAD_DIR`                  | 動画ファイルの保存ディレクトリ   | `./uploads`                                                      |
| `ALLOWED_VIDEO_EXTENSIONS`    | 許可する動画ファイル形式         | `mp4,avi,mov,wmv,flv,webm`                                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | アクセストークンの有効期限（分） | `30`                                                             |

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。貢献する前に、コーディング規約とプルリクエストのガイドラインを確認してください。
