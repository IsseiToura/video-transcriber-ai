# クライアント Docker 環境での実行

このプロジェクトは Docker を使用して簡単に実行できます。

## 前提条件

- Docker
- Docker Compose

## クイックスタート

### 1. 開発環境での起動

```bash
# 開発サーバーを起動（ホットリロード対応）
docker-compose up client-dev

# バックグラウンドで起動
docker-compose up -d client-dev
```

開発サーバーは http://localhost:5173 でアクセスできます。

### 2. 本番環境での起動

```bash
# 本番ビルドを起動
docker-compose up client-prod

# バックグラウンドで起動
docker-compose up -d client-prod
```

本番アプリケーションは http://localhost:80 でアクセスできます。

## 個別の Docker 実行

### 開発環境

```bash
# 開発用イメージをビルド
docker build --target development -t video-transcriber-ai-client:dev .

# 開発サーバーを実行
docker run -p 5173:5173 \
  -v $(pwd):/app \
  -v /app/node_modules \
  video-transcriber-ai-client:dev
```

### 本番環境

```bash
# 本番用イメージをビルド
docker build --target production -t video-transcriber-ai-client:prod .

# 本番サーバーを実行
docker run -p 80:80 video-transcriber-ai-client:prod
```

## ビルドプロセス

### マルチステージビルド

1. **Builder Stage**: Node.js 環境でアプリケーションをビルド
2. **Production Stage**: Nginx でビルドされたファイルを配信
3. **Development Stage**: 開発サーバーでホットリロード対応

### ビルドコマンド

```bash
# 全ステージをビルド
docker build .

# 特定のステージのみビルド
docker build --target development .
docker build --target production .
```

## 環境変数

### 開発環境

- `NODE_ENV=development`
- ポート: 5173
- ホットリロード: 有効

### 本番環境

- ポート: 80
- Nginx 配信
- 静的ファイル最適化

## バックエンドとの連携

### API プロキシ

本番環境では、nginx.conf で API リクエストをバックエンドにプロキシします：

```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;
    # ... その他の設定
}
```

### 開発環境

開発環境では、Vite の設定で API プロキシが有効です：

```typescript
// vite.config.ts
proxy: {
  "/api": {
    target: "http://localhost:8000",
    changeOrigin: true,
    secure: false,
  },
}
```

## データの永続化

- ソースコード: ボリュームマウント（開発環境）
- ビルド成果物: コンテナ内（本番環境）

## トラブルシューティング

### ポートの競合

ポート 5173 が既に使用されている場合：

```bash
# 別のポートで実行
docker run -p 5174:5173 video-transcriber-ai-client:dev
```

### 権限の問題

```bash
# ディレクトリの権限を修正
sudo chown -R $USER:$USER .
```

### ログの確認

```bash
# 開発環境のログ
docker-compose logs client-dev

# 本番環境のログ
docker-compose logs client-prod
```

### 依存関係の問題

```bash
# node_modulesを再構築
docker-compose down
docker-compose up --build client-dev
```

## パフォーマンス最適化

### 開発環境

- ソースマップ有効
- ホットリロード対応
- ボリュームマウントで高速なファイルアクセス

### 本番環境

- Gzip 圧縮
- 静的ファイルキャッシュ
- セキュリティヘッダー
- 最適化されたビルド

## セキュリティ

- 非 root ユーザーでの実行
- セキュリティヘッダーの設定
- 必要最小限の依存関係

## クリーンアップ

```bash
# コンテナを停止・削除
docker-compose down

# イメージも削除
docker-compose down --rmi all

# ボリュームも削除
docker-compose down -v
```

## カスタマイズ

### nginx 設定の変更

`nginx.conf`を編集して、必要に応じて設定をカスタマイズできます。

### ビルド設定の変更

`vite.config.ts`や`tsconfig.json`を編集して、ビルド設定をカスタマイズできます。

### 環境変数の追加

必要に応じて、Dockerfile や docker-compose.yml に環境変数を追加できます。
