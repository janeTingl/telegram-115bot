#!/bin/bash
set -e
CONFIG_DIR="/app/data"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
echo "🚀 启动 Telegram-115Bot..."
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📁 生成默认配置文件..."
    mkdir -p $CONFIG_DIR
    cat > $CONFIG_FILE << EOF
bot_token: ""
allowed_user: ""
115_app_id: ""
115_user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
web_username: "root"
web_password: "root"
http_proxy: ""
https_proxy: ""
no_proxy: "localhost,127.0.0.1"
EOF
    echo "✅ 配置文件已生成"
fi
if [ -n "$HTTP_PROXY" ]; then
    echo "🔌 设置代理: $HTTP_PROXY"
    export http_proxy="$HTTP_PROXY"; export https_proxy="$HTTPS_PROXY"; export no_proxy="$NO_PROXY"
fi
echo "🌐 Web管理界面: http://0.0.0.0:12808"
exec python main.py