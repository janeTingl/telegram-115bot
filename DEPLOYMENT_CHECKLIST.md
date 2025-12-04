# Telegram 115 Bot - 部署检查清单

本文档提供完整的部署和验证流程，确保 Docker Hub 自动发布功能正常工作。

## 📋 准备阶段

### 已完成项

- ✅ GitHub 仓库：`janebin/telegram-115bot`
- ✅ Docker Hub 账号：`janebin`
- ✅ Docker Hub Token：已生成
- ✅ GitHub Actions 工作流：已配置（`.github/workflows/docker-publish.yml`）
- ✅ 多架构支持：AMD64 + ARM64
- ✅ 文档齐全：配置指南、验证脚本

### 需要完成的操作

以下操作需要**手动在 GitHub 网站上完成**：

## 🔐 步骤 1：配置 GitHub Secrets

> ⚠️ **重要**：此步骤必须在 GitHub 网站上手动完成

### 操作步骤

1. 访问仓库 Secrets 配置页面：
   ```
   https://github.com/janebin/telegram-115bot/settings/secrets/actions
   ```

2. 添加第一个 Secret：
   - 点击 **New repository secret**
   - Name: `DOCKERHUB_USERNAME`
   - Value: `janebin`
   - 点击 **Add secret**

3. 添加第二个 Secret：
   - 点击 **New repository secret**
   - Name: `DOCKERHUB_TOKEN`
   - Value: `<your-docker-hub-token>`
   - 点击 **Add secret**

4. 验证 Secrets：
   - 在 Secrets 列表中应看到：
     - ✅ `DOCKERHUB_USERNAME`
     - ✅ `DOCKERHUB_TOKEN`

### 配置参考

完整的配置说明请参考：[GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)

---

## 🚀 步骤 2：触发首次构建

配置完 Secrets 后，有以下几种方式触发构建：

### 方法 A：手动触发（最简单，推荐）

1. 访问 GitHub Actions 页面：
   ```
   https://github.com/janebin/telegram-115bot/actions
   ```

2. 选择左侧的 **Build and Push Docker Image to Docker Hub** 工作流

3. 点击右上角的 **Run workflow** 按钮

4. 选择分支 `main`

5. 点击绿色的 **Run workflow** 按钮启动构建

### 方法 B：通过推送代码触发（自动）

本次提交已经包含了文档更新和小改动，推送到 `main` 分支后会自动触发构建：

```bash
# 查看当前分支
git branch

# 推送到 main 分支（如果需要）
git push origin ci-configure-github-secrets-docker-publish-telegram-115bot:main
```

### 方法 C：创建版本标签

```bash
# 创建并推送标签
git tag v1.0.0
git push origin v1.0.0

# 这会触发构建并创建 v1.0.0 标签的镜像
```

---

## 📊 步骤 3：监控构建进度

### 查看实时日志

1. 访问 Actions 页面：
   ```
   https://github.com/janebin/telegram-115bot/actions
   ```

2. 点击最新的工作流运行

3. 查看三个主要任务的进度：
   - **Pre-build Validation** (~2 分钟)
     - Python 语法检查
     - Dockerfile 验证
     - 依赖文件检查
   
   - **Build and Push Docker Image** (~10-20 分钟)
     - QEMU 多架构设置
     - Docker Hub 登录
     - AMD64 镜像构建
     - ARM64 镜像构建
     - 镜像推送
   
   - **Notification** (~1 分钟)
     - 构建结果通知

### 预期总时长

- **最少**：12 分钟
- **通常**：15-20 分钟
- **最多**：30 分钟（高负载时）

### 成功标志

所有任务都应显示 ✅ 绿色勾选标记。

---

## ✅ 步骤 4：验证发布成功

### 4.1 GitHub Actions 验证

在 Actions 页面检查：
- [ ] Pre-build Validation: ✅ 成功
- [ ] Build and Push: ✅ 成功  
- [ ] Notification: ✅ 成功
- [ ] 总体状态：✅ 绿色

### 4.2 Docker Hub 验证

访问 Docker Hub 仓库：
```
https://hub.docker.com/r/janebin/telegram-115bot
```

检查项：
- [ ] 仓库已创建且可访问
- [ ] 存在 `latest` 标签
- [ ] 存在 `main` 标签
- [ ] 显示支持的架构：linux/amd64, linux/arm64
- [ ] 镜像大小合理（预计 500MB-1GB）
- [ ] 最后更新时间：刚刚

### 4.3 本地拉取验证

使用验证脚本（推荐）：

```bash
# 运行验证脚本
./verify-docker-image.sh
```

或手动验证：

```bash
# 拉取镜像
docker pull janebin/telegram-115bot:latest

# 查看镜像信息
docker images janebin/telegram-115bot

# 检查镜像架构
docker manifest inspect janebin/telegram-115bot:latest
```

### 4.4 容器运行测试

```bash
# 快速测试运行
docker run --rm -p 12808:12808 janebin/telegram-115bot:latest

# 或使用 Docker Compose
docker-compose up -d

# 访问测试
curl http://localhost:12808
# 或在浏览器打开 http://localhost:12808
```

### 4.5 功能测试

1. 访问 `http://localhost:12808`
2. 使用默认凭据登录：
   - 用户名：`admin`
   - 密码：`admin`
3. 验证主要功能：
   - [ ] 登录成功
   - [ ] 可以访问仪表板
   - [ ] 各个菜单可以正常打开
   - [ ] 配置可以正常保存

---

## 📈 步骤 5：更新 README 徽章

确认 README 中的徽章正常显示：

- **Docker Build 徽章**：
  ```markdown
  [![Docker Build](https://github.com/janebin/telegram-115bot/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/janebin/telegram-115bot/actions/workflows/docker-publish.yml)
  ```
  应显示：![badge](https://img.shields.io/badge/build-passing-brightgreen)

- **Docker Hub 徽章**：
  ```markdown
  [![Docker Hub](https://img.shields.io/docker/pulls/janebin/telegram-115bot.svg)](https://hub.docker.com/r/janebin/telegram-115bot)
  ```
  应显示拉取次数（初始可能为 0）

---

## 🎯 完整检查清单

### GitHub 配置

- [ ] Secrets `DOCKERHUB_USERNAME` 已添加
- [ ] Secrets `DOCKERHUB_TOKEN` 已添加
- [ ] 工作流文件 `.github/workflows/docker-publish.yml` 存在
- [ ] 工作流文件中 Secrets 引用正确

### 首次构建

- [ ] 构建已触发（手动或自动）
- [ ] Pre-build Validation 通过
- [ ] Build and Push 成功
- [ ] Notification 显示成功

### Docker Hub

- [ ] 仓库 `janebin/telegram-115bot` 可访问
- [ ] `latest` 标签存在
- [ ] `main` 标签存在
- [ ] 多架构镜像已发布（amd64, arm64）
- [ ] 镜像可以正常拉取

### 本地测试

- [ ] 镜像拉取成功
- [ ] 容器启动成功
- [ ] 服务端口 12808 可访问
- [ ] Web 界面正常显示
- [ ] 可以登录管理面板

### 文档和工具

- [ ] `GITHUB_SECRETS_SETUP.md` 文档完整
- [ ] `DEPLOYMENT_CHECKLIST.md` 文档完整
- [ ] `verify-docker-image.sh` 脚本可用
- [ ] README 引用了配置指南

---

## 🔧 常见问题排查

### Q1: Secrets 配置后工作流仍然失败

**检查**：
1. Secret 名称是否完全匹配（区分大小写）
2. Secret 值是否正确复制（没有多余空格）
3. Docker Hub Token 是否有效

**解决**：
- 删除并重新创建 Secrets
- 确保使用正确的 Token（以 `dckr_pat_` 开头）

### Q2: 构建超时或卡住

**检查**：
1. GitHub Actions runner 状态
2. 构建日志中的具体错误

**解决**：
- 取消当前运行，等待几分钟后重试
- 检查 Dockerfile 是否有语法错误

### Q3: Docker Hub 推送失败

**检查**：
1. Docker Hub Token 权限
2. 仓库名称是否正确
3. Docker Hub 账号状态

**解决**：
- 重新生成 Docker Hub Token（确保有写权限）
- 确认仓库名称：`janebin/telegram-115bot`

### Q4: 镜像拉取失败

**检查**：
1. 镜像是否已成功推送到 Docker Hub
2. 镜像名称和标签是否正确
3. Docker Hub 仓库权限设置（应设为 Public）

**解决**：
- 访问 Docker Hub 确认镜像存在
- 确保仓库是 Public 而不是 Private
- 检查网络连接

---

## 🎉 成功标志

当以下所有项目都完成时，说明部署成功：

✅ GitHub Secrets 配置完成
✅ 工作流首次运行成功
✅ Docker Hub 镜像已发布
✅ 多架构镜像可用（AMD64 + ARM64）
✅ 本地可以拉取并运行镜像
✅ Web 界面可以正常访问
✅ README 徽章显示正常

---

## 📞 获取帮助

如需进一步帮助，请：

1. 查看详细文档：
   - [GitHub Secrets 配置](GITHUB_SECRETS_SETUP.md)
   - [Docker 发布配置](DOCKER_PUBLISH.md)

2. 检查日志：
   - GitHub Actions 工作流日志
   - Docker 容器日志

3. 使用验证脚本：
   ```bash
   ./verify-docker-image.sh
   ```

---

## 🚀 下一步

部署成功后，你可以：

1. **配置 Bot**：在 Web 界面配置 Telegram Bot Token

2. **设置自动化**：每次推送到 main 都会自动构建

3. **创建版本发布**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **生产环境部署**：
   ```bash
   docker-compose up -d
   ```

5. **监控服务**：使用 Docker 命令或 Web 界面监控服务状态

---

**文档版本**：1.0  
**创建时间**：2024  
**维护者**：Telegram 115 Bot Team

**快速链接**：
- [GitHub 仓库](https://github.com/janebin/telegram-115bot)
- [Docker Hub](https://hub.docker.com/r/janebin/telegram-115bot)
- [GitHub Actions](https://github.com/janebin/telegram-115bot/actions)
