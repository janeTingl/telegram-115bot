# Docker Hub Token 信息

## 🔐 关于 Docker Hub Token

为了安全考虑，实际的 Docker Hub Token 已从文档中移除。

### 如何获取 Token

#### 方法 1：使用提供的 Token（如果已收到）

如果你已经收到了 Docker Hub Token（通过安全渠道），请直接使用该 Token。

Token 格式示例：
```
dckr_pat_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 方法 2：生成新的 Token

1. 访问 Docker Hub：https://hub.docker.com
2. 登录你的账号（janebin）
3. 点击右上角头像 → Account Settings
4. 左侧菜单选择 "Security"
5. 点击 "New Access Token"
6. 填写信息：
   - Description: `GitHub Actions - telegram-115bot`
   - Access permissions: `Read, Write, Delete`
7. 点击 "Generate"
8. **立即复制生成的 Token**（只显示一次！）

### 配置到 GitHub Secrets

获得 Token 后，访问：
```
https://github.com/janebin/telegram-115bot/settings/secrets/actions
```

添加 Secret：
- Name: `DOCKERHUB_TOKEN`
- Value: `<粘贴你的实际 Token>`

## ⚠️ 安全提示

1. **永远不要**在公开代码中提交 Token
2. **永远不要**在文档中明文记录完整 Token
3. Token 只能在以下地方使用：
   - GitHub Secrets（推荐）
   - 本地环境变量（临时使用）
   - 安全的密码管理器
4. 如果 Token 泄露，立即在 Docker Hub 上撤销并生成新的

## 📚 相关文档

配置步骤详见：
- [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

---

**保护好你的 Token！** 🔒
