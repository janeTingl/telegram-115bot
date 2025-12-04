# GitHub Secrets 配置指南

本文档详细说明如何为 telegram-115bot 仓库配置 GitHub Secrets 以实现 Docker 镜像的自动构建和发布。

## 📋 前置条件

- ✅ GitHub 仓库：`janebin/telegram-115bot`
- ✅ Docker Hub 账号：`janebin`
- ✅ Docker Hub Access Token（已准备）
- ✅ GitHub Actions 工作流文件（已配置）

## 🔐 配置 GitHub Secrets

### 步骤 1：访问仓库设置

1. 打开浏览器，访问：`https://github.com/janebin/telegram-115bot`
2. 点击仓库页面顶部的 **Settings**（设置）选项卡
3. 在左侧菜单中找到 **Secrets and variables**
4. 点击 **Actions** 子菜单

### 步骤 2：添加 DOCKERHUB_USERNAME

1. 点击右上角的 **New repository secret** 按钮
2. 填写以下信息：
   - **Name**: `DOCKERHUB_USERNAME`
   - **Value**: `janebin`
3. 点击 **Add secret** 按钮保存

### 步骤 3：添加 DOCKERHUB_TOKEN

1. 再次点击 **New repository secret** 按钮
2. 填写以下信息：
   - **Name**: `DOCKERHUB_TOKEN`
   - **Value**: `<your-docker-hub-token>`
3. 点击 **Add secret** 按钮保存

### 步骤 4：验证 Secrets

配置完成后，你应该在 Secrets 列表中看到：
- ✅ `DOCKERHUB_USERNAME`
- ✅ `DOCKERHUB_TOKEN`

> **注意**：出于安全考虑，GitHub 不会显示 Secret 的值，只显示名称。

## 🚀 触发首次构建

配置 Secrets 后，你可以通过以下方式触发构建：

### 方法 1：手动触发（推荐）

1. 访问 GitHub Actions 页面：`https://github.com/janebin/telegram-115bot/actions`
2. 在左侧选择 **Build and Push Docker Image to Docker Hub** 工作流
3. 点击右上角的 **Run workflow** 按钮
4. 选择分支 `main`
5. 点击绿色的 **Run workflow** 按钮

### 方法 2：推送代码触发

工作流会在以下情况自动触发：
- 推送到 `main` 或 `master` 分支
- 创建以 `v` 开头的标签（如 `v1.0.0`）

本次提交已包含一个小更新，会自动触发构建。

## 📊 监控构建进度

### 查看工作流状态

1. 访问 Actions 页面：`https://github.com/janebin/telegram-115bot/actions`
2. 找到最新的工作流运行
3. 点击进入查看详细日志

### 构建阶段说明

工作流包含 3 个主要任务：

#### 1. Pre-build Validation（预构建验证）
- ✅ 检查 Python 语法
- ✅ 验证 Dockerfile
- ✅ 检查必需文件

预计时间：1-2 分钟

#### 2. Build and Push Docker Image（构建和推送镜像）
- ✅ 设置 QEMU（多架构支持）
- ✅ 登录 Docker Hub
- ✅ 构建 AMD64 架构镜像
- ✅ 构建 ARM64 架构镜像
- ✅ 推送到 Docker Hub

预计时间：10-20 分钟

#### 3. Notification（通知）
- ✅ 检查构建状态
- ✅ 输出构建结果

预计时间：< 1 分钟

### 总构建时间

预计总时长：**15-25 分钟**（取决于 GitHub Actions runner 的负载）

## ✅ 验证发布成功

### 1. GitHub Actions 状态

在 Actions 页面应该看到：
- ✅ **Pre-build Validation**: 绿色勾选
- ✅ **Build and Push Docker Image**: 绿色勾选
- ✅ **Notification**: 绿色勾选

### 2. Docker Hub 验证

访问 Docker Hub 仓库页面：
```
https://hub.docker.com/r/janebin/telegram-115bot
```

你应该看到：
- ✅ 仓库已创建
- ✅ 镜像标签：`latest`, `main`
- ✅ 支持架构：`linux/amd64`, `linux/arm64`
- ✅ 最后更新时间：刚刚

### 3. 本地测试

在本地拉取镜像进行测试：

```bash
# 拉取最新镜像
docker pull janebin/telegram-115bot:latest

# 验证镜像信息
docker inspect janebin/telegram-115bot:latest

# 运行容器测试
docker run -d \
  --name telegram-115bot-test \
  -p 12808:12808 \
  janebin/telegram-115bot:latest

# 检查容器状态
docker ps | grep telegram-115bot-test

# 访问测试（可选）
curl http://localhost:12808

# 清理测试容器
docker stop telegram-115bot-test
docker rm telegram-115bot-test
```

## 🎯 成功标志清单

配置和首次构建成功后，确认以下各项：

- [ ] GitHub Secrets 已正确配置
  - [ ] `DOCKERHUB_USERNAME` = `janebin`
  - [ ] `DOCKERHUB_TOKEN` = `dckr_pat_SEV-...`
- [ ] 工作流已成功运行
  - [ ] Pre-build Validation: ✅
  - [ ] Build and Push: ✅
  - [ ] Notification: ✅
- [ ] Docker Hub 镜像已发布
  - [ ] 仓库 URL: `hub.docker.com/r/janebin/telegram-115bot`
  - [ ] 标签 `latest` 存在
  - [ ] 多架构支持已启用
- [ ] 本地可拉取镜像
  - [ ] `docker pull janebin/telegram-115bot:latest` 成功
- [ ] README 徽章显示正常
  - [ ] Docker Build 徽章：绿色
  - [ ] Docker Hub 徽章：显示拉取次数

## 🔧 故障排查

### 问题 1：Secrets 未生效

**症状**：工作流失败，提示认证错误

**解决方案**：
1. 确认 Secret 名称完全匹配（区分大小写）
2. 重新创建 Secrets
3. 确保 Docker Hub Token 未过期

### 问题 2：构建超时

**症状**：构建运行超过 30 分钟

**解决方案**：
1. 取消当前运行
2. 等待 5-10 分钟后重试
3. 检查 GitHub Actions 服务状态

### 问题 3：多架构构建失败

**症状**：AMD64 成功但 ARM64 失败

**解决方案**：
1. 检查 Dockerfile 是否支持多架构
2. 确认 QEMU 设置正确
3. 查看详细构建日志

### 问题 4：Docker Hub 推送失败

**症状**：构建成功但推送失败

**解决方案**：
1. 验证 Docker Hub Token 权限
2. 确认仓库名称正确
3. 检查 Docker Hub 存储配额

## 📞 获取帮助

如果遇到问题：

1. **查看日志**：GitHub Actions 页面 → 点击失败的工作流 → 查看详细日志
2. **检查文档**：参考 [DOCKER_PUBLISH.md](DOCKER_PUBLISH.md)
3. **重试构建**：很多问题可以通过重新运行解决

## 🎉 下一步

首次构建成功后，你可以：

1. **使用镜像部署**：
   ```bash
   docker-compose up -d
   ```

2. **创建版本标签**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **配置自动化**：每次推送到 main 分支都会自动构建和发布

4. **监控徽章**：README 中的徽章会实时显示构建状态

---

**配置完成时间**：2024

**文档版本**：1.0

**维护者**：Telegram 115 Bot Team
