# 🎯 Docker Hub 自动发布 - 用户操作指引

> **目标用户**: janebin  
> **项目**: telegram-115bot  
> **任务**: 启动 Docker Hub 自动化发布

---

## 📋 配置状态

### ✅ 已完成（自动化配置）

以下内容已由开发团队配置完成，无需操作：

- ✅ GitHub Actions 工作流文件 (`.github/workflows/docker-publish.yml`)
- ✅ Dockerfile 验证和优化
- ✅ README.md 更新（用户名、链接、Docker Hub 信息）
- ✅ docker-compose.yml 更新（镜像名称）
- ✅ DOCKER_PUBLISH.md 更新（所有示例用户名）
- ✅ 项目版本标记（VERSION 文件：v1.0.0）
- ✅ 发布说明（RELEASE_NOTES.md）
- ✅ 详细配置文档（多个指南文档）

### ⚠️ 待完成（需要用户操作）

以下操作**必须由用户 janebin 完成**：

1. **配置 GitHub Secrets**（最关键！）
2. 触发首次构建
3. 验证发布结果

---

## 🚨 重要：立即操作

### 操作 1: 配置 GitHub Secrets（必需，5 分钟）

#### 1.1 生成 Docker Hub Access Token

1. 访问 https://hub.docker.com/
2. 使用 `janebin` 账号登录
3. 点击右上角头像 → **Account Settings**
4. 进入 **Security** 选项卡
5. 点击 **New Access Token**
6. 配置 Token:
   ```
   Description: github-actions-telegram-115bot
   Permissions: Read, Write, Delete
   ```
7. 点击 **Generate**
8. **立即复制** Token（只显示一次！格式类似：`dckr_pat_XXXXX...`）
9. 将 Token 保存到安全的地方

#### 1.2 配置 GitHub Secrets

1. 访问 GitHub 仓库设置页面:
   ```
   https://github.com/janebin/telegram-115bot/settings/secrets/actions
   ```

2. 添加第一个 Secret:
   - 点击 **New repository secret**
   - Name: `DOCKERHUB_USERNAME`
   - Secret: `janebin`
   - 点击 **Add secret**

3. 添加第二个 Secret:
   - 再次点击 **New repository secret**
   - Name: `DOCKERHUB_TOKEN`
   - Secret: (粘贴步骤 1.1 中复制的 Token)
   - 点击 **Add secret**

4. 验证配置:
   - 返回 Secrets 页面
   - 确认看到两个 Secrets: `DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN`

**⚠️ 注意**: 
- Secret 名称必须**完全匹配**（区分大小写）
- 使用 Access Token，**不是**密码
- Token 只显示一次，请妥善保存

#### 1.3 详细步骤（含截图说明）

如需详细步骤和说明，请查看: [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)

---

### 操作 2: 触发首次构建（3 种方式任选其一）

#### 方式 A: 手动触发（推荐，最简单）

1. 访问 GitHub Actions 页面:
   ```
   https://github.com/janebin/telegram-115bot/actions
   ```

2. 点击左侧的 "Build and Push Docker Image to Docker Hub" 工作流

3. 点击右上角的 **Run workflow** 按钮

4. 选择 `main` 分支

5. 点击绿色的 **Run workflow** 按钮

6. 等待工作流启动

#### 方式 B: 推送到主分支

如果你有权限推送到 main 分支：

```bash
git checkout main
git merge ci-dockerhub-verify-publish-telegram-115bot
git push origin main
```

#### 方式 C: 创建版本标签（正式发布）

创建 v1.0.0 标签并推送：

```bash
git tag -a v1.0.0 -m "Release v1.0.0: First Docker Hub publication"
git push origin v1.0.0
```

---

### 操作 3: 监控构建过程（10-20 分钟）

1. 访问 GitHub Actions 页面:
   ```
   https://github.com/janebin/telegram-115bot/actions
   ```

2. 点击最新的工作流运行（顶部第一个）

3. 观察构建进度:
   - **Job 1: Pre-build Validation** - 验证代码和配置（约 1-2 分钟）
   - **Job 2: Build and Push Docker Image** - 构建多架构镜像（约 8-15 分钟）
   - **Job 3: Notification** - 发送通知（约 10 秒）

4. 等待所有步骤显示 ✅ 绿色勾

**⚠️ 注意**: 
- 首次构建需要 10-20 分钟（多架构构建）
- 后续构建会更快（5-10 分钟）
- 如果看到红色 ❌，点击查看详细日志

---

### 操作 4: 验证发布结果（2 分钟）

#### 4.1 检查 Docker Hub

1. 访问你的 Docker Hub 仓库:
   ```
   https://hub.docker.com/r/janebin/telegram-115bot
   ```

2. 确认镜像已发布

3. 检查标签:
   - `latest` - 应该存在
   - `main` - 应该存在
   - `1.0.0`, `1.0`, `1` - 如果创建了 v1.0.0 标签

4. 确认支持的架构:
   - `linux/amd64`
   - `linux/arm64`

#### 4.2 测试拉取镜像

在本地终端执行：

```bash
# 拉取镜像
docker pull janebin/telegram-115bot:latest

# 查看镜像信息
docker images | grep telegram-115bot
```

#### 4.3 测试运行容器

```bash
# 运行容器
docker run -d \
  --name telegram-115bot-test \
  -p 12808:12808 \
  janebin/telegram-115bot:latest

# 等待 5 秒让服务启动
sleep 5

# 检查容器状态
docker ps | grep telegram-115bot-test

# 测试访问（应返回 HTML 或 JSON）
curl http://localhost:12808

# 查看日志
docker logs telegram-115bot-test

# 清理测试容器
docker stop telegram-115bot-test
docker rm telegram-115bot-test
```

---

## ✅ 成功标志

完成以上所有操作后，如果满足以下条件，说明配置成功：

- ✅ GitHub Secrets 已配置（2 个）
- ✅ 工作流运行成功（所有步骤绿色 ✅）
- ✅ Docker Hub 仓库中出现镜像
- ✅ 可以成功拉取镜像
- ✅ 容器可以正常运行
- ✅ 可以访问应用（端口 12808）

---

## 🎉 配置完成！

恭喜！你的 Docker Hub 自动化发布已完全配置并验证成功！

### 后续操作

#### 自动发布
从现在开始，每次执行以下操作都会自动触发构建和发布：

1. **推送到 main 分支**
   ```bash
   git push origin main
   ```
   → 自动发布 `latest` 和 `main` 标签

2. **创建版本标签**
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
   → 自动发布 `1.2.3`, `1.2`, `1`, `latest` 标签

3. **手动触发**
   - 在 GitHub Actions 页面点击 "Run workflow"

#### 使用镜像

在任何机器上都可以使用你的镜像：

```bash
# 使用 Docker
docker pull janebin/telegram-115bot:latest
docker run -d -p 12808:12808 janebin/telegram-115bot:latest

# 使用 Docker Compose
docker-compose up -d
```

#### 分享给他人

任何人都可以使用你的公开镜像：

```bash
docker pull janebin/telegram-115bot:latest
```

Docker Hub 地址: https://hub.docker.com/r/janebin/telegram-115bot

---

## 📚 参考文档

| 文档 | 用途 | 何时查看 |
|------|------|----------|
| [QUICK_START_DOCKER_HUB.md](QUICK_START_DOCKER_HUB.md) | 5 分钟快速指南 | 首次配置 |
| [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) | Secrets 详细配置 | 配置 Secrets 时 |
| [DOCKER_HUB_AUTO_PUBLISH_SUMMARY.md](DOCKER_HUB_AUTO_PUBLISH_SUMMARY.md) | 配置总结 | 了解整体配置 |
| [DOCKER_HUB_SETUP_VERIFICATION.md](DOCKER_HUB_SETUP_VERIFICATION.md) | 验证清单 | 验证配置时 |
| [DOCKER_PUBLISH.md](DOCKER_PUBLISH.md) | 完整发布指南 | 深入了解 |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | 发布说明 | 查看版本信息 |

---

## 🆘 遇到问题？

### 问题 1: Login to Docker Hub 失败

**错误**: `Error: unauthorized`

**解决**:
1. 检查 `DOCKERHUB_USERNAME` 是否为 `janebin`（区分大小写）
2. 确认 `DOCKERHUB_TOKEN` 是 Access Token（不是密码）
3. 验证 Token 没有过期
4. 重新生成 Token 并更新 Secret

### 问题 2: Secrets 未配置

**错误**: `Error: Input required and not supplied: username`

**解决**:
- 按照"操作 1"配置 GitHub Secrets
- 确认 Secret 名称完全匹配

### 问题 3: 构建失败

**解决**:
1. 点击失败的工作流查看详细日志
2. 查看 [DOCKER_HUB_SETUP_VERIFICATION.md](DOCKER_HUB_SETUP_VERIFICATION.md) 故障排查部分
3. 在本地测试构建: `docker build -t test .`

### 问题 4: 拉取镜像失败

**解决**:
1. 确认镜像已成功推送到 Docker Hub
2. 检查镜像名称: `janebin/telegram-115bot:latest`
3. 确认网络连接正常

---

## 📞 获取帮助

如需帮助：
1. 查看对应文档的故障排查部分
2. 检查 GitHub Actions 详细日志
3. 在项目 Issues 中提问

---

## 📋 操作检查清单

在完成配置前，请确认：

- [ ] 已生成 Docker Hub Access Token
- [ ] 已配置 `DOCKERHUB_USERNAME` Secret
- [ ] 已配置 `DOCKERHUB_TOKEN` Secret
- [ ] 已触发首次构建（手动/推送/标签）
- [ ] 已监控构建过程并确认成功
- [ ] 已访问 Docker Hub 确认镜像存在
- [ ] 已测试拉取镜像
- [ ] 已测试运行容器
- [ ] 已访问应用确认正常工作
- [ ] 已阅读相关文档以备后续使用

---

## 🎯 快速命令参考

```bash
# 查看 GitHub Actions
open https://github.com/janebin/telegram-115bot/actions

# 查看 Docker Hub
open https://hub.docker.com/r/janebin/telegram-115bot

# 拉取镜像
docker pull janebin/telegram-115bot:latest

# 运行容器
docker run -d --name bot -p 12808:12808 janebin/telegram-115bot:latest

# 查看日志
docker logs bot

# 访问应用
curl http://localhost:12808
open http://localhost:12808

# 停止并删除
docker stop bot && docker rm bot
```

---

**用户**: janebin  
**项目**: telegram-115bot  
**镜像**: janebin/telegram-115bot  
**版本**: v1.0.0  
**配置日期**: 2024-12-04  

**状态**: ✅ 配置就绪，待用户完成 Secrets 配置后即可发布

---

**Good luck! 🚀**
