# 🚀 快速设置指南 - Docker Hub 自动发布

## 📌 概述

本指南帮助你快速完成 Telegram 115 Bot 的 Docker Hub 自动发布配置。

---

## ⚡ 三步完成设置

### 第 1 步：配置 GitHub Secrets（2 分钟）

访问：https://github.com/janebin/telegram-115bot/settings/secrets/actions

添加两个 Secrets：

| Secret Name | Secret Value |
|------------|--------------|
| `DOCKERHUB_USERNAME` | `janebin` |
| `DOCKERHUB_TOKEN` | `<your-docker-hub-token>` |

### 第 2 步：触发构建（1 分钟）

访问：https://github.com/janebin/telegram-115bot/actions

1. 选择 "Build and Push Docker Image to Docker Hub" 工作流
2. 点击 "Run workflow" 按钮
3. 选择 `main` 分支
4. 点击 "Run workflow" 开始构建

### 第 3 步：验证部署（5 分钟）

等待构建完成（15-20 分钟），然后：

```bash
# 方法 A: 使用验证脚本（推荐）
./verify-docker-image.sh

# 方法 B: 手动验证
docker pull janebin/telegram-115bot:latest
docker run --rm -p 12808:12808 janebin/telegram-115bot:latest
```

访问：http://localhost:12808

---

## 📚 详细文档

如需更详细的说明，请参考：

### 核心文档

1. **[GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)**
   - 完整的 GitHub Secrets 配置步骤
   - 构建进度监控指南
   - 故障排查方案

2. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**
   - 完整的部署检查清单
   - 详细的验证步骤
   - 常见问题解答

3. **[DOCKER_PUBLISH.md](DOCKER_PUBLISH.md)**
   - Docker Hub 自动发布配置说明
   - 工作流详细解析

### 工具脚本

- **verify-docker-image.sh**
  - 自动验证 Docker 镜像
  - 一键启动测试容器
  - 健康检查和状态监控

---

## 🎯 成功标志

当你看到以下内容时，说明部署成功：

✅ GitHub Actions 显示绿色勾选  
✅ Docker Hub 页面显示镜像  
✅ 本地可以拉取并运行镜像  
✅ http://localhost:12808 可以访问  
✅ 可以使用 admin/admin 登录  

---

## 🔗 快速链接

| 链接 | 用途 |
|-----|------|
| [GitHub Secrets](https://github.com/janebin/telegram-115bot/settings/secrets/actions) | 配置 Secrets |
| [GitHub Actions](https://github.com/janebin/telegram-115bot/actions) | 查看构建状态 |
| [Docker Hub](https://hub.docker.com/r/janebin/telegram-115bot) | 查看发布的镜像 |

---

## 💡 提示

- **首次构建**：通常需要 15-20 分钟
- **后续构建**：利用缓存可能更快（10-15 分钟）
- **构建触发**：每次推送到 `main` 分支都会自动构建
- **版本标签**：推送 `v*` 标签会创建版本镜像

---

## 🆘 需要帮助？

1. 查看 [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) 的故障排查部分
2. 查看 GitHub Actions 的详细日志
3. 运行 `./verify-docker-image.sh` 进行诊断

---

**快速设置，立即使用！** 🚀
