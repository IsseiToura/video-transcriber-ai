#!/bin/bash

# EC2インスタンスでのDocker環境セットアップスクリプト
# 使用方法: sudo bash ec2-setup.sh

set -e

echo "🚀 EC2インスタンスでのDocker環境セットアップを開始します..."

# システムの更新
echo "📦 システムパッケージを更新中..."
apt-get update
apt-get upgrade -y

# 必要なパッケージのインストール
echo "🔧 必要なパッケージをインストール中..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    unzip \
    htop \
    nginx

# Dockerのインストール
echo "🐳 Dockerをインストール中..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker Composeのインストール
echo "📋 Docker Composeをインストール中..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Dockerサービスの開始と自動起動設定
echo "🔄 Dockerサービスを開始中..."
systemctl start docker
systemctl enable docker

# 現在のユーザーをdockerグループに追加
echo "👤 ユーザーをdockerグループに追加中..."
usermod -aG docker $SUDO_USER

# スワップファイルの作成（メモリ不足対策）
echo "💾 スワップファイルを作成中..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# ファイアウォールの設定
echo "🔥 ファイアウォールを設定中..."
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable

# プロジェクトディレクトリの作成
echo "📁 プロジェクトディレクトリを作成中..."
mkdir -p /opt/video-transcriber-ai
cd /opt/video-transcriber-ai

# 環境変数ファイルの作成
echo "⚙️ 環境変数ファイルを作成中..."
cat > .env << 'EOF'
# Application Configuration
APP_NAME=Video Transcriber AI
APP_VERSION=1.0.0
NODE_ENV=production

# Security
SECRET_KEY=change-this-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Storage
MAX_FILE_SIZE=100MB
UPLOAD_DIR=./server/data

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS Settings
ALLOWED_ORIGINS=http://localhost,http://localhost:80,http://localhost:3000,http://localhost:5173

# Network Configuration
APP_NETWORK_SUBNET=172.20.0.0/16

# Health Check Settings
HEALTH_CHECK_INTERVAL=30s
HEALTH_CHECK_TIMEOUT=10s
HEALTH_CHECK_RETRIES=3
HEALTH_CHECK_START_PERIOD=40s
EOF

# データディレクトリの作成と権限設定
echo "📂 データディレクトリを作成中..."
mkdir -p server/data/videos server/data/transcripts server/uploads
chown -R $SUDO_USER:$SUDO_USER /opt/video-transcriber-ai
chmod -R 755 /opt/video-transcriber-ai

# systemdサービスの作成（自動起動用）
echo "🔄 systemdサービスを作成中..."
cat > /etc/systemd/system/video-transcriber-ai.service << 'EOF'
[Unit]
Description=Video Transcriber AI Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/video-transcriber-ai
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# systemdサービスの有効化
systemctl daemon-reload
systemctl enable video-transcriber-ai.service

# ログローテーションの設定
echo "📝 ログローテーションを設定中..."
cat > /etc/logrotate.d/docker-compose << 'EOF'
/opt/video-transcriber-ai/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

# バックアップスクリプトの作成
echo "💾 バックアップスクリプトを作成中..."
cat > /opt/video-transcriber-ai/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# ファイルのバックアップ
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz -C /opt/video-transcriber-ai server/data server/uploads

# 古いバックアップの削除（30日以上古いもの）
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "バックアップ完了: $DATE"
EOF

chmod +x /opt/video-transcriber-ai/backup.sh

# cronジョブの設定（日次バックアップ）
echo "⏰ cronジョブを設定中..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/video-transcriber-ai/backup.sh >> /var/log/backup.log 2>&1") | crontab -

# 監視スクリプトの作成
echo "👀 監視スクリプトを作成中..."
cat > /opt/video-transcriber-ai/monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/video-transcriber-monitor.log"

# ヘルスチェック
check_service() {
    local service=$1
    local port=$2
    
    if ! nc -z localhost $port 2>/dev/null; then
        echo "$(date): $service (port $port) is down, restarting..." >> $LOG_FILE
        cd /opt/video-transcriber-ai
        docker-compose restart $service
    fi
}

# 各サービスのチェック
check_service "frontend" 80
check_service "backend" 8000

# ディスク使用量チェック
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# メモリ使用量チェック
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "$(date): Memory usage is high: ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x /opt/video-transcriber-ai/monitor.sh

# 監視のcronジョブ設定（5分ごと）
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/video-transcriber-ai/monitor.sh") | crontab -

# セキュリティ設定
echo "🔒 セキュリティ設定を適用中..."
# SSH設定の強化
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# ファイアウォールルールの追加
ufw default deny incoming
ufw default allow outgoing
ufw allow from 127.0.0.1
ufw allow ssh

echo "✅ セットアップが完了しました！"
echo ""
echo "📋 次のステップ:"
echo "1. プロジェクトファイルを /opt/video-transcriber-ai にコピーしてください"
echo "2. .envファイルの設定を本番環境用に変更してください"
echo "3. 以下のコマンドでサービスを起動してください:"
echo "   cd /opt/video-transcriber-ai"
echo "   docker-compose up -d"
echo ""
echo "🔍 ログの確認:"
echo "   docker-compose logs -f"
echo ""
echo "📊 システム監視:"
echo "   docker stats"
echo ""
echo "🔄 自動起動設定済み（systemctl status video-transcriber-ai.service）"
echo "💾 自動バックアップ設定済み（毎日午前2時）"
echo "👀 自動監視設定済み（5分ごと）"
echo ""
echo "⚠️  重要: セキュリティ設定を確認し、必要に応じて調整してください"
