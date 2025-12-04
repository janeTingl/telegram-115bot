# ⚡ 快速修复：Docker Hub Login 失败

## 🎯 问题
```
Error: Username and password required
```

## ✅ 解决方案（3 步）

### 1️⃣ 访问 Secrets 页面
👉 https://github.com/janebin/telegram-115bot/settings/secrets/actions

### 2️⃣ 添加两个 Secrets

**Secret 1:**
- Name: `DOCKERHUB_USERNAME`
- Value: `janebin`

**Secret 2:**
- Name: `DOCKERHUB_TOKEN`
- Value: `<YOUR_DOCKER_HUB_TOKEN>`

> 📖 **获取 Token**：参见 [SECRETS_INFO.md](SECRETS_INFO.md)

### 3️⃣ 重新运行工作流
👉 https://github.com/janebin/telegram-115bot/actions

点击 **Run workflow**

---

## 📋 检查清单
- [ ] 添加 DOCKERHUB_USERNAME
- [ ] 添加 DOCKERHUB_TOKEN
- [ ] 运行工作流
- [ ] Login to Docker Hub 步骤成功 ✅

---

**详细文档**: [DOCKER_HUB_SECRETS_FIX.md](DOCKER_HUB_SECRETS_FIX.md)
