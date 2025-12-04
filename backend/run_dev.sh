#!/bin/bash
# 开发模式启动脚本

set -e

cd "$(dirname "$0")"

echo "=== Telegram 115 Bot Backend - Dev Server ==="
echo ""

# 检查依赖
echo "检查 Python 依赖..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "错误: fastapi 未安装"
    echo "请运行: pip install -r requirements.txt"
    exit 1
}

echo "依赖检查完成 ✓"
echo ""

# 创建数据目录
mkdir -p ../data
echo "数据目录就绪 ✓"
echo ""

# 启动服务
echo "启动 FastAPI 服务器..."
echo "访问地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""

python3 main.py
