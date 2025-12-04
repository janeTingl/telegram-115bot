# Docker Hub 自动发布配置指南

本文档说明如何配置 GitHub Actions 自动构建和发布 Docker 镜像到 Docker Hub。

## 📋 概述

本项目已配置 GitHub Actions 工作流，可以自动构建多架构（AMD64 和 ARM64）Docker 镜像并发布到 Docker Hub。

### 触发条件

工作流会在以下情况自动触发：

1. **推送到主分支**（main 或 master）
   - 自动构建并发布 `latest` 标签
   
2. **创建版本标签**（如 `v1.0.0`、`v1.2.3`）
   - 自动构建并发布版本标签
   - 同时发布 `latest` 标签（如果是主分支）
   - 支持语义化版本标签（major.minor.patch）

3. **手动触发**
   - 可以在 GitHub Actions 页面手动运行工作流

## 🔧 配置步骤

### 1. 创建 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 点击右上角头像 → **Account Settings**
3. 进入 **Security** 选项卡
4. 点击 **New Access Token**
5. 填写描述（如 `github-actions-telegram-115bot`）
6. 选择权限：**Read, Write, Delete**（推荐）或 **Read & Write**
7. 点击 **Generate**
8. **重要**：立即复制生成的 Token（只显示一次！）

### 2. 配置 GitHub Secrets

1. 打开你的 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret** 添加以下两个密钥：

#### Secret 1: DOCKERHUB_USERNAME
- **Name**: `DOCKERHUB_USERNAME`
- **Value**: 你的 Docker Hub 用户名（例如：`janebin`）

#### Secret 2: DOCKERHUB_TOKEN
- **Name**: `DOCKERHUB_TOKEN`
- **Value**: 在步骤 1 中生成的 Access Token（**不是**你的 Docker Hub 密码！）

### 3. 验证配置

配置完成后，你可以通过以下方式验证：

1. **推送代码到主分支**
   ```bash
   git add .
   git commit -m "Test Docker publish"
   git push origin main
   ```

2. **创建版本标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. 查看 GitHub Actions 运行状态：
   - 进入仓库的 **Actions** 标签页
   - 查看 "Build and Push Docker Image to Docker Hub" 工作流
   - 检查运行日志确认构建成功

## 📦 镜像标签策略

### 主分支推送
推送到 `main` 或 `master` 分支时：
- `janebin/telegram-115bot:latest`
- `janebin/telegram-115bot:main`（或 `master`）

### 版本标签
创建版本标签时（如 `v1.2.3`）：
- `janebin/telegram-115bot:1.2.3`
- `janebin/telegram-115bot:1.2`
- `janebin/telegram-115bot:1`
- `janebin/telegram-115bot:latest`

### 示例

```bash
# 发布 latest 版本
git push origin main

# 发布特定版本
git tag v1.0.0
git push origin v1.0.0

# 发布补丁版本
git tag v1.0.1
git push origin v1.0.1
```

## 🏗️ 工作流特性

### 多架构支持
- **AMD64**（x86_64）：适用于大多数云服务器和个人电脑
- **ARM64**（aarch64）：适用于 Apple Silicon、Raspberry Pi 等

### 构建前验证
自动运行以下检查：
- ✅ Python 语法检查
- ✅ Dockerfile 验证
- ✅ 必需文件检查（requirements.txt、nginx.conf、supervisord.conf）

### 构建缓存
使用 GitHub Actions 缓存机制，加速后续构建（首次构建较慢，后续构建更快）。

### 镜像元数据
自动添加以下标签：
- 构建日期
- Git 提交 SHA
- OCI 标准元数据

## 🐳 使用 Docker 镜像

### 拉取镜像

```bash
# 拉取最新版本
docker pull janebin/telegram-115bot:latest

# 拉取特定版本
docker pull janebin/telegram-115bot:1.0.0
```

### 使用 Docker Compose

项目已包含 `docker-compose.yml` 文件，修改镜像名称后即可使用：

```yaml
version: "3.8"
services:
  backend:
    image: janebin/telegram-115bot:latest
    container_name: telegram_115_backend
    restart: unless-stopped
    ports:
      - "12808:12808"
    volumes:
      - ./backend/config.json:/app/config.json
      - ./backend/uploads:/app/uploads
      - ./backend/backend.log:/app/backend.log
      - ./backend/secrets.db:/app/secrets.db
      - ./backend/data.db:/app/data.db
      - ./backend/data:/app/data
```

运行：

```bash
docker-compose up -d
```

### 直接运行容器

```bash
docker run -d \
  --name telegram-115bot \
  -p 12808:12808 \
  -v $(pwd)/backend/data:/app/data \
  -v $(pwd)/backend/uploads:/app/uploads \
  janebin/telegram-115bot:latest
```

## 🔍 故障排查

### 问题 1：工作流失败 - "Login to Docker Hub" 步骤

**原因**：Docker Hub 凭证配置错误

**解决方法**：
1. 检查 GitHub Secrets 中的 `DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN` 是否正确
2. 确认 Token 没有过期
3. 重新生成 Token 并更新 Secret

### 问题 2：工作流失败 - "Build and push" 步骤

**原因**：可能是 Dockerfile 错误或依赖问题

**解决方法**：
1. 本地测试构建：`docker build -t test .`
2. 检查 requirements.txt 中的依赖是否可用
3. 查看 GitHub Actions 日志获取详细错误信息

### 问题 3：多架构构建很慢

**原因**：首次构建需要为两个架构编译，尤其是 ARM64 模拟构建较慢

**解决方法**：
- 等待首次构建完成后，后续构建会使用缓存，速度会大幅提升
- 如果只需要单架构，可以修改工作流中的 `platforms` 参数

## 📊 工作流状态徽章

在你的 `README.md` 中添加以下徽章显示工作流状态：

```markdown
[![Docker Build](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/docker-publish.yml)
```

将 `YOUR_USERNAME` 和 `YOUR_REPO` 替换为你的 GitHub 用户名和仓库名。

## 📚 更多资源

- [Docker Hub 官方文档](https://docs.docker.com/docker-hub/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Buildx 多架构构建](https://docs.docker.com/buildx/working-with-buildx/)
- [语义化版本规范](https://semver.org/lang/zh-CN/)

## ⚙️ 高级配置

### 自定义镜像仓库名

如果你想使用不同的镜像名称，修改工作流文件 `.github/workflows/docker-publish.yml`：

```yaml
env:
  IMAGE_NAME: your-custom-name  # 修改这里
```

### 添加更多平台

在工作流文件中修改 `platforms` 参数：

```yaml
platforms: linux/amd64,linux/arm64,linux/arm/v7
```

### 禁用自动发布 latest 标签

在工作流文件中注释或删除以下行：

```yaml
type=raw,value=latest,enable={{is_default_branch}}
```

## 📝 版本发布最佳实践

1. **使用语义化版本**：遵循 `vMAJOR.MINOR.PATCH` 格式
   - MAJOR：不兼容的 API 修改
   - MINOR：向下兼容的功能性新增
   - PATCH：向下兼容的问题修正

2. **创建 Release Notes**：在 GitHub 上创建 Release 时添加更新日志

3. **测试后发布**：在开发分支测试通过后再推送到主分支或打标签

4. **使用 Pre-release**：测试版本可以使用 `v1.0.0-beta.1` 等标签

## 🙋 获取帮助

如果遇到问题：
1. 查看 GitHub Actions 日志获取详细错误信息
2. 检查本文档的故障排查部分
3. 在项目 Issues 中提问

---

**配置完成后，你的 Docker 镜像将自动构建和发布！** 🎉
