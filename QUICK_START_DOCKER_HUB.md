# 🚀 Docker Hub 自动发布快速启动指南

## ⏱️ 5 分钟快速配置

### 第 1 步: 生成 Docker Hub Token (2 分钟)

1. 访问 https://hub.docker.com/
2. 登录账号 `janebin`
3. 点击右上角头像 → **Account Settings**
4. 进入 **Security** 选项卡
5. 点击 **New Access Token**
6. 填写:
   - Description: `github-actions-telegram-115bot`
   - Permissions: **Read, Write, Delete**
7. 点击 **Generate**
8. **立即复制** Token（只显示一次！）

### 第 2 步: 配置 GitHub Secrets (2 分钟)

1. 访问 https://github.com/janebin/telegram-115bot/settings/secrets/actions

2. 点击 **New repository secret**

3. 添加第一个 Secret:
   - Name: `DOCKERHUB_USERNAME`
   - Secret: `janebin`
   - 点击 **Add secret**

4. 再次点击 **New repository secret**

5. 添加第二个 Secret:
   - Name: `DOCKERHUB_TOKEN`
   - Secret: (粘贴步骤 1 中的 Token)
   - 点击 **Add secret**

### 第 3 步: 触发首次构建 (1 分钟)

#### 选项 A: 手动触发（最简单）

1. 访问 https://github.com/janebin/telegram-115bot/actions
2. 点击 "Build and Push Docker Image to Docker Hub"
3. 点击 **Run workflow**
4. 选择 `main` 分支
5. 点击 **Run workflow**

#### 选项 B: 推送代码触发

```bash
# 合并到 main 分支
git checkout main
git merge ci-dockerhub-verify-publish-telegram-115bot
git push origin main
```

#### 选项 C: 创建标签触发

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 第 4 步: 监控构建 (10-20 分钟)

1. 访问 https://github.com/janebin/telegram-115bot/actions
2. 查看最新的工作流运行
3. 等待所有步骤显示 ✅（首次约 10-20 分钟）

### 第 5 步: 验证发布 (1 分钟)

```bash
# 访问 Docker Hub 仓库
# https://hub.docker.com/r/janebin/telegram-115bot

# 拉取镜像
docker pull janebin/telegram-115bot:latest

# 运行测试
docker run -d --name test -p 12808:12808 janebin/telegram-115bot:latest

# 访问应用
curl http://localhost:12808

# 清理
docker stop test && docker rm test
```

## ✅ 完成！

你的 Docker Hub 自动发布已配置完成！🎉

每次推送到 `main` 分支或创建版本标签，都会自动构建并发布镜像。

---

## 📚 详细文档

需要更多帮助？查看完整文档：

- [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) - Secrets 配置详解
- [DOCKER_HUB_AUTO_PUBLISH_SUMMARY.md](DOCKER_HUB_AUTO_PUBLISH_SUMMARY.md) - 配置总结
- [DOCKER_HUB_SETUP_VERIFICATION.md](DOCKER_HUB_SETUP_VERIFICATION.md) - 验证清单
- [DOCKER_PUBLISH.md](DOCKER_PUBLISH.md) - 完整发布指南

## 🆘 遇到问题？

### Login 失败
- 检查 Secret 名称是否完全匹配
- 确认使用 Token 而非密码
- 验证 Token 权限包含 Write

### 构建失败
- 查看 GitHub Actions 详细日志
- 本地测试: `docker build -t test .`

### 推送失败
- 确认 Docker Hub 仓库存在
- 检查 Token 权限

---

**Docker Hub**: https://hub.docker.com/r/janebin/telegram-115bot  
**GitHub**: https://github.com/janebin/telegram-115bot
