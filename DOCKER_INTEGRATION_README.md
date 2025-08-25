# Docker 統合環境での実行

このプロジェクトは、クライアントとサーバーの両方のアプリケーションを 1 つの EC2 インスタンスで動作させるための統合 Docker 環境を提供します。

## 前提条件

- Docker
- Docker Compose
- EC2 インスタンス（推奨: t3.medium 以上）

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   (Port 80)     │◄──►│   (Port 8000)   │
│   React App     │    │   FastAPI       │
└─────────────────┘    └─────────────────┘
```

## クイックスタート

### 1. 環境変数の設定

```bash
# 環境変数ファイルを作成
cp .env.example .env

# .envファイルを編集して本番環境用の設定を行ってください
# 特に以下の項目は必ず変更してください：
# - SECRET_KEY: 強力なランダム文字列
# - POSTGRES_PASSWORD: 強力なデータベースパスワード
# - REDIS_PASSWORD: 強力なRedisパスワード
```

### 2. 全サービスを起動

```bash
# 本番環境で全サービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### 3. 開発環境での起動（オプション）

```bash
# 開発環境も含めて起動
docker-compose --profile dev up -d

# 開発サーバーは http://localhost:5173 でアクセス可能
```

## サービス構成

### フロントエンド (Frontend)

- **ポート**: 80
- **URL**: http://localhost
- **機能**: React + TypeScript + Vite アプリケーション
- **特徴**: 本番ビルド、Nginx 配信

### バックエンド (Backend)

- **ポート**: 8000
- **URL**: http://localhost:8000
- **機能**: FastAPI + Python
- **特徴**: AI 動画転写、API 提供

## 環境変数

### 必須設定

```bash
# セキュリティ
SECRET_KEY=your-super-secret-key-here
```

### 推奨設定

```bash
# ログレベル
LOG_LEVEL=INFO

# ファイルサイズ制限
MAX_FILE_SIZE=100MB

# CORS設定
ALLOWED_ORIGINS=http://localhost,http://localhost:80
```

## ネットワーク設定

### 内部ネットワーク

- **サブネット**: 172.20.0.0/16
- **サービス間通信**: 内部 IP アドレス
- **外部アクセス**: ポート 80, 8000

### セキュリティグループ設定（EC2）

```bash
# インバウンドルール
HTTP (80)     : 0.0.0.0/0
HTTPS (443)   : 0.0.0.0/0  # SSL証明書使用時
SSH (22)      : あなたのIPアドレス
Custom (8000) : 0.0.0.0/0  # API直接アクセス時
```

## データの永続化

### ボリュームマウント

```yaml
volumes:
  - ./server/data:/app/data # 動画・音声ファイル
  - ./server/uploads:/app/uploads # アップロード一時保存
```

### バックアップ

```bash
# ファイルのバックアップ
tar -czf data-backup.tar.gz server/data server/uploads
```

## パフォーマンス最適化

### リソース制限

```yaml
# docker-compose.ymlに追加
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
        reservations:
          memory: 1G
          cpus: "0.5"
```

### スケーリング

```bash
# バックエンドをスケールアップ
docker-compose up -d --scale backend=3

# フロントエンドをスケールアップ
docker-compose up -d --scale frontend=2
```

## 監視とログ

### ヘルスチェック

```bash
# 全サービスのヘルスステータス確認
docker-compose ps

# 特定サービスのログ確認
docker-compose logs backend
docker-compose logs frontend
```

### メトリクス

```bash
# リソース使用量確認
docker stats

# コンテナ詳細情報
docker inspect video-transcriber-backend
```

## トラブルシューティング

### よくある問題

#### 1. ポートの競合

```bash
# 使用中のポートを確認
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000

# 競合するプロセスを停止
sudo systemctl stop nginx  # 例
```

#### 2. 権限の問題

```bash
# データディレクトリの権限を修正
sudo chown -R $USER:$USER ./server/data ./server/uploads
sudo chmod -R 755 ./server/data ./server/uploads
```

#### 3. メモリ不足

```bash
# スワップファイルの作成
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### ログの確認

```bash
# リアルタイムログ
docker-compose logs -f --tail=100

# エラーログのみ
docker-compose logs --tail=100 | grep ERROR
```

## 本番環境での運用

### SSL/TLS 証明書

```bash
# Let's Encrypt証明書の取得
sudo certbot certonly --standalone -d yourdomain.com

# nginx-proxyプロファイルでリバースプロキシを使用
docker-compose --profile proxy up -d
```

### 自動更新

```bash
# システムパッケージの自動更新
sudo crontab -e

# 毎週日曜日の2時に更新
0 2 * * 0 /usr/bin/apt-get update && /usr/bin/apt-get upgrade -y
```

### バックアップ自動化

```bash
# 日次バックアップスクリプト
#!/bin/bash
DATE=$(date +%Y%m%d)
docker exec video-transcriber-postgres pg_dump -U postgres video_transcriber_ai > backup_$DATE.sql
tar -czf data-backup_$DATE.tar.gz server/data server/uploads
```

## 開発環境での使用

### ホットリロード

```bash
# 開発プロファイルで起動
docker-compose --profile dev up -d

# フロントエンド開発サーバー
# http://localhost:5173 でアクセス
```

### デバッグ

```bash
# バックエンドのデバッグモード
docker-compose run --service-ports backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## クリーンアップ

### 完全なクリーンアップ

```bash
# 全サービスを停止・削除
docker-compose down

# ボリュームも削除
docker-compose down -v

# イメージも削除
docker-compose down --rmi all

# 未使用リソースのクリーンアップ
docker system prune -a --volumes
```

### 部分的なクリーンアップ

```bash
# 特定サービスのみ停止
docker-compose stop backend

# 特定サービスのみ再起動
docker-compose restart backend
```

## サポート

問題が発生した場合は、以下の情報を確認してください：

1. Docker Compose のログ
2. 各サービスのヘルスステータス
3. システムリソース使用量
4. ネットワーク設定
5. 環境変数の設定

詳細なトラブルシューティングについては、各サービスの個別 README も参照してください。
