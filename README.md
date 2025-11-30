# Telegram-115Bot

一个基于Docker的Telegram 115网盘管理机器人。

## 快速开始

1. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件填写实际配置
#!/bin/bash
echo "🚀 设置 Telegram-115Bot 开发环境..."

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建项目结构（调用主脚本）
if [ -f "../setup-project.sh" ]; then
    chmod +x ../setup-project.sh
    ../setup-project.sh
else
    echo "❌ setup-project.sh 未找到"
fi

echo "✅ 开发环境设置完成！"
#!/bin/bash

# Telegram-115Bot GitHub 一键初始化脚本
# 自动创建仓库、提交代码、设置 Secrets

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查 Git
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装！"
        exit 1
    fi
    log_success "Git 检查通过"
}

# 初始化 Git 仓库
init_git() {
    log_info "初始化 Git 仓库..."
    
    if [ ! -d ".git" ]; then
        git init
        git branch -M main
        log_success "Git 仓库初始化完成"
    else
        log_info "Git 仓库已存在"
    fi
}

# 创建 .gitignore
create_gitignore() {
    log_info "创建 .gitignore..."
    
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
env.bak/
venv.bak/

# Docker
data/
*.env
.env.local
.env.production

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
tmp/
temp/
