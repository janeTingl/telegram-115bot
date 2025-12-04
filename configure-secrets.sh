#!/bin/bash

# GitHub Secrets 配置辅助脚本
# 用于验证 Docker Hub 凭据并提供配置指导

set -e

echo "=================================================="
echo "  GitHub Secrets 配置辅助工具"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置信息
DOCKERHUB_USERNAME="janebin"
GITHUB_REPO="janeTingl/telegram-115bot"
GITHUB_REPO_URL="https://github.com/${GITHUB_REPO}"

# 从文件读取 Token（不提交到版本控制）
if [ -f ".dockerhub-token" ]; then
    DOCKERHUB_TOKEN=$(cat .dockerhub-token | tr -d '\n\r')
else
    echo -e "${RED}❌ 错误: .dockerhub-token 文件未找到${NC}"
    echo "请在项目根目录创建 .dockerhub-token 文件并将 Docker Hub Token 写入"
    exit 1
fi

echo -e "${BLUE}📋 配置信息${NC}"
echo "  仓库: ${GITHUB_REPO}"
echo "  Docker Hub 用户: ${DOCKERHUB_USERNAME}"
echo ""

# 步骤 1: 验证 Docker Hub 凭据
echo -e "${BLUE}🔍 步骤 1/4: 验证 Docker Hub 凭据${NC}"
echo "正在测试 Docker Hub 登录..."

# 尝试登录 Docker Hub
if echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Hub 凭据有效${NC}"
    docker logout > /dev/null 2>&1
else
    echo -e "${RED}❌ Docker Hub 凭据无效${NC}"
    echo "请检查用户名和 Token 是否正确"
    exit 1
fi
echo ""

# 步骤 2: 检查 GitHub CLI
echo -e "${BLUE}🔧 步骤 2/4: 检查 GitHub CLI${NC}"
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✅ GitHub CLI 已安装${NC}"
    
    # 检查是否已认证
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}✅ GitHub CLI 已认证${NC}"
        
        # 尝试设置 Secrets
        echo ""
        echo -e "${BLUE}🚀 步骤 3/4: 尝试配置 GitHub Secrets${NC}"
        echo "尝试设置 DOCKERHUB_USERNAME..."
        
        if gh secret set DOCKERHUB_USERNAME --body "${DOCKERHUB_USERNAME}" --repo "${GITHUB_REPO}" 2>/dev/null; then
            echo -e "${GREEN}✅ DOCKERHUB_USERNAME 设置成功${NC}"
        else
            echo -e "${YELLOW}⚠️  需要手动配置（权限不足）${NC}"
        fi
        
        echo "尝试设置 DOCKERHUB_TOKEN..."
        if gh secret set DOCKERHUB_TOKEN --body "${DOCKERHUB_TOKEN}" --repo "${GITHUB_REPO}" 2>/dev/null; then
            echo -e "${GREEN}✅ DOCKERHUB_TOKEN 设置成功${NC}"
        else
            echo -e "${YELLOW}⚠️  需要手动配置（权限不足）${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  GitHub CLI 未认证${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GitHub CLI 未安装${NC}"
fi
echo ""

# 步骤 4: 提供手动配置指南
echo -e "${BLUE}📖 步骤 4/4: 手动配置指南${NC}"
echo ""
echo -e "${YELLOW}如果自动配置失败，请手动配置 GitHub Secrets：${NC}"
echo ""
echo "1️⃣  访问 Secrets 设置页面："
echo "   ${GITHUB_REPO_URL}/settings/secrets/actions"
echo ""
echo "2️⃣  添加第一个 Secret："
echo "   Name:  DOCKERHUB_USERNAME"
echo "   Value: ${DOCKERHUB_USERNAME}"
echo ""
echo "3️⃣  添加第二个 Secret："
echo "   Name:  DOCKERHUB_TOKEN"
echo "   Value: [从 .dockerhub-token 文件获取]"
echo "   提示: 运行 'cat .dockerhub-token' 查看完整 Token"
echo ""
echo "4️⃣  触发工作流："
echo "   访问: ${GITHUB_REPO_URL}/actions"
echo "   选择: Build and Push Docker Image to Docker Hub"
echo "   点击: Run workflow"
echo ""
echo -e "${GREEN}📚 详细说明文档：${NC}"
echo "   - SECRETS_CONFIGURATION_REQUIRED.md (完整配置指南)"
echo "   - GITHUB_SECRETS_SETUP.md (详细步骤说明)"
echo ""

# 显示验证步骤
echo -e "${BLUE}✅ 配置完成后验证：${NC}"
echo ""
echo "1. GitHub Actions 状态："
echo "   ${GITHUB_REPO_URL}/actions"
echo ""
echo "2. Docker Hub 镜像："
echo "   https://hub.docker.com/r/${DOCKERHUB_USERNAME}/telegram-115bot"
echo ""
echo "3. 本地拉取测试："
echo "   docker pull ${DOCKERHUB_USERNAME}/telegram-115bot:latest"
echo ""

echo "=================================================="
echo -e "${GREEN}  配置工具运行完成${NC}"
echo "=================================================="
