# GitHub Secrets 配置指南

本文档提供详细的 GitHub Secrets 配置步骤，用于 Docker Hub 自动化发布。

## 📋 前提条件

- GitHub 仓库: `janebin/telegram-115bot`
- Docker Hub 账号: `janebin`
- 仓库管理员权限

## 🔑 需要配置的 Secrets

### 1. DOCKERHUB_USERNAME
- **名称**: `DOCKERHUB_USERNAME`
- **值**: `janebin`
- **说明**: Docker Hub 用户名

### 2. DOCKERHUB_TOKEN
- **名称**: `DOCKERHUB_TOKEN`
- **值**: Docker Hub Access Token（在 Docker Hub 生成）
- **说明**: Docker Hub 访问令牌（**不是**密码！）

## 🔧 配置步骤

### 步骤 1: 生成 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 点击右上角头像 → **Account Settings**
3. 进入 **Security** 选项卡
4. 点击 **New Access Token**

![Docker Hub Security](https://docs.docker.com/docker-hub/images/access-tokens.png)

5. 填写 Token 信息：
   - **Description**: `github-actions-telegram-115bot`
   - **Access permissions**: 选择 **Read, Write, Delete** 或 **Read & Write**

6. 点击 **Generate**

7. **重要**: 立即复制生成的 Token（只显示一次！）
   ```
   示例格式: dckr_pat_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

8. 将 Token 保存到安全的地方（密码管理器）

### 步骤 2: 配置 GitHub Secrets

1. 打开 GitHub 仓库: https://github.com/janebin/telegram-115bot

2. 进入 **Settings** 标签页
   ![GitHub Settings](https://docs.github.com/assets/cb-21851/images/help/repository/repo-actions-settings.png)

3. 在左侧菜单找到 **Secrets and variables** → **Actions**

4. 点击 **New repository secret** 按钮

#### 添加 DOCKERHUB_USERNAME

5. 创建第一个 Secret:
   - **Name**: `DOCKERHUB_USERNAME`
   - **Secret**: `janebin`
   - 点击 **Add secret**

![Add Secret](https://docs.github.com/assets/cb-48007/images/help/settings/actions-secrets-add-secret.png)

#### 添加 DOCKERHUB_TOKEN

6. 再次点击 **New repository secret**

7. 创建第二个 Secret:
   - **Name**: `DOCKERHUB_TOKEN`
   - **Secret**: (粘贴在步骤 1 中生成的 Docker Hub Token)
   - 点击 **Add secret**

### 步骤 3: 验证配置

8. 返回到 **Secrets and variables** → **Actions** 页面

9. 确认看到两个 Secrets:
   - ✅ `DOCKERHUB_USERNAME`
   - ✅ `DOCKERHUB_TOKEN`

![Secrets List](https://docs.github.com/assets/cb-29167/images/help/settings/actions-secrets-list.png)

**注意**: GitHub 不会显示 Secret 的值，只显示名称。这是正常的安全设计。

## ✅ 配置验证清单

在继续之前，请确认：

- [ ] Docker Hub Access Token 已生成
- [ ] Token 权限包含 **Read & Write** 或更高
- [ ] GitHub Secret `DOCKERHUB_USERNAME` 已创建，值为 `janebin`
- [ ] GitHub Secret `DOCKERHUB_TOKEN` 已创建，值为实际的 Token
- [ ] 两个 Secrets 在 GitHub 仓库设置中可见

## 🧪 测试配置

配置完成后，可以通过以下方式测试：

### 方法 1: 手动触发工作流

1. 进入仓库的 **Actions** 标签页
2. 选择 "Build and Push Docker Image to Docker Hub" 工作流
3. 点击 **Run workflow** 按钮
4. 选择 `main` 分支
5. 点击 **Run workflow**

### 方法 2: 推送代码触发

```bash
# 创建测试提交
git add .
git commit -m "test: Verify Docker Hub auto-publish setup"
git push origin main
```

### 方法 3: 创建版本标签触发

```bash
# 创建并推送版本标签
git tag v1.0.0
git push origin v1.0.0
```

## 📊 监控工作流

1. 进入 **Actions** 标签页: https://github.com/janebin/telegram-115bot/actions

2. 查看最新的工作流运行

3. 检查各个步骤的状态:
   - ✅ **Pre-build Validation**: 验证通过
   - ✅ **Login to Docker Hub**: 登录成功
   - ✅ **Build and push multi-arch image**: 构建推送成功
   - ✅ **Notification**: 通知成功

## 🔍 故障排查

### 问题 1: "Login to Docker Hub" 步骤失败

**错误信息**: 
```
Error: Error response from daemon: Get https://registry-1.docker.io/v2/: unauthorized
```

**原因**: Docker Hub 凭证错误

**解决方法**:
1. 检查 `DOCKERHUB_USERNAME` 是否为 `janebin`（区分大小写）
2. 检查 `DOCKERHUB_TOKEN` 是否为正确的 Token（不是密码）
3. 确认 Token 没有过期
4. 重新生成 Token 并更新 GitHub Secret

### 问题 2: Secret 值错误需要更新

**步骤**:
1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 找到需要更新的 Secret
3. 点击 Secret 名称旁的 **Update** 按钮
4. 输入新的值
5. 点击 **Update secret**

### 问题 3: 无法访问 Settings 页面

**原因**: 没有仓库管理员权限

**解决方法**:
- 联系仓库所有者授予权限
- 或请仓库所有者配置 Secrets

## 📝 安全最佳实践

### ✅ 推荐做法

- ✅ 使用 Access Token 而不是密码
- ✅ 为不同项目创建不同的 Token
- ✅ 定期轮换 Token（如每 90 天）
- ✅ 使用最小权限原则（只授予必要权限）
- ✅ 在密码管理器中安全存储 Token

### ❌ 避免

- ❌ 不要在代码中硬编码凭证
- ❌ 不要将 Token 提交到 Git
- ❌ 不要与他人共享 Token
- ❌ 不要在日志或错误信息中暴露 Token

## 🔄 Token 轮换

建议定期轮换 Access Token：

1. 在 Docker Hub 生成新的 Token
2. 在 GitHub 更新 `DOCKERHUB_TOKEN` Secret
3. 在 Docker Hub 撤销旧的 Token
4. 测试新 Token 是否工作正常

## 📚 相关文档

- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Docker Hub API](https://docs.docker.com/docker-hub/api/latest/)

## ✅ 配置完成检查表

完成以下所有项后，配置即完成：

- [ ] Docker Hub Access Token 已生成并保存
- [ ] `DOCKERHUB_USERNAME` Secret 已在 GitHub 中配置
- [ ] `DOCKERHUB_TOKEN` Secret 已在 GitHub 中配置
- [ ] 工作流文件 `.github/workflows/docker-publish.yml` 存在
- [ ] 已测试触发工作流（手动或推送代码）
- [ ] 工作流运行成功（所有步骤为绿色 ✅）
- [ ] 镜像已出现在 Docker Hub: https://hub.docker.com/r/janebin/telegram-115bot
- [ ] 可以成功拉取镜像: `docker pull janebin/telegram-115bot:latest`

---

**配置完成后，你的 Docker Hub 自动化发布就绪！** 🎉

每次推送到 `main` 分支或创建版本标签，都会自动构建并发布新的 Docker 镜像。
