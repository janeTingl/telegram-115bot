# Telegram 115 Bot

[![Docker Build](https://github.com/YOUR_USERNAME/telegram-115bot/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/YOUR_USERNAME/telegram-115bot/actions/workflows/docker-publish.yml)
[![Docker Hub](https://img.shields.io/docker/pulls/YOUR_USERNAME/telegram-115bot.svg)](https://hub.docker.com/r/YOUR_USERNAME/telegram-115bot)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 全栈 Telegram 115 云盘管理机器人，带有完整的 Web 管理面板

## 📖 项目简介

Telegram 115 Bot 是一个功能强大的全栈应用，提供：

- 🤖 **Telegram Bot 集成**：通过 Telegram 机器人管理 115 云盘
- 🖥️ **Web 管理面板**：React + TypeScript 构建的现代化管理界面
- 🔐 **安全认证**：支持 TOTP 双因素认证
- 📁 **文件管理**：浏览、移动、重命名 115 云盘文件
- 🎬 **媒体整理**：自动化媒体文件整理和元数据获取（TMDB）
- 📺 **Emby 集成**：生成 STRM 文件，直接串流播放
- 🌐 **WebDAV 支持**：通过 WebDAV 访问云盘
- ⬇️ **离线下载**：支持离线下载任务管理

## 🏗️ 技术栈

### 后端
- **FastAPI 0.115**：高性能 Python Web 框架
- **Python 3.12**：最新 Python 版本
- **SQLite**：配置和密钥存储
- **Uvicorn**：ASGI 服务器
- **Nginx**：反向代理
- **Supervisor**：进程管理

### 前端
- **React 18**：现代化前端框架
- **TypeScript**：类型安全
- **Vite**：快速构建工具
- **Tailwind CSS**：实用优先的 CSS 框架
- **Lucide React**：精美图标库

### 部署
- **Docker**：容器化部署
- **Docker Compose**：编排管理
- **Multi-arch**：支持 AMD64 和 ARM64 架构

## 🚀 快速开始

### 使用 Docker（推荐）

1. 拉取镜像：

```bash
docker pull YOUR_USERNAME/telegram-115bot:latest
```

2. 使用 Docker Compose 运行：

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/telegram-115bot.git
cd telegram-115bot

# 启动服务
docker-compose up -d
```

3. 访问管理面板：

打开浏览器访问 `http://localhost:12808`

默认管理员账号：
- 用户名：`admin`
- 密码：`admin`（首次登录后请立即修改！）

### 手动构建

```bash
# 构建镜像
docker build -t telegram-115bot .

# 运行容器
docker run -d \
  --name telegram-115bot \
  -p 12808:12808 \
  -v $(pwd)/backend/data:/app/data \
  -v $(pwd)/backend/uploads:/app/uploads \
  telegram-115bot
```

## 📦 Docker Hub 自动发布

本项目已配置 GitHub Actions 自动构建和发布 Docker 镜像。

详细配置说明请查看：[DOCKER_PUBLISH.md](DOCKER_PUBLISH.md)

### 镜像标签

- `latest`：最新稳定版本（主分支）
- `v1.0.0`、`v1.2.3`：语义化版本标签
- `main`/`master`：主分支最新构建

### 支持架构

- `linux/amd64`：x86_64 架构（云服务器、个人电脑）
- `linux/arm64`：ARM64 架构（Apple Silicon、树莓派等）

## ⚙️ 配置

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | Web 服务端口 | `12808` |
| `PYTHONPATH` | Python 模块路径 | `/app` |

### 数据持久化

建议挂载以下目录：

```yaml
volumes:
  - ./backend/config.json:/app/config.json    # 配置文件
  - ./backend/data:/app/data                  # 数据库和密钥
  - ./backend/uploads:/app/uploads            # 上传文件
  - ./backend/backend.log:/app/backend.log    # 日志文件
```

## 🔧 功能特性

### 1. 用户认证
- 登录/登出
- TOTP 双因素认证
- 密码修改
- Session 管理

### 2. 云盘管理
- 文件浏览和搜索
- 文件移动和重命名
- 批量操作
- 文件夹管理

### 3. 离线下载
- 添加离线下载任务
- 任务状态监控
- 下载进度跟踪

### 4. 媒体整理
- 自动识别电影/电视剧
- TMDB 元数据获取
- 自定义整理规则
- 文件自动归类

### 5. Emby 集成
- 生成 STRM 文件
- 媒体库刷新
- 直接串流播放

### 6. 系统管理
- 日志查看
- 系统配置
- Bot 设置
- WebDAV 配置

## 📚 文档

- [Docker 发布配置指南](DOCKER_PUBLISH.md)
- [后端实现文档](BACKEND_IMPLEMENTATION.md)

## 🛠️ 开发

### 本地开发

1. 安装依赖：

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

2. 启动开发服务器：

```bash
# 后端（在 backend 目录）
uvicorn main:app --reload --port 8000

# 前端（在 frontend 目录）
npm run dev
```

### 构建生产版本

```bash
# 前端构建
cd frontend
npm run build

# 复制到项目根目录
cp -r dist ../

# Docker 构建
cd ..
docker build -t telegram-115bot .
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [115 云盘](https://115.com/)
- [TMDB](https://www.themoviedb.org/)
- [Emby](https://emby.media/)

---

**注意**：使用前请将 `YOUR_USERNAME` 替换为你的 GitHub/Docker Hub 用户名
