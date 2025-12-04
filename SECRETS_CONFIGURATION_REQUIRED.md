# 🔐 GitHub Secrets 配置 - 立即行动指南

## ⚠️ 重要提示

由于 API 权限限制，GitHub Secrets 需要通过 GitHub Web 界面手动配置。本文档提供完整的配置步骤和确切的值。

## 📋 配置信息

### 仓库信息
- **GitHub 仓库**: `janeTingl/telegram-115bot`
- **仓库 URL**: https://github.com/janeTingl/telegram-115bot
- **主分支**: `main`

### Docker Hub 信息
- **用户名**: `janebin`
- **Token**: `dckr_pat_***` (见下方获取方式)

## 🚀 立即配置步骤

### 第 1 步：访问 Secrets 设置页面

直接访问以下 URL（需要登录 GitHub）：

```
https://github.com/janeTingl/telegram-115bot/settings/secrets/actions
```

或者手动导航：
1. 打开 https://github.com/janeTingl/telegram-115bot
2. 点击 **Settings** 选项卡
3. 左侧菜单：**Secrets and variables** → **Actions**

### 第 2 步：添加第一个 Secret - DOCKERHUB_USERNAME

1. 点击 **New repository secret** 按钮
2. 填写表单：
   ```
   Name: DOCKERHUB_USERNAME
   Value: janebin
   ```
3. 点击 **Add secret** 保存

### 第 3 步：添加第二个 Secret - DOCKERHUB_TOKEN

1. 再次点击 **New repository secret** 按钮  
2. 填写表单：
   ```
   Name: DOCKERHUB_TOKEN
   Value: [从本地文件 .dockerhub-token 获取完整 Token]
   ```
   
   **获取 Token 值**：
   ```bash
   # 方法 1: 查看本地文件
   cat .dockerhub-token
   
   # 方法 2: 从 Docker Hub 重新生成
   # 访问 https://hub.docker.com/settings/security
   # 生成新的 Access Token (Read, Write, Delete 权限)
   ```

3. 点击 **Add secret** 保存

### 第 4 步：验证配置

在 Secrets 列表中确认显示：
- ✅ DOCKERHUB_USERNAME
- ✅ DOCKERHUB_TOKEN

> 注意：Secret 的值不会显示，这是正常的安全措施

## 🎯 触发工作流

配置完 Secrets 后，有两种方式触发 Docker 镜像构建：

### 方式 A：手动触发工作流（最快）

1. 访问 Actions 页面：
   ```
   https://github.com/janeTingl/telegram-115bot/actions
   ```

2. 左侧选择工作流：
   ```
   Build and Push Docker Image to Docker Hub
   ```

3. 点击右上角的 **Run workflow** 按钮

4. 在弹出窗口中：
   - Branch: `main`
   - 点击绿色的 **Run workflow** 按钮

### 方式 B：推送代码触发（自动）

本次已准备了一个小更新，配置完 Secrets 后执行：

```bash
git checkout main
git pull origin main
git push origin main
```

工作流将自动触发。

## 📊 监控构建过程

### 1. 查看工作流状态

访问：https://github.com/janeTingl/telegram-115bot/actions

构建包含 3 个阶段：

| 阶段 | 名称 | 预计时间 | 关键步骤 |
|------|------|----------|----------|
| 1 | Pre-build Validation | 1-2 分钟 | Python 语法检查、Dockerfile 验证 |
| 2 | Build and Push Docker Image | 10-20 分钟 | 多架构构建、推送到 Docker Hub |
| 3 | Notification | < 1 分钟 | 构建状态通知 |

**总预计时间**: 15-25 分钟

### 2. 关键步骤检查

在 **Build and Push Docker Image** 阶段，特别关注：

✅ **Login to Docker Hub** - 此步骤必须成功，表明 Secrets 配置正确
✅ **Build and push multi-arch image** - 构建并推送 AMD64 和 ARM64 镜像

## ✅ 验证发布成功

### 1. GitHub Actions 验证

在 Actions 页面确认：
- ✅ 所有 3 个任务都显示绿色勾选
- ✅ 没有红色失败标记
- ✅ 工作流总体状态为 Success

### 2. Docker Hub 验证

访问镜像仓库：
```
https://hub.docker.com/r/janebin/telegram-115bot
```

确认以下内容：
- ✅ 仓库已创建
- ✅ 标签显示：`latest`, `main`  
- ✅ 架构支持：`linux/amd64`, `linux/arm64`
- ✅ 最后推送时间：刚刚

### 3. 本地拉取验证

在本地终端执行：

```bash
# 拉取镜像
docker pull janebin/telegram-115bot:latest

# 验证镜像
docker images | grep telegram-115bot

# 查看镜像详情
docker inspect janebin/telegram-115bot:latest | grep -A 5 "Architecture"
```

应该看到成功拉取的消息。

## 🔍 常见问题排查

### 问题 1：Login to Docker Hub 步骤失败

**错误信息**: "Error: Invalid username or password"

**原因**: Secrets 配置不正确

**解决方案**:
1. 回到 Secrets 设置页面
2. 删除现有的 DOCKERHUB_USERNAME 和 DOCKERHUB_TOKEN
3. 重新创建，确保没有多余空格
4. 重新运行工作流

### 问题 2：工作流无法找到 Secrets

**错误信息**: "Error: Username and password required"

**原因**: Secret 名称不匹配

**解决方案**:
确保 Secret 名称完全一致（区分大小写）：
- `DOCKERHUB_USERNAME`（不是 DockerHubUsername）
- `DOCKERHUB_TOKEN`（不是 DOCKERHUB_TOKEN）

### 问题 3：构建超时

**解决方案**:
1. 取消当前运行
2. 等待 5 分钟
3. 重新运行工作流

## 📝 快速检查清单

配置前：
- [ ] 已登录 GitHub 账号 `janeTingl`
- [ ] 有仓库 Settings 访问权限
- [ ] 已准备好 Docker Hub 凭据

配置中：
- [ ] Secret 名称完全匹配（DOCKERHUB_USERNAME, DOCKERHUB_TOKEN）
- [ ] Token 值完整复制（包括 `dckr_pat_` 前缀）
- [ ] 没有多余的空格或换行

配置后：
- [ ] 两个 Secrets 都显示在列表中
- [ ] 工作流已触发
- [ ] 所有阶段都成功（绿色）
- [ ] Docker Hub 上可见镜像

## 🎉 成功标志

当看到以下内容时，任务完成：

1. ✅ GitHub Secrets 配置页面显示 2 个 Secrets
2. ✅ GitHub Actions 工作流状态：Success ✓
3. ✅ Docker Hub 页面显示新发布的镜像
4. ✅ 本地可以成功拉取：`docker pull janebin/telegram-115bot:latest`

## 📞 需要帮助？

如果遇到问题：

1. **查看详细日志**: GitHub Actions 页面 → 点击工作流 → 展开失败的步骤
2. **检查 Secret 值**: 删除并重新创建 Secrets
3. **验证 Token**: 使用脚本 `./verify-dockerhub-token.sh` 测试 Token 有效性
4. **重新运行**: 大多数临时问题可以通过重新运行解决

---

**创建时间**: 2024-12-04
**优先级**: 🔥 高
**预计完成时间**: 5 分钟配置 + 15-25 分钟构建

**下一步**: 配置完 Secrets 后立即触发工作流！
