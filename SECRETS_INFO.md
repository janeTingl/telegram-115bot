# 🔐 GitHub Secrets 配置信息

## 重要安全提示

出于安全考虑，实际的 Docker Hub Token 不能直接存储在代码仓库中。GitHub 的推送保护已检测并阻止了包含敏感信息的提交。

## 📋 需要配置的 Secrets

访问：https://github.com/janebin/telegram-115bot/settings/secrets/actions

添加以下两个 Secrets：

### 1. DOCKERHUB_USERNAME
```
Name: DOCKERHUB_USERNAME
Value: janebin
```

### 2. DOCKERHUB_TOKEN
```
Name: DOCKERHUB_TOKEN
Value: <请使用实际的 Docker Hub Token>
```

## 🔑 获取 Docker Hub Token

### 方法 1：使用现有 Token

如果你已经有 Docker Hub Personal Access Token，直接使用即可。

Token 格式应该是：`dckr_pat_` 开头的字符串

### 方法 2：生成新 Token

1. 登录 Docker Hub：https://hub.docker.com/
2. 点击右上角头像 → **Account Settings**
3. 选择 **Security** 标签
4. 点击 **New Access Token**
5. 填写信息：
   - Token Description: `GitHub Actions CI/CD`
   - Access Permissions: `Read, Write, Delete`
6. 点击 **Generate**
7. **立即复制生成的 Token**（只显示一次！）

## 📝 Token 信息记录

**Token 位置**：请从以下位置获取实际的 Token：

1. ✅ 如果是项目维护者，查看之前的安全记录或联系管理员
2. ✅ 如果是首次配置，请按照上述方法生成新 Token
3. ✅ Token 生成后，立即添加到 GitHub Secrets，不要存储在其他地方

## 🛡️ 安全最佳实践

### ✅ 正确做法
- ✅ Token 只存储在 GitHub Secrets 中
- ✅ 使用 Personal Access Token 而非密码
- ✅ 为 Token 设置描述性名称（如 "GitHub Actions"）
- ✅ 只授予必要的权限
- ✅ 定期轮换 Token

### ❌ 避免的做法
- ❌ 不要在代码中硬编码 Token
- ❌ 不要在文档中包含实际 Token
- ❌ 不要通过邮件或消息发送 Token
- ❌ 不要使用 Docker Hub 密码代替 Token
- ❌ 不要将 Token 存储在本地文件中

## 🔄 Token 泄露应对

如果 Token 意外泄露：

1. **立即撤销**：访问 https://hub.docker.com/settings/security
2. **生成新 Token**：按照上述步骤重新生成
3. **更新 GitHub Secrets**：用新 Token 替换旧值
4. **验证工作流**：确保新 Token 能正常工作

## 📖 相关文档

Token 配置完成后，参考以下文档完成修复：

- [START_HERE_FIX.md](START_HERE_FIX.md) - 开始修复
- [QUICK_FIX.md](QUICK_FIX.md) - 快速修复步骤
- [DOCKER_HUB_SECRETS_FIX.md](DOCKER_HUB_SECRETS_FIX.md) - 详细配置指南
- [FIX_CHECKLIST.md](FIX_CHECKLIST.md) - 检查清单

## ⚠️ 重要提醒

文档中所有 `<YOUR_DOCKER_HUB_TOKEN>` 占位符都需要替换为实际的 Docker Hub Personal Access Token。

**Token 格式示例**：`dckr_pat_xxxxxxxxxxxxxxxxxxxxx`（实际 Token 约 30-40 个字符）

---

**创建时间**：2024  
**目的**：防止敏感信息泄露，提供安全配置指南
