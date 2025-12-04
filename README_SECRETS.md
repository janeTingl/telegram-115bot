# 📝 Docker Hub Token 说明

## 🔐 Token 存储位置

Docker Hub Access Token 存储在本地文件 `.dockerhub-token` 中，该文件已被添加到 `.gitignore`，不会被提交到 Git 仓库。

## 📁 文件结构

```
telegram-115bot/
├── .dockerhub-token          # Docker Hub Token (本地，不提交)
├── .gitignore                # 包含 .dockerhub-token 规则
├── configure-secrets.sh      # 配置辅助脚本（会读取此文件）
└── ...
```

## 🔍 如何使用

### 查看 Token

```bash
cat .dockerhub-token
```

### 验证 Token 有效性

```bash
./configure-secrets.sh
```

该脚本会：
1. 读取 `.dockerhub-token` 文件
2. 验证 Token 是否有效
3. 提供配置 GitHub Secrets 的详细指导

## ⚠️ 安全提示

1. **不要提交到 Git**：`.dockerhub-token` 文件已在 `.gitignore` 中，确保不会意外提交
2. **不要分享**：Token 具有 Docker Hub 账号的完整权限，不要分享给他人
3. **定期轮换**：建议定期更新 Token 以提高安全性
4. **最小权限原则**：Token 应仅具有构建和推送镜像所需的权限（Read, Write, Delete）

## 🔄 Token 更新

如需更新 Docker Hub Token：

### 步骤 1：生成新 Token

1. 访问：https://hub.docker.com/settings/security
2. 点击 "New Access Token"
3. 权限选择：
   - ✅ Read
   - ✅ Write  
   - ✅ Delete
4. 复制新生成的 Token

### 步骤 2：更新本地文件

```bash
echo "dckr_pat_YOUR_NEW_TOKEN_HERE" > .dockerhub-token
```

### 步骤 3：更新 GitHub Secrets

1. 访问：https://github.com/janeTingl/telegram-115bot/settings/secrets/actions
2. 找到 `DOCKERHUB_TOKEN`
3. 点击 "Update" 按钮
4. 粘贴新 Token
5. 点击 "Update secret"

### 步骤 4：验证

```bash
# 测试本地 Token
./configure-secrets.sh

# 触发 GitHub Actions 工作流测试
git push origin main
```

## 📚 相关文档

- **配置指南**：`SECRETS_CONFIGURATION_REQUIRED.md`
- **快速开始**：`START_HERE.md`
- **完整行动计划**：`DOCKER_HUB_PUBLISH_READY.md`

## ❓ 常见问题

### Q: 为什么不直接在文档中写 Token？

**A**: 出于安全考虑，Token 不应该提交到 Git 仓库。GitHub 有推送保护功能，会阻止包含敏感信息的提交。将 Token 存储在本地文件中可以：
- ✅ 保持 Git 历史干净
- ✅ 避免 Token 泄露
- ✅ 通过 GitHub 推送保护检查

### Q: 如果 .dockerhub-token 文件丢失怎么办？

**A**: 从 Docker Hub 重新生成一个新的 Access Token：
1. 访问 https://hub.docker.com/settings/security
2. 删除旧 Token（如果还在）
3. 生成新 Token
4. 保存到 `.dockerhub-token` 文件
5. 更新 GitHub Secrets

### Q: 可以用密码代替 Token 吗？

**A**: 不推荐。Docker Hub 推荐使用 Access Token 而不是密码，因为：
- Token 可以随时撤销
- Token 可以设置特定权限
- Token 更安全（不暴露主密码）

---

**最后更新**: 2024-12-04  
**文档版本**: 1.0
