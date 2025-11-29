#!/bin/bash

set -e

CONFIG_DIR="/app/data"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

echo "🚀 启动 Telegram-115Bot..."

# 如果配置文件不存在，生成默认配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📁 生成默认配置文件..."
    mkdir -p $CONFIG_DIR
    
    cat > $CONFIG_FILE << EOF
# Telegram Bot配置
bot_token: "${BOT_TOKEN:-}"
allowed_user: "${ALLOWED_USER:-}"

# 115网盘配置
115_app_id: "${APP_115_APP_ID:-}"
115_user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Web管理界面配置
web:
  host: "0.0.0.0"
  port: 12808
  username: "${WEB_USERNAME:-admin}"
  password: "${WEB_PASSWORD:-admin123}"

# 代理配置
http_proxy: "${HTTP_PROXY:-}"
https_proxy: "${HTTPS_PROXY:-}"
no_proxy: "${NO_PROXY:-localhost,127.0.0.1,192.168.0.0/16}"

# 下载配置
download:
  max_retries: 3
  retry_interval: 300
  timeout: 1800

# 日志配置
log:
  level: "INFO"
  file: "/app/data/logs/bot.log"
  max_size: 10
  backup_count: 5
EOF
    echo "✅ 配置文件已生成: $CONFIG_FILE"
    echo "📝 请通过Web界面(端口12808)配置必要参数"
fi

# 设置代理环境变量（如果配置了代理）
if [ -n "$HTTP_PROXY" ]; then
    echo "🔌 设置代理: $HTTP_PROXY"
    export http_proxy="$HTTP_PROXY"
    export https_proxy="$HTTPS_PROXY"
    export no_proxy="$NO_PROXY"
fi

# 启动应用
echo "🌐 Web管理界面: http://0.0.0.0:12808"
exec python main.py#!/bin/bash

set -e

CONFIG_DIR="/app/data"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

echo "🚀 启动 Telegram-115Bot..."

# 如果配置文件不存在，生成默认配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📁 生成默认配置文件..."
    mkdir -p $CONFIG_DIR
    
    cat > $CONFIG_FILE << EOF
# Telegram Bot配置
bot_token: "${BOT_TOKEN:-}"
allowed_user: "${ALLOWED_USER:-}"

# 115网盘配置
115_app_id: "${APP_115_APP_ID:-}"
115_user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Web管理界面配置
web:
  host: "0.0.0.0"
  port: 12808
  username: "${WEB_USERNAME:-admin}"
  password: "${WEB_PASSWORD:-admin123}"

# 代理配置
http_proxy: "${HTTP_PROXY:-}"
https_proxy: "${HTTPS_PROXY:-}"
no_proxy: "${NO_PROXY:-localhost,127.0.0.1,192.168.0.0/16}"

# 下载配置
download:
  max_retries: 3
  retry_interval: 300
  timeout: 1800

# 日志配置
log:
  level: "INFO"
  file: "/app/data/logs/bot.log"
  max_size: 10
  backup_count: 5
EOF
    echo "✅ 配置文件已生成: $CONFIG_FILE"
    echo "📝 请通过Web界面(端口12808)配置必要参数"
fi

# 设置代理环境变量（如果配置了代理）
if [ -n "$HTTP_PROXY" ]; then
    echo "🔌 设置代理: $HTTP_PROXY"
    export http_proxy="$HTTP_PROXY"
    export https_proxy="$HTTPS_PROXY"
    export no_proxy="$NO_PROXY"
fi

# 启动应用
echo "🌐 Web管理界面: http://0.0.0.0:12808"
exec python main.py