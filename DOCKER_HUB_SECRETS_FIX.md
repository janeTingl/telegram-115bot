# 🔧 Docker Hub Secrets 配置修复指南

## 问题诊断

### ✅ 工作流文件检查 - 正常

经检查 `.github/workflows/docker-publish.yml` 文件，Docker login 步骤配置正确：

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**结论**：工作流文件本身没有问题，语法和 Secrets 引用都是正确的。

### ❌ 实际问题

错误信息 "Username and password required" 表明 **GitHub Secrets 尚未在仓库中配置**。

工作流文件引用的 Secrets 变量为空值，导致 Docker login 失败。

## 🔐 修复步骤

### 步骤 1：访问 GitHub Secrets 配置页面

直接点击以下链接：

👉 https://github.com/janebin/telegram-115bot/settings/secrets/actions

或手动导航：
1. 访问仓库：https://github.com/janebin/telegram-115bot
2. 点击顶部 **Settings** 标签
3. 左侧菜单点击 **Secrets and variables** → **Actions**

### 步骤 2：添加 DOCKERHUB_USERNAME

1. 点击 **New repository secret** 按钮
2. 填写：
   - **Name**: `DOCKERHUB_USERNAME`
   - **Secret**: `janebin`
3. 点击 **Add secret** 保存

### 步骤 3：添加 DOCKERHUB_TOKEN

1. 再次点击 **New repository secret** 按钮
2. 填写：
   - **Name**: `DOCKERHUB_TOKEN`
   - **Secret**: `<YOUR_DOCKER_HUB_TOKEN>`
3. 点击 **Add secret** 保存

### 步骤 4：验证 Secrets 已添加

配置完成后，在 Actions secrets 页面应该看到：
- ✅ DOCKERHUB_USERNAME
- ✅ DOCKERHUB_TOKEN

> **注意**：GitHub 不会显示 Secret 的具体值，只显示名称和最后更新时间。

## 🚀 触发工作流验证修复

### 方法 1：手动触发（推荐）

1. 访问：https://github.com/janebin/telegram-115bot/actions
2. 选择 **Build and Push Docker Image to Docker Hub** 工作流
3. 点击 **Run workflow** 下拉按钮
4. 确认分支为 `main`
5. 点击绿色的 **Run workflow** 按钮

### 方法 2：推送代码触发

```bash
# 创建一个小的提交触发工作流
git commit --allow-empty -m "test: trigger docker workflow after secrets configuration"
git push origin main
```

## ✅ 验证修复成功

### 1. 检查 GitHub Actions 日志

在工作流运行页面，展开 **Login to Docker Hub** 步骤：

**修复前（失败）**：
```
Error: Username and password required
```

**修复后（成功）**：
```
✓ Login to Docker Hub
  Logging into Docker Hub...
  Login Succeeded
```

### 2. 确认后续步骤执行

修复成功后，以下步骤应该都能正常执行：
- ✅ Extract metadata (tags, labels)
- ✅ Build and push multi-arch image
- ✅ Image digest

### 3. 验证镜像已发布到 Docker Hub

访问：https://hub.docker.com/r/janebin/telegram-115bot

应该能看到：
- ✅ 仓库已创建
- ✅ 标签：`latest`, `main`
- ✅ 架构：`linux/amd64`, `linux/arm64`
- ✅ 最后推送时间为最近

### 4. 本地拉取测试

```bash
# 拉取镜像
docker pull janebin/telegram-115bot:latest

# 验证成功
docker images | grep telegram-115bot
```

## 📊 预期结果

修复完成后的完整工作流运行应该显示：

```
✅ Pre-build Validation
   ✅ Checkout code
   ✅ Set up Python
   ✅ Check Python syntax
   ✅ Validate Dockerfile
   ✅ Check required files

✅ Build and Push Docker Image
   ✅ Checkout code
   ✅ Set up QEMU
   ✅ Set up Docker Buildx
   ✅ Login to Docker Hub          ← 这一步现在应该成功
   ✅ Extract metadata
   ✅ Build and push multi-arch image
   ✅ Image digest

✅ Notification
   ✅ Check build status
   "✅ Docker image built and pushed successfully!"
```

## 🔒 安全提示

1. **Token 安全**：
   - Docker Hub Token 是敏感信息，仅存储在 GitHub Secrets 中
   - 不要在代码、文档或 commit 中包含实际 Token 值
   - GitHub Secrets 是加密存储的，只有工作流可以读取

2. **Token 权限**：
   - 当前 Token 权限：Read, Write, Delete
   - 只授予必要的权限
   - 定期轮换 Token

3. **Token 管理**：
   - Token 可以在 Docker Hub 中撤销和重新生成
   - 位置：https://hub.docker.com/settings/security

## 🛠️ 故障排查

### 如果 Login 步骤仍然失败

1. **检查 Secret 名称**：
   - 必须完全匹配：`DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN`
   - 区分大小写
   - 没有多余空格

2. **检查 Secret 值**：
   - Username: `janebin`（无多余空格）
   - Token: `<YOUR_DOCKER_HUB_TOKEN>`（完整复制）

3. **验证 Token 有效性**：
   ```bash
   # 在本地测试 Token 是否有效
   echo "<YOUR_DOCKER_HUB_TOKEN>" | docker login -u janebin --password-stdin
   ```

4. **重新创建 Secrets**：
   - 删除现有 Secrets
   - 重新添加，确保值正确

### 如果其他步骤失败

查看具体错误信息，常见问题：
- **Docker Hub 配额**：检查账号存储限制
- **网络问题**：GitHub Actions 网络连接到 Docker Hub
- **构建超时**：多架构构建可能需要 15-20 分钟

## 📝 修复检查清单

完成以下项目确认修复成功：

- [ ] GitHub Secrets 已配置
  - [ ] DOCKERHUB_USERNAME = janebin
  - [ ] DOCKERHUB_TOKEN = <YOUR_DOCKER_HUB_TOKEN>
- [ ] 工作流已重新运行
- [ ] Login to Docker Hub 步骤显示成功
- [ ] 镜像构建完成
- [ ] 镜像已推送到 Docker Hub
- [ ] Docker Hub 仓库页面可访问
- [ ] 本地可以拉取镜像

## 🎯 下一步

修复成功后：

1. **自动化已启用**：每次推送到 `main` 分支会自动构建和发布
2. **版本标签**：推送 `v*` 标签会创建版本化镜像
3. **多架构支持**：自动构建 AMD64 和 ARM64 架构

---

**文档创建时间**：2024
**状态**：待执行
**预计修复时间**：5 分钟（配置）+ 15-20 分钟（首次构建）
