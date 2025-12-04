#!/bin/bash

# Docker Hub Token 验证脚本
# 用途：在本地验证 Docker Hub Token 是否有效

set -e

echo "🔐 Docker Hub Token 验证工具"
echo "================================"
echo ""

# 配置
DOCKERHUB_USERNAME="janebin"
DOCKERHUB_TOKEN="<YOUR_DOCKER_HUB_TOKEN>"

echo "📋 配置信息："
echo "  Username: $DOCKERHUB_USERNAME"
echo "  Token: ${DOCKERHUB_TOKEN:0:20}...（已隐藏部分）"
echo ""

# 测试登录
echo "🔄 正在测试 Docker Hub 登录..."
echo ""

if echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin > /dev/null 2>&1; then
    echo "✅ 登录成功！"
    echo ""
    echo "Token 有效，可以用于 GitHub Actions Secrets 配置"
    echo ""
    
    # 登出
    docker logout > /dev/null 2>&1
    echo "🔓 已自动登出"
else
    echo "❌ 登录失败！"
    echo ""
    echo "可能的原因："
    echo "1. Token 已过期或被撤销"
    echo "2. Token 权限不足"
    echo "3. Username 不正确"
    echo "4. 网络连接问题"
    echo ""
    echo "请访问 Docker Hub 重新生成 Token："
    echo "https://hub.docker.com/settings/security"
    exit 1
fi

echo ""
echo "================================"
echo "📝 下一步操作："
echo ""
echo "1. 访问 GitHub Secrets 配置页面："
echo "   https://github.com/janebin/telegram-115bot/settings/secrets/actions"
echo ""
echo "2. 添加以下 Secrets："
echo "   - DOCKERHUB_USERNAME = janebin"
echo "   - DOCKERHUB_TOKEN = <YOUR_DOCKER_HUB_TOKEN>"
echo ""
echo "3. 运行 GitHub Actions 工作流"
echo ""
