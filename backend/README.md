# Telegram 115 Bot - Backend

FastAPI 0.115 后端服务，提供完整的管理面板 API 支持。

## 技术栈

- **FastAPI 0.115**: 高性能异步 Web 框架
- **Python 3.12**: 最新稳定版 Python
- **SQLite**: 配置和密钥存储
- **AES-GCM**: 敏感数据加密
- **TOTP**: 双因素认证支持

## 核心功能

### 1. 认证系统 (`router/auth.py`)
- ✅ 密码登录 (`POST /api/auth/login`)
- ✅ 修改密码 (`POST /api/auth/password`)
- ✅ 2FA 密钥生成 (`GET /api/auth/2fa/generate`)
- ✅ 2FA 验证 (`POST /api/auth/2fa/verify`)

### 2. 配置管理 (`router/config.py`)
- ✅ 加载全局配置 (`GET /api/config/load`)
- ✅ 保存全局配置 (`POST /api/config/save_all`)
- ✅ 保存代理配置 (`POST /api/config/proxy`)

### 3. 文件管理 (`router/file.py`)
- ✅ 115 云盘文件列表 (`GET /api/file/list`)
- ✅ 文件移动 (`POST /api/file/move`)
- ✅ 文件重命名 (`POST /api/file/rename`)
- ✅ 触发整理任务 (`POST /api/file/organize/start`)
- ✅ 通知 Emby 刷新 (`POST /api/file/notify_emby`)

### 4. TMDB 集成 (`router/tmdb.py`)
- ✅ 搜索影视 (`POST /api/tmdb/search`)
- ✅ 获取详情 (`POST /api/tmdb/details`)
- ✅ AI 辅助识别 (`POST /api/tmdb/identify`)

### 5. Emby 集成 (`router/emby.py`)
- ✅ 刷新媒体库 (`POST /api/emby/refresh_and_probe`)

### 6. 离线下载 (`router/offline.py`)
- ✅ 创建离线任务 (`POST /api/offline/create`)
- ✅ 查询任务状态 (`GET /api/offline/status`)

### 7. 通知系统 (`router/notify.py`)
- ✅ 115 云盘事件通知 (`POST /api/notify/115_event`)

## 核心模块

### `core/db.py`
SQLite 数据库封装，提供配置和密钥的持久化存储：
- `get_config()` / `set_config()`: 配置读写
- `get_secret()` / `set_secret()`: 加密密钥读写
- `get_all_config()` / `set_all_config()`: 批量配置操作

### `core/utils.py`
工具函数库：
- `generate_base32_secret()`: 生成 2FA 密钥
- `verify_totp()`: 验证 TOTP 验证码

### `core/organizer.py`
网盘整理任务管理：
- `start_organize_job()`: 启动异步整理任务

### `core/encrypt.py`
AES-GCM 加密封装：
- `encrypt_str()` / `decrypt_str()`: 字符串加密/解密

### `core/p115_client.py`
115 云盘客户端适配器，提供统一接口封装

### `core/logger.py`
日志管理系统，支持滚动日志（最多 1000 条）

### `core/qps_limiter.py`
QPS 限流器，基于令牌桶算法

### `core/tmdb_client.py`
TMDB API 客户端封装

## 安全特性

1. **敏感数据加密**: 所有密钥和 Cookie 使用 AES-GCM 加密存储
2. **2FA 支持**: 可选的双因素认证
3. **QPS 限流**: 防止 API 滥用
4. **日志脱敏**: 日志中不包含敏感信息

## 数据存储

- `data.db`: 应用配置数据库
- `secrets.db`: 加密的密钥数据库
- `secure_key.bin`: AES 加密主密钥（自动生成）

## 启动方式

```bash
cd backend
python3 main.py
```

默认监听 `0.0.0.0:8000`

## 环境变量

- `DATA_DIR`: 数据目录路径（默认: `../data`）
- `DB_KEY`: 数据库加密主密钥（可选，用于额外的加密层）

## API 规范

所有 API 响应遵循统一格式：

```json
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```

- `code`: 0 表示成功，非 0 表示错误
- `msg`: 消息文本
- `data`: 响应数据（可选）

## 开发指南

### 添加新路由

1. 在 `router/` 目录下创建新的路由文件
2. 定义 `APIRouter` 实例
3. 在 `main.py` 中使用 `_include_router()` 加载

### 添加新配置

1. 使用 `set_config(key, value)` 保存
2. 使用 `get_config(key, default)` 读取
3. 敏感数据使用 `set_secret()` / `get_secret()`

## 测试

运行路由测试：

```bash
python3 test_routes.py
```

## 部署

推荐使用 Docker 部署，详见项目根目录的 `Dockerfile` 和 `docker-compose.yml`。
