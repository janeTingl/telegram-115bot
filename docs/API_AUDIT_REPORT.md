# Telegram-115Bot 三层 API 完整性审计报告

**生成时间**: 2024-12-05  
**审计范围**: Backend API → Frontend Services → UI Components

---

## 执行摘要

### 审计统计

| 层级 | 已实现 | 缺失 | 状态 |
|------|--------|------|------|
| **后端 API** | 24 个端点 | 15+ 个预期端点 | ⚠️ 部分完整 |
| **前端服务** | 3 个服务文件 | 5+ 个缺失服务 | ⚠️ 严重不足 |
| **UI 层** | 9 个视图 | 部分直接调用 API | ⚠️ 架构违规 |

### 关键发现

🔴 **严重问题**:
1. 前端缺少 5 个核心服务模块（file, offline, strm, tmdb, emby）
2. SettingsView.tsx 直接调用 fetch()，违反服务层架构
3. 后端 health.py 列出的预期端点与实际实现严重不匹配
4. 配置端点命名不一致（/api/config/load vs /api/config/get）

🟡 **中等问题**:
5. 文件操作、离线下载、STRM 生成等核心功能缺少前端服务封装
6. 多个后端端点无前端调用
7. UI 组件可能直接调用后端 API

---

## 第一部分：后端 API 层审计

### 1.1 已实现的后端端点

#### 认证模块 (router/auth.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| POST | `/api/auth/login` | 用户登录 | ✅ auth.ts |
| POST | `/api/auth/password` | 修改密码 | ✅ config.ts |
| GET | `/api/auth/2fa/generate` | 生成 2FA 密钥 | ✅ config.ts |
| POST | `/api/auth/2fa/verify` | 验证 2FA | ✅ auth.ts, config.ts |

#### 配置模块 (router/config.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| GET | `/api/config/load` | 加载配置 | ✅ config.ts |
| POST | `/api/config/save_all` | 保存全部配置 | ✅ config.ts |
| POST | `/api/config/proxy` | 保存代理配置 | ✅ config.ts |

#### 文件模块 (router/file.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| GET | `/api/file/list` | 列出文件 | ❌ 无服务 |
| POST | `/api/file/move` | 移动文件 | ❌ 无服务 |
| POST | `/api/file/rename` | 重命名文件 | ❌ 无服务 |
| POST | `/api/file/notify_emby` | 通知 Emby | ❌ 无服务 |
| POST | `/api/file/organize/start` | 启动整理任务 | ✅ task.ts |

#### 离线下载模块 (router/offline.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| POST | `/api/offline/create` | 创建离线任务 | ❌ 无服务 |
| GET | `/api/offline/status` | 查询任务状态 | ❌ 无服务 |

#### TMDB 模块 (router/tmdb.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| POST | `/api/tmdb/search` | 搜索影视 | ❌ 无服务 |
| POST | `/api/tmdb/details` | 获取详情 | ❌ 无服务 |
| POST | `/api/tmdb/identify` | AI 识别 | ❌ 无服务 |

#### Emby 模块 (router/emby.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| POST | `/api/emby/refresh_and_probe` | 刷新并探测 | ❌ 无服务 |

#### 通知模块 (router/notify.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| POST | `/api/notify/115_event` | 115 事件通知 | ❌ 无服务 |

#### 健康检查模块 (router/health.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| GET | `/api/health/report` | 健康报告 | ❌ 无服务 |

#### 主程序附加端点 (main.py)
| 方法 | 路径 | 描述 | 前端服务 |
|------|------|------|----------|
| GET | `/healthz` | 健康检查 | ❌ 无服务 |
| GET | `/api/status` | 运行状态 | ❌ 无服务 |
| GET | `/api/version` | 版本信息 | ❌ 无服务 |
| GET | `/api/config/get` | 获取配置（⚠️ 与 config/load 重复） | ❌ 无服务 |
| POST | `/api/config/update` | 更新配置（⚠️ 与 config/save_all 重复） | ❌ 无服务 |
| POST | `/api/2fa/verify` | 2FA 验证（⚠️ 与 auth/2fa/verify 重复） | ✅ auth.ts |
| GET | `/api/secret/get` | 获取密钥 | ❌ 无服务 |
| POST | `/api/files/upload` | 上传文件 | ❌ 无服务 |
| GET | `/api/files/list` | 文件列表（⚠️ 与 file/list 路径不同） | ❌ 无服务 |

### 1.2 预期但缺失的后端端点

根据 `router/health.py` 中的 `EXPECTED_ENDPOINTS` 列表，以下端点被期望但未实现：

| 方法 | 路径 | 描述 | 状态 |
|------|------|------|------|
| POST | `/api/auth/logout` | 用户登出 | ❌ 未实现 |
| GET | `/api/auth/verify` | 验证认证状态 | ❌ 未实现 |
| GET | `/api/config/all` | 获取所有配置 | ⚠️ 路径不同（实际: config/load） |
| POST | `/api/config/set` | 设置配置 | ⚠️ 路径不同（实际: config/update） |
| GET | `/api/config/{key}` | 获取单个配置 | ❌ 未实现 |
| DELETE | `/api/config/{key}` | 删除配置 | ❌ 未实现 |
| POST | `/api/file/upload` | 上传文件 | ⚠️ 路径不同（实际: files/upload） |
| POST | `/api/file/delete` | 删除文件 | ❌ 未实现 |
| POST | `/api/offline/add` | 添加离线任务 | ⚠️ 路径不同（实际: offline/create） |
| GET | `/api/offline/list` | 离线任务列表 | ❌ 未实现 |
| POST | `/api/offline/start` | 启动任务 | ❌ 未实现 |
| POST | `/api/offline/cancel` | 取消任务 | ❌ 未实现 |
| GET | `/api/tmdb/search` | TMDB 搜索 | ⚠️ 方法不同（实际: POST） |
| GET | `/api/tmdb/details/{id}` | TMDB 详情 | ⚠️ 方法不同（实际: POST） |
| GET | `/api/tmdb/images` | TMDB 图片 | ❌ 未实现 |
| POST | `/api/emby/refresh` | 刷新媒体库 | ⚠️ 路径不同（实际: emby/refresh_and_probe） |
| GET | `/api/emby/status` | Emby 状态 | ❌ 未实现 |
| POST | `/api/emby/scan` | 扫描媒体库 | ❌ 未实现 |
| POST | `/api/strm/generate` | 生成 STRM | ❌ 未实现 |
| GET | `/api/strm/list` | STRM 列表 | ❌ 未实现 |
| POST | `/api/notification/send` | 发送通知 | ❌ 未实现 |
| GET | `/api/notification/logs` | 通知日志 | ❌ 未实现 |

### 1.3 后端问题总结

🔴 **严重问题**:
1. **路径不一致**: 多个端点实际路径与预期文档不匹配
2. **方法不一致**: TMDB 搜索/详情使用 POST 而非 RESTful 标准的 GET
3. **重复端点**: main.py 和 router 中存在功能重复的端点
4. **缺失端点**: 15+ 个预期端点未实现

🟡 **中等问题**:
5. **命名混乱**: `/api/file/list` vs `/api/files/list`，`/api/config/load` vs `/api/config/get`
6. **功能缺失**: STRM 生成、通知管理、离线任务管理缺少完整接口

---

## 第二部分：前端服务层审计

### 2.1 已实现的前端服务

#### services/auth.ts
| 函数 | 后端端点 | 状态 |
|------|----------|------|
| `login(username, pass)` | POST /api/auth/login | ✅ 正常 |
| `verify2FA(code)` | POST /api/2fa/verify | ✅ 正常 |
| `checkAuth()` | 本地存储 | ✅ 正常 |
| `logout()` | 本地存储 | ⚠️ 无后端对应 |
| `getFailedAttempts()` | 本地存储 | ✅ 正常 |
| `isLocked()` | 本地存储 | ✅ 正常 |

#### services/config.ts
| 函数 | 后端端点 | 状态 |
|------|----------|------|
| `loadGlobalConfig()` | GET /api/config/load | ✅ 正常 |
| `saveGlobalConfig(config)` | POST /api/config/save_all | ✅ 正常 |
| `saveAdminPassword(newPassword)` | POST /api/auth/password | ✅ 正常 |
| `saveProxyConfig(proxyConfig)` | POST /api/config/proxy | ✅ 正常 |
| `generate2FASecret()` | GET /api/auth/2fa/generate | ✅ 正常 |
| `verifyAndSave2FA(secret, code)` | POST /api/auth/2fa/verify | ✅ 正常 |

#### services/task.ts
| 函数 | 后端端点 | 状态 |
|------|----------|------|
| `startOrganizeTask()` | POST /api/file/organize/start | ✅ 正常 |

#### services/api.ts
| 函数 | 描述 | 状态 |
|------|------|------|
| `api.get(url)` | 通用 GET 包装器 | ✅ 正常 |
| `api.post(url, data)` | 通用 POST 包装器 | ✅ 正常 |

#### services/mockConfig.ts
| 函数 | 描述 | 状态 |
|------|------|------|
| `loadConfig()` | 加载本地配置 | ✅ 正常 |
| `saveConfig(config)` | 保存本地配置 | ✅ 正常 |
| `DEFAULT_MOVIE_RULES` | 默认电影规则 | ✅ 正常 |
| `DEFAULT_TV_RULES` | 默认电视规则 | ✅ 正常 |

### 2.2 缺失的前端服务

以下关键服务模块完全缺失：

#### ❌ services/file.ts (文件管理服务)
应包含的函数：
- `listFiles(path: string)` → GET /api/file/list
- `moveFile(src: string, dst: string)` → POST /api/file/move
- `renameFile(path: string, newName: string)` → POST /api/file/rename
- `deleteFile(path: string)` → POST /api/file/delete
- `uploadFile(file: File)` → POST /api/files/upload
- `notifyEmby(path: string)` → POST /api/file/notify_emby

#### ❌ services/offline.ts (离线下载服务)
应包含的函数：
- `createOfflineTask(url: string, targetFolder: string, notifyTg: boolean)` → POST /api/offline/create
- `getOfflineStatus(taskId: string)` → GET /api/offline/status
- `listOfflineTasks()` → GET /api/offline/list (后端缺失)
- `cancelOfflineTask(taskId: string)` → POST /api/offline/cancel (后端缺失)

#### ❌ services/strm.ts (STRM 生成服务)
应包含的函数：
- `generateStrm(files: string[], targetDir: string, template: string)` → POST /api/strm/generate (后端缺失)
- `listStrm()` → GET /api/strm/list (后端缺失)
- `deleteStrm(strmId: string)` → DELETE /api/strm/{id} (后端缺失)

#### ❌ services/tmdb.ts (TMDB 服务)
应包含的函数：
- `searchMedia(query: string, type: string, year?: number)` → POST /api/tmdb/search
- `getMediaDetails(id: number, type: string)` → POST /api/tmdb/details
- `identifyMedia(name: string, type: string)` → POST /api/tmdb/identify

#### ❌ services/emby.ts (Emby 服务)
应包含的函数：
- `refreshLibrary(itemId?: string)` → POST /api/emby/refresh_and_probe
- `getEmbyStatus()` → GET /api/emby/status (后端缺失)
- `scanLibrary()` → POST /api/emby/scan (后端缺失)

#### ❌ services/health.ts (健康检查服务)
应包含的函数：
- `getHealthReport()` → GET /api/health/report
- `getVersion()` → GET /api/version
- `getStatus()` → GET /api/status

#### ❌ services/logs.ts (日志服务)
应包含的函数：
- `getLogs(filters?)` → GET /api/logs (后端缺失)
- `clearLogs()` → DELETE /api/logs (后端缺失)

### 2.3 服务层问题总结

🔴 **严重问题**:
1. **缺失 6 个核心服务模块**: file, offline, strm, tmdb, emby, health
2. **架构违规**: 发现 UI 层直接调用 fetch() 而非使用服务层

🟡 **中等问题**:
3. **服务覆盖率低**: 仅 24 个后端端点中的 9 个有服务封装（37.5%）
4. **错误处理不统一**: 不同服务的错误处理方式不一致

---

## 第三部分：前端 UI 层审计

### 3.1 已实现的视图和组件

#### 视图 (views/)
| 视图 | 主要功能 | 使用的服务 | 架构合规性 |
|------|----------|------------|-----------|
| **LoginView.tsx** | 登录/2FA | auth.ts | ✅ 合规 |
| **UserCenterView.tsx** | 用户中心 | 未检查 | ❓ 待审计 |
| **BotSettingsView.tsx** | Bot 配置 | 未检查 | ❓ 待审计 |
| **CloudOrganizeView.tsx** | 网盘整理 | config.ts, task.ts | ✅ 合规 |
| **SettingsView.tsx** | 系统设置 | ❌ 直接 fetch() | 🔴 违规 |
| **EmbyView.tsx** | Emby 管理 | 未检查 | ❓ 待审计 |
| **StrmView.tsx** | STRM 管理 | 未检查 | ❓ 待审计 |
| **LogsView.tsx** | 日志查看 | 未检查 | ❓ 待审计 |
| **DashboardView.tsx** | 仪表板 | 未检查 | ❓ 待审计 |

#### 组件 (components/)
| 组件 | 主要功能 | 使用的服务 | 架构合规性 |
|------|----------|------------|-----------|
| **FileSelector.tsx** | 文件选择器 | ❓ 可能直接调用 /api/file/list | ⚠️ 待审计 |
| **SensitiveInput.tsx** | 敏感信息输入 | 无 | ✅ 纯组件 |
| **TwoFactorAuth.tsx** | 2FA 组件 | auth.ts | ✅ 合规 |
| **Sidebar.tsx** | 侧边栏 | 无 | ✅ 纯组件 |
| **Logo.tsx** | Logo | 无 | ✅ 纯组件 |
| **CommandCard.tsx** | 命令卡片 | 无 | ✅ 纯组件 |
| **Tooltip.tsx** | 提示框 | 无 | ✅ 纯组件 |

### 3.2 UI 层问题总结

🔴 **严重问题**:
1. **SettingsView.tsx 直接调用 fetch()**:
   ```typescript
   const res = await fetch('/api/config');  // 行 49
   const res = await fetch('/api/config', { method: 'POST', ... });  // 行 65
   const res = await fetch('/api/115/qrcode');  // 行 88
   ```
   这违反了三层架构原则，应该通过服务层封装。

2. **FileSelector.tsx 可能直接调用 API**:
   需要进一步审计该组件是否直接调用 `/api/file/list`。

🟡 **中等问题**:
3. **缺少服务层支持**: 多个视图（EmbyView, StrmView, LogsView）可能因为缺少服务层而直接调用 API
4. **错误处理不统一**: 不同视图的错误提示方式不一致（toast vs alert vs console.error）

---

## 第四部分：三层对接完整性审计

### 4.1 对接矩阵

| 功能模块 | 后端 API | 前端服务 | UI 层 | 状态 |
|----------|----------|----------|-------|------|
| **用户登录** | ✅ | ✅ | ✅ | ✅ 完整 |
| **2FA 认证** | ✅ | ✅ | ✅ | ✅ 完整 |
| **配置管理** | ✅ | ✅ | ⚠️ | ⚠️ UI 违规 |
| **网盘整理** | ✅ | ✅ | ✅ | ✅ 完整 |
| **文件管理** | ⚠️ | ❌ | ❓ | ❌ 不完整 |
| **离线下载** | ⚠️ | ❌ | ❓ | ❌ 不完整 |
| **STRM 生成** | ❌ | ❌ | ❓ | ❌ 缺失 |
| **TMDB 搜索** | ✅ | ❌ | ❓ | ❌ 不完整 |
| **Emby 管理** | ⚠️ | ❌ | ❓ | ❌ 不完整 |
| **日志查看** | ❌ | ❌ | ✅ | ❌ 不完整 |
| **健康检查** | ✅ | ❌ | ❌ | ❌ 不完整 |

### 4.2 数据流分析

#### ✅ 完整流程示例：用户登录
```
UI (LoginView.tsx)
  → 收集用户输入 (username, password)
  → 调用 auth.login(username, password)

Service (auth.ts)
  → 构造 FormData
  → POST /api/auth/login
  → 处理响应，存储 token

Backend (router/auth.py)
  → 验证密码
  → 返回 {code: 0, msg: "登录成功", data: {token: "ok"}}

UI (LoginView.tsx)
  → 接收结果
  → 跳转到主界面
```

#### 🔴 违规流程示例：系统设置
```
UI (SettingsView.tsx)
  → 直接调用 fetch('/api/config')  ← 违规！
  → 应该调用服务层

缺失的正确流程:
UI (SettingsView.tsx)
  → 调用 config.loadGlobalConfig()

Service (config.ts)
  → fetch('/api/config/load')
  → 处理响应

Backend (router/config.py)
  → GET /api/config/load
  → 返回配置数据
```

#### ❌ 断裂流程示例：文件管理
```
UI (FileSelector.tsx)
  → 可能直接调用 fetch('/api/file/list')  ← 违规！
  → 或根本没有调用

缺失的完整流程:
UI (FileManager 组件)
  → 调用 file.listFiles(path)  ← 服务不存在！

Service (file.ts)  ← 文件不存在！
  → fetch('/api/file/list?path=' + path)
  → 处理响应

Backend (router/file.py)
  → GET /api/file/list
  → 返回文件列表
```

### 4.3 API 规范一致性问题

#### 路径命名不一致
| 功能 | router 实际路径 | main.py 路径 | health.py 预期路径 |
|------|----------------|--------------|-------------------|
| 配置加载 | /api/config/load | /api/config/get | /api/config/all |
| 配置保存 | /api/config/save_all | /api/config/update | /api/config/set |
| 文件列表 | /api/file/list | /api/files/list | /api/file/list |
| 文件上传 | - | /api/files/upload | /api/file/upload |
| 离线任务创建 | /api/offline/create | - | /api/offline/add |

#### HTTP 方法不一致
| 端点 | 实际方法 | RESTful 标准 | 说明 |
|------|----------|--------------|------|
| /api/tmdb/search | POST | GET | ⚠️ 搜索应该用 GET |
| /api/tmdb/details | POST | GET | ⚠️ 获取详情应该用 GET |
| /api/tmdb/identify | POST | POST | ✅ 正确（包含 AI 处理） |
| /api/emby/refresh_and_probe | POST | POST | ✅ 正确（触发操作） |

#### 响应格式
大部分端点使用一致的响应格式：
```json
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```
✅ **响应格式统一**（这是做得好的地方）

---

## 第五部分：问题汇总与优先级

### 5.1 后端层问题

#### 🔴 P0 - 紧急
1. **解决路径重复问题**: main.py 与 router 中的重复端点（config/get vs config/load）
2. **修复 health.py 预期端点列表**: 与实际路径不匹配

#### 🟡 P1 - 重要
3. **实现缺失的核心端点**:
   - POST /api/auth/logout
   - DELETE /api/file/delete
   - GET /api/offline/list
   - POST /api/strm/generate
   - GET /api/strm/list

4. **统一命名规范**: 将 `/api/files/*` 统一为 `/api/file/*`

#### 🟢 P2 - 次要
5. **改进 RESTful 设计**: TMDB search/details 改为 GET 方法
6. **添加文档**: 为所有端点添加 OpenAPI 文档

### 5.2 服务层问题

#### 🔴 P0 - 紧急
1. **创建 services/file.ts**: 封装文件管理功能
2. **创建 services/offline.ts**: 封装离线下载功能

#### 🟡 P1 - 重要
3. **创建 services/strm.ts**: 封装 STRM 生成功能
4. **创建 services/tmdb.ts**: 封装 TMDB 功能
5. **创建 services/emby.ts**: 封装 Emby 功能

#### 🟢 P2 - 次要
6. **创建 services/health.ts**: 封装健康检查功能
7. **创建 services/logs.ts**: 封装日志功能
8. **统一错误处理**: 在所有服务中实现一致的错误处理

### 5.3 UI 层问题

#### 🔴 P0 - 紧急
1. **重构 SettingsView.tsx**: 移除直接 fetch() 调用，使用服务层
2. **审计 FileSelector.tsx**: 确认是否直接调用 API，如是则重构

#### 🟡 P1 - 重要
3. **审计所有视图**: 确保所有视图都通过服务层调用 API
4. **统一错误提示**: 实现全局错误处理机制（toast/notification）

#### 🟢 P2 - 次要
5. **添加 loading 状态**: 所有异步操作添加 loading 指示器
6. **添加表单验证**: 在 UI 层添加输入验证

---

## 第六部分：修复建议

### 6.1 快速修复（1-2 天）

#### 步骤 1: 创建缺失的服务文件

**创建 `frontend/src/services/file.ts`**:
```typescript
export const fileService = {
  async listFiles(path: string = '0', limit: number = 200) {
    const response = await fetch(`/api/file/list?path=${path}&limit=${limit}`);
    const data = await response.json();
    if (data.code !== 0) throw new Error(data.msg || '获取文件列表失败');
    return data.data;
  },
  
  async moveFile(src: string, dst: string) {
    const formData = new FormData();
    formData.append('src', src);
    formData.append('dst', dst);
    const response = await fetch('/api/file/move', { method: 'POST', body: formData });
    const data = await response.json();
    if (data.code !== 0) throw new Error(data.msg || '移动文件失败');
    return data.data;
  },
  
  async renameFile(path: string, newName: string) {
    const formData = new FormData();
    formData.append('path', path);
    formData.append('new_name', newName);
    const response = await fetch('/api/file/rename', { method: 'POST', body: formData });
    const data = await response.json();
    if (data.code !== 0) throw new Error(data.msg || '重命名失败');
    return data.data;
  }
};
```

**创建 `frontend/src/services/offline.ts`**, **tmdb.ts**, **emby.ts** 等（类似结构）

#### 步骤 2: 重构 SettingsView.tsx

替换直接的 fetch() 调用为服务层调用：
```typescript
// 之前：
const res = await fetch('/api/config');

// 修改为：
import { loadGlobalConfig } from '../services/config';
const config = await loadGlobalConfig();
```

#### 步骤 3: 审计 FileSelector.tsx

检查是否直接调用 API，如果是，则修改为：
```typescript
import { fileService } from '../services/file';

const files = await fileService.listFiles(currentPath);
```

### 6.2 中期修复（3-5 天）

#### 后端统一路径命名
- 将 main.py 中的 `/api/config/get` 移除，统一使用 router 中的 `/api/config/load`
- 将 `/api/files/*` 重命名为 `/api/file/*`

#### 实现缺失的后端端点
- 添加 POST /api/auth/logout
- 添加 GET /api/offline/list
- 添加 POST /api/strm/generate
- 等等

#### 更新 health.py 中的预期端点列表
与实际实现保持一致。

### 6.3 长期优化（1-2 周）

#### 完善 API 文档
- 添加 OpenAPI/Swagger 文档
- 为每个端点添加详细的请求/响应示例

#### 实现全局错误处理
- 创建统一的 API 调用包装器
- 实现全局 toast/notification 系统

#### 添加端到端测试
- 为关键流程添加 E2E 测试
- 使用 Playwright 或 Cypress

---

## 第七部分：成功标准

### 完成标志

- ✅ **后端层**: 
  - 所有路径命名统一
  - health.py 预期端点与实际一致
  - 缺失的核心端点已实现

- ✅ **服务层**:
  - 创建了 file.ts, offline.ts, strm.ts, tmdb.ts, emby.ts
  - 所有后端端点都有对应的服务函数
  - 服务覆盖率 > 90%

- ✅ **UI 层**:
  - 所有视图都通过服务层调用 API
  - 无直接 fetch() 调用（除 api.ts 工具函数）
  - 架构合规性 100%

- ✅ **集成测试**:
  - 所有主要功能流程测试通过
  - 错误情况都有正确处理
  - 用户体验流畅

### 验收测试清单

#### 认证流程
- [ ] 用户可以正常登录
- [ ] 2FA 验证正常工作
- [ ] 登出功能正常（需实现后端）
- [ ] 认证状态验证正常（需实现后端）

#### 配置管理
- [ ] 可以加载配置
- [ ] 可以保存配置
- [ ] 配置更改即时生效
- [ ] SettingsView 使用服务层（需重构）

#### 文件管理
- [ ] 可以浏览文件列表（需创建服务）
- [ ] 可以移动文件（需创建服务）
- [ ] 可以重命名文件（需创建服务）
- [ ] FileSelector 使用服务层（需审计）

#### 网盘整理
- [ ] 可以启动整理任务
- [ ] 可以查看任务状态
- [ ] 整理规则正确应用
- [ ] Emby 刷新正常触发

#### 离线下载
- [ ] 可以创建离线任务（需创建服务）
- [ ] 可以查看任务状态（需创建服务）
- [ ] 任务完成后自动处理
- [ ] Telegram 通知正常发送

#### TMDB & Emby
- [ ] TMDB 搜索功能正常（需创建服务）
- [ ] 元数据识别正常（需创建服务）
- [ ] Emby 刷新功能正常（需创建服务）
- [ ] 媒体库扫描正常（需实现后端）

---

## 附录

### A. 技术债务清单

1. **main.py 中的重复端点** - 技术债务等级: P0
2. **health.py 预期端点不准确** - 技术债务等级: P0
3. **服务层覆盖率低（37.5%）** - 技术债务等级: P0
4. **SettingsView 架构违规** - 技术债务等级: P0
5. **路径命名不一致** - 技术债务等级: P1
6. **HTTP 方法不符合 RESTful** - 技术债务等级: P2
7. **缺少 API 文档** - 技术债务等级: P2
8. **缺少 E2E 测试** - 技术债务等级: P2

### B. 参考资料

- 项目 README: `/home/engine/project/README.md`
- 后端路由: `/home/engine/project/backend/router/`
- 前端服务: `/home/engine/project/frontend/src/services/`
- 前端视图: `/home/engine/project/frontend/src/views/`
- 健康报告端点: GET `/api/health/report`

### C. 联系方式

如有疑问，请联系项目维护者或提交 Issue。

---

**报告结束**
