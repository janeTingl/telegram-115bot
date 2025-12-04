# Release Notes

## v1.0.0 - Initial Release (2024-12-04)

### 🎉 首次发布

这是 Telegram 115 Bot 的首个正式版本，包含完整的功能集。

### ✨ 主要特性

#### 后端
- ✅ FastAPI 0.115 高性能 Web 框架
- ✅ Python 3.12 支持
- ✅ SQLite 数据库（配置和密钥存储）
- ✅ TOTP 双因素认证
- ✅ 115 云盘集成
- ✅ TMDB 元数据获取
- ✅ Emby 集成和 STRM 生成
- ✅ WebDAV 支持
- ✅ 离线下载管理
- ✅ 后台任务队列
- ✅ 日志记录和管理

#### 前端
- ✅ React 18 + TypeScript
- ✅ Vite 构建工具
- ✅ Tailwind CSS 样式
- ✅ Lucide React 图标
- ✅ 响应式设计
- ✅ 用户认证和会话管理
- ✅ 文件浏览器
- ✅ 媒体整理规则配置
- ✅ 日志查看器

#### 部署
- ✅ Docker 容器化
- ✅ 多架构支持（AMD64、ARM64）
- ✅ Docker Compose 编排
- ✅ Nginx 反向代理
- ✅ Supervisor 进程管理
- ✅ GitHub Actions 自动化发布

### 🐳 Docker Hub

**镜像地址**: [janebin/telegram-115bot](https://hub.docker.com/r/janebin/telegram-115bot)

```bash
docker pull janebin/telegram-115bot:latest
docker pull janebin/telegram-115bot:1.0.0
```

### 📦 支持架构

- `linux/amd64` - x86_64 架构（云服务器、PC）
- `linux/arm64` - ARM64 架构（Apple Silicon、树莓派等）

### 🚀 快速开始

```bash
# 使用 Docker Compose
docker-compose up -d

# 或直接运行
docker run -d \
  --name telegram-115bot \
  -p 12808:12808 \
  -v $(pwd)/backend/data:/app/data \
  -v $(pwd)/backend/uploads:/app/uploads \
  janebin/telegram-115bot:latest
```

访问: http://localhost:12808

默认账号:
- 用户名: `admin`
- 密码: `admin` (首次登录后请立即修改！)

### 📝 配置文件

- `data.db` - 配置数据库
- `secrets.db` - 密钥数据库
- `secure_key.bin` - 加密密钥
- `backend.log` - 应用日志

### 🔒 安全特性

- AES-GCM 加密存储敏感数据
- TOTP 双因素认证
- Session 管理
- 密码哈希存储
- 令牌桶限流

### 🛠️ 技术栈

**后端**: FastAPI, Python 3.12, SQLite, Uvicorn, Nginx, Supervisor  
**前端**: React 18, TypeScript, Vite, Tailwind CSS  
**部署**: Docker, Docker Compose, GitHub Actions

### 📚 文档

- [README.md](README.md) - 项目介绍和快速开始
- [DOCKER_PUBLISH.md](DOCKER_PUBLISH.md) - Docker 发布配置指南
- [BACKEND_IMPLEMENTATION.md](BACKEND_IMPLEMENTATION.md) - 后端实现文档

### 🙏 致谢

感谢所有开源项目和贡献者！

---

**完整更新日志和下载**: [GitHub Releases](https://github.com/janebin/telegram-115bot/releases/tag/v1.0.0)
