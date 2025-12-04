#!/bin/bash

# Telegram 115 Bot - Docker 镜像验证脚本
# 用于验证 Docker Hub 镜像是否成功发布

set -e

DOCKER_USER="janebin"
IMAGE_NAME="telegram-115bot"
FULL_IMAGE="${DOCKER_USER}/${IMAGE_NAME}"

echo "=========================================="
echo "   Telegram 115 Bot - 镜像验证脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

echo "✅ Docker 已安装"
echo ""

# 尝试拉取镜像
echo "📦 正在拉取镜像: ${FULL_IMAGE}:latest"
echo "-------------------------------------------"

if docker pull ${FULL_IMAGE}:latest; then
    echo ""
    echo "✅ 镜像拉取成功！"
    echo ""
else
    echo ""
    echo "❌ 镜像拉取失败"
    echo ""
    echo "可能的原因："
    echo "1. 镜像尚未发布到 Docker Hub"
    echo "2. 网络连接问题"
    echo "3. Docker Hub 仓库权限设置"
    echo ""
    echo "请检查："
    echo "- GitHub Actions 构建是否成功"
    echo "- Docker Hub 仓库: https://hub.docker.com/r/${FULL_IMAGE}"
    echo ""
    exit 1
fi

# 显示镜像信息
echo "📋 镜像详细信息"
echo "-------------------------------------------"
docker images ${FULL_IMAGE}:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

# 获取镜像架构信息
echo "🏗️  支持的架构"
echo "-------------------------------------------"
docker manifest inspect ${FULL_IMAGE}:latest 2>/dev/null | grep -A 2 "architecture" || echo "无法获取架构信息（可能需要 Docker 实验性特性）"
echo ""

# 提供测试运行选项
echo "🚀 测试运行选项"
echo "-------------------------------------------"
echo "1. 快速测试（前台运行，Ctrl+C 退出）："
echo "   docker run --rm -p 12808:12808 ${FULL_IMAGE}:latest"
echo ""
echo "2. 后台运行："
echo "   docker run -d --name telegram-115bot-test -p 12808:12808 ${FULL_IMAGE}:latest"
echo ""
echo "3. 使用 Docker Compose："
echo "   docker-compose up -d"
echo ""

# 询问是否启动测试容器
read -p "是否现在启动测试容器？(y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 启动测试容器..."
    echo "-------------------------------------------"
    
    # 检查是否已有同名容器
    if docker ps -a --format '{{.Names}}' | grep -q "^telegram-115bot-test$"; then
        echo "⚠️  发现已存在的测试容器，正在清理..."
        docker stop telegram-115bot-test 2>/dev/null || true
        docker rm telegram-115bot-test 2>/dev/null || true
    fi
    
    # 启动容器
    docker run -d \
        --name telegram-115bot-test \
        -p 12808:12808 \
        -v $(pwd)/backend/data:/app/data \
        -v $(pwd)/backend/uploads:/app/uploads \
        ${FULL_IMAGE}:latest
    
    echo ""
    echo "✅ 容器已启动！"
    echo ""
    echo "📊 容器状态："
    docker ps --filter name=telegram-115bot-test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "🌐 访问地址: http://localhost:12808"
    echo "👤 默认账号: admin / admin"
    echo ""
    echo "📝 查看日志: docker logs -f telegram-115bot-test"
    echo "🛑 停止容器: docker stop telegram-115bot-test"
    echo "🗑️  删除容器: docker rm telegram-115bot-test"
    echo ""
    
    # 等待几秒钟让容器启动
    echo "⏳ 等待容器启动..."
    sleep 5
    
    # 检查容器是否正常运行
    if docker ps --filter name=telegram-115bot-test --filter status=running | grep -q telegram-115bot-test; then
        echo "✅ 容器运行正常！"
        
        # 尝试健康检查
        if command -v curl &> /dev/null; then
            echo ""
            echo "🏥 执行健康检查..."
            if curl -s -o /dev/null -w "%{http_code}" http://localhost:12808 | grep -q "200\|302"; then
                echo "✅ 服务响应正常！"
            else
                echo "⚠️  服务可能还在启动中，请稍后访问"
            fi
        fi
    else
        echo "❌ 容器启动失败，请查看日志："
        echo "   docker logs telegram-115bot-test"
    fi
else
    echo ""
    echo "✅ 验证完成！镜像已就绪。"
fi

echo ""
echo "=========================================="
echo "   验证完成"
echo "=========================================="
