# Telegram-115Bot 三层集成指南

**版本**: 2.1  
**更新时间**: 2024-12-05  
**目标**: 确保前端 UI → 服务层 → 后端 API 完美对接

---

## 目录

1. [架构概览](#架构概览)
2. [服务层使用指南](#服务层使用指南)
3. [后端 API 映射表](#后端-api-映射表)
4. [最佳实践](#最佳实践)
5. [常见问题](#常见问题)
6. [迁移指南](#迁移指南)

---

## 架构概览

### 三层架构原则

```
┌─────────────────────────────────────────────────────────┐
│                      UI 层 (Views)                       │
│  UserCenterView, CloudOrganizeView, SettingsView, etc.  │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ 调用服务函数
                         │ 例: await fileService.listFiles(path)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  服务层 (Services)                       │
│  auth.ts, config.ts, file.ts, offline.ts, tmdb.ts, ... │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP 请求 (fetch)
                         │ 例: POST /api/file/list
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  后端 API (FastAPI)                      │
│  router/auth.py, router/file.py, router/config.py, ... │
└─────────────────────────────────────────────────────────┘
```

### 核心原则

1. **UI 层禁止直接调用 fetch()** - 必须通过服务层
2. **服务层统一错误处理** - 抛出用户友好的错误信息
3. **后端统一响应格式** - `{code: 0, msg: "...", data: {...}}`

---

## 服务层使用指南

### 安装和导入

所有服务已在 `frontend/src/services/index.ts` 中统一导出：

```typescript
// 推荐：按需导入
import { fileService, offlineService, tmdbService } from '@/services';

// 或者：导入特定服务
import { fileService } from '@/services/file';
import { authService } from '@/services/auth';
```

### 1. 认证服务 (auth.ts)

#### 登录

```typescript
import { login } from '@/services/auth';

const handleLogin = async (username: string, password: string) => {
  try {
    const result = await login(username, password);
    if (result.success) {
      console.log('登录成功');
      // 跳转到主页
    } else if (result.locked) {
      console.error('账户已锁定');
    } else {
      console.error('密码错误');
    }
  } catch (error) {
    console.error('登录失败:', error);
  }
};
```

#### 2FA 验证

```typescript
import { verify2FA } from '@/services/auth';

const handle2FA = async (code: string) => {
  const success = await verify2FA(code);
  if (success) {
    console.log('2FA 验证成功');
  }
};
```

#### 检查认证状态

```typescript
import { checkAuth, check2FA } from '@/services/auth';

const isLoggedIn = checkAuth(); // 检查是否登录
const is2FAVerified = check2FA(); // 检查 2FA 是否已验证
```

#### 登出

```typescript
import { logout } from '@/services/auth';

const handleLogout = () => {
  logout();
  // 跳转到登录页
};
```

---

### 2. 配置服务 (config.ts)

#### 加载全局配置

```typescript
import { loadGlobalConfig } from '@/services/config';

const fetchConfig = async () => {
  try {
    const config = await loadGlobalConfig();
    console.log('配置加载成功:', config);
    return config;
  } catch (error) {
    console.error('配置加载失败:', error);
    // 可以使用 mockConfig 作为后备
  }
};
```

#### 保存全局配置

```typescript
import { saveGlobalConfig } from '@/services/config';

const handleSave = async (config: AppConfig) => {
  try {
    await saveGlobalConfig(config);
    console.log('配置保存成功');
  } catch (error) {
    console.error('配置保存失败:', error);
  }
};
```

#### 修改管理员密码

```typescript
import { saveAdminPassword } from '@/services/config';

const changePassword = async (newPassword: string) => {
  await saveAdminPassword(newPassword);
  console.log('密码修改成功');
};
```

#### 保存代理配置

```typescript
import { saveProxyConfig } from '@/services/config';

const updateProxy = async (proxyConfig: ProxySettings) => {
  await saveProxyConfig(proxyConfig);
  console.log('代理配置已保存');
};
```

#### 生成和验证 2FA

```typescript
import { generate2FASecret, verifyAndSave2FA } from '@/services/config';

// 生成 2FA 密钥
const setup2FA = async () => {
  const { secret, otpauthUrl } = await generate2FASecret();
  console.log('2FA 密钥:', secret);
  console.log('OTP Auth URL:', otpauthUrl);
  // 显示二维码
};

// 验证并保存 2FA
const save2FA = async (secret: string, code: string) => {
  await verifyAndSave2FA(secret, code);
  console.log('2FA 已启用');
};
```

---

### 3. 文件服务 (file.ts)

#### 列出文件

```typescript
import { fileService } from '@/services/file';

const loadFiles = async (path: string = '0') => {
  try {
    const files = await fileService.listFiles(path, 200);
    console.log('文件列表:', files);
    return files;
  } catch (error) {
    if (error.message.includes('115 Cookie')) {
      console.error('请先登录 115 账号');
    } else {
      console.error('加载文件失败:', error);
    }
  }
};
```

#### 移动文件

```typescript
const moveFile = async (srcPath: string, dstPath: string) => {
  await fileService.moveFile(srcPath, dstPath);
  console.log('文件移动成功');
};
```

#### 重命名文件

```typescript
const renameFile = async (filePath: string, newName: string) => {
  await fileService.renameFile(filePath, newName);
  console.log('文件重命名成功');
};
```

#### 上传文件

```typescript
const uploadFile = async (file: File) => {
  const result = await fileService.uploadFile(file);
  console.log('上传成功:', result.filename);
  return result.path;
};
```

#### 通知 Emby 刷新

```typescript
const notifyEmbyRefresh = async (path: string) => {
  await fileService.notifyEmby(path);
  console.log('已通知 Emby 刷新');
};
```

---

### 4. 离线下载服务 (offline.ts)

#### 创建离线任务

```typescript
import { offlineService } from '@/services/offline';

const createDownload = async (url: string, folder: string = '/') => {
  try {
    const task = await offlineService.createTask(url, folder, true);
    console.log('任务创建成功:', task.local_task_id);
    return task;
  } catch (error) {
    if (error.message.includes('QPS')) {
      console.error('请求频率过高，请稍后再试');
    } else {
      console.error('创建任务失败:', error);
    }
  }
};
```

#### 查询任务状态

```typescript
const checkTaskStatus = async (taskId: string) => {
  try {
    const status = await offlineService.getTaskStatus(taskId);
    console.log('任务状态:', status.status || status.state);
    return status;
  } catch (error) {
    if (error.message.includes('不存在')) {
      console.error('任务不存在');
    } else {
      console.error('查询失败:', error);
    }
  }
};
```

---

### 5. TMDB 服务 (tmdb.ts)

#### 搜索影视

```typescript
import { tmdbService } from '@/services/tmdb';

const searchMovie = async (query: string, year?: number) => {
  const results = await tmdbService.search(query, 'movie', year);
  console.log('搜索结果:', results);
  return results;
};

const searchTV = async (query: string) => {
  const results = await tmdbService.search(query, 'tv');
  return results;
};
```

#### 获取详情

```typescript
const getMovieDetails = async (tmdbId: number) => {
  const details = await tmdbService.getDetails(tmdbId, 'movie');
  console.log('电影详情:', details);
  return details;
};
```

#### AI 识别

```typescript
const identifyMedia = async (filename: string) => {
  const result = await tmdbService.identify(filename, 'movie');
  console.log('识别结果:', result.candidates);
  if (result.ai_choice) {
    console.log('AI 推荐:', result.ai_choice);
  }
  return result;
};
```

---

### 6. Emby 服务 (emby.ts)

#### 刷新媒体库

```typescript
import { embyService } from '@/services/emby';

const refreshLibrary = async (itemId?: string) => {
  try {
    await embyService.refreshAndProbe(itemId);
    console.log('Emby 刷新成功');
  } catch (error) {
    if (error.message.includes('未配置')) {
      console.error('请先配置 Emby 连接信息');
    } else if (error.message.includes('频率')) {
      console.error('请求过于频繁');
    } else {
      console.error('刷新失败:', error);
    }
  }
};

// 简化版（无 itemId）
const simpleRefresh = async () => {
  await embyService.refresh();
};
```

---

### 7. 任务服务 (task.ts)

#### 启动整理任务

```typescript
import { startOrganizeTask } from '@/services/task';

const runOrganize = async () => {
  try {
    const response = await startOrganizeTask();
    if (response.status === 'success') {
      console.log('整理任务已启动，Job ID:', response.job_id);
    }
  } catch (error) {
    console.error('启动任务失败:', error);
  }
};
```

---

### 8. 健康检查服务 (health.ts)

#### 获取健康报告

```typescript
import { healthService } from '@/services/health';

const checkHealth = async () => {
  const report = await healthService.getReport();
  console.log('健康分数:', report.summary.health_score);
  console.log('缺失端点:', report.missing_endpoints);
  return report;
};
```

#### 获取版本信息

```typescript
const getVersion = async () => {
  const version = await healthService.getVersion();
  console.log('版本:', version.version);
  console.log('名称:', version.name);
};
```

#### 简单健康检查

```typescript
const quickCheck = async () => {
  const isHealthy = await healthService.check();
  if (isHealthy) {
    console.log('后端服务正常');
  } else {
    console.log('后端服务异常');
  }
};
```

---

## 后端 API 映射表

### 认证相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属 Router |
|---------|----------|---------|------------|
| `login()` | POST | `/api/auth/login` | router/auth.py |
| `verify2FA()` | POST | `/api/2fa/verify` | main.py |
| `saveAdminPassword()` | POST | `/api/auth/password` | router/auth.py |
| `generate2FASecret()` | GET | `/api/auth/2fa/generate` | router/auth.py |
| `verifyAndSave2FA()` | POST | `/api/auth/2fa/verify` | router/auth.py |

### 配置相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属 Router |
|---------|----------|---------|------------|
| `loadGlobalConfig()` | GET | `/api/config/load` | router/config.py |
| `saveGlobalConfig()` | POST | `/api/config/save_all` | router/config.py |
| `saveProxyConfig()` | POST | `/api/config/proxy` | router/config.py |

**注意**: SettingsView.tsx 使用的是 `api/common_settings.py` 提供的 `/api/config` (GET/POST)，这与 router/config.py 不同。两套配置接口需要统一。

### 文件相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属 Router |
|---------|----------|---------|------------|
| `fileService.listFiles()` | GET | `/api/file/list` | router/file.py |
| `fileService.moveFile()` | POST | `/api/file/move` | router/file.py |
| `fileService.renameFile()` | POST | `/api/file/rename` | router/file.py |
| `fileService.notifyEmby()` | POST | `/api/file/notify_emby` | router/file.py |
| `fileService.uploadFile()` | POST | `/api/files/upload` | main.py |

### 离线下载相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属 Router |
|---------|----------|---------|------------|
| `offlineService.createTask()` | POST | `/api/offline/create` | router/offline.py |
| `offlineService.getTaskStatus()` | GET | `/api/offline/status` | router/offline.py |

### TMDB 相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属 Router |
|---------|----------|---------|------------|
| `tmdbService.search()` | POST | `/api/tmdb/search` | router/tmdb.py |
| `tmdbService.getDetails()` | POST | `/api/tmdb/details` | router/tmdb.py |
| `tmdbService.identify()` | POST | `/api/tmdb/identify` | router/tmdb.py |

### Emby 相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属 Router |
|---------|----------|---------|------------|
| `embyService.refreshAndProbe()` | POST | `/api/emby/refresh_and_probe` | router/emby.py |
| `embyService.refresh()` | POST | `/api/emby/refresh_and_probe` | router/emby.py |

### 任务相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属 Router |
|---------|----------|---------|------------|
| `startOrganizeTask()` | POST | `/api/file/organize/start` | router/file.py |

### 健康检查相关

| 服务函数 | HTTP 方法 | 后端路径 | 所属文件 |
|---------|----------|---------|---------|
| `healthService.getReport()` | GET | `/api/health/report` | router/health.py |
| `healthService.getVersion()` | GET | `/api/version` | main.py |
| `healthService.getStatus()` | GET | `/api/status` | main.py |
| `healthService.check()` | GET | `/healthz` | main.py |

---

## 最佳实践

### 1. UI 层调用服务的标准模式

```typescript
import { fileService } from '@/services';
import { useState } from 'react';

const MyComponent = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any[]>([]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fileService.listFiles('0');
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  // UI 渲染
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  return <div>数据: {JSON.stringify(data)}</div>;
};
```

### 2. 统一错误处理

所有服务函数都会在请求失败时抛出 Error，UI 层应该使用 try-catch 捕获：

```typescript
try {
  await someService.someMethod();
  showSuccessToast('操作成功');
} catch (error) {
  const message = error instanceof Error ? error.message : '操作失败';
  showErrorToast(message);
}
```

### 3. Loading 状态管理

为所有异步操作添加 loading 状态：

```typescript
const [isSaving, setIsSaving] = useState(false);

const handleSave = async () => {
  setIsSaving(true);
  try {
    await configService.saveGlobalConfig(config);
  } finally {
    setIsSaving(false);
  }
};
```

### 4. 响应式设计

服务层返回的数据应该直接用于状态更新：

```typescript
const [files, setFiles] = useState<FileItem[]>([]);

useEffect(() => {
  const load = async () => {
    const data = await fileService.listFiles();
    setFiles(data);
  };
  load();
}, []);
```

### 5. 避免直接调用 fetch

❌ **错误示例**:
```typescript
// 直接在组件中调用 fetch - 违反架构原则！
const res = await fetch('/api/config');
const data = await res.json();
```

✅ **正确示例**:
```typescript
// 通过服务层调用
import { loadGlobalConfig } from '@/services/config';
const config = await loadGlobalConfig();
```

---

## 常见问题

### Q1: 服务函数抛出错误后如何处理？

**A**: 所有服务函数在失败时会抛出 Error 对象，UI 层应该使用 try-catch 捕获并显示用户友好的错误提示。

```typescript
try {
  await fileService.moveFile(src, dst);
  toast.success('文件移动成功');
} catch (error) {
  toast.error(error.message || '移动失败');
}
```

### Q2: 为什么有些服务使用 FormData，有些使用 JSON？

**A**: 这取决于后端接口的定义：
- **FormData**: 用于文件上传、表单提交（如 auth.login）
- **JSON**: 用于复杂对象传递（如 config.saveGlobalConfig）

查看后端路由的参数定义：
- `Form(...)` 参数 → 使用 FormData
- `BaseModel` 参数 → 使用 JSON

### Q3: 如何在服务层添加新的 API 调用？

**A**: 步骤如下：

1. 确认后端接口已实现
2. 在对应的服务文件中添加函数
3. 遵循现有模式（async/await, 错误处理）
4. 在 `services/index.ts` 中导出（如果是新文件）
5. 在 UI 层使用新函数

### Q4: SettingsView.tsx 为什么直接调用 fetch？

**A**: 这是历史遗留问题。SettingsView 使用的 `/api/config` 端点来自 `api/common_settings.py`，与 router/config.py 不同。建议：

1. 统一使用 router/config.py 的端点
2. 修改 SettingsView 使用 config.ts 服务层
3. 或者为 common_settings 创建专门的服务文件

### Q5: 如何处理 QPS 限流错误？

**A**: 服务层会抛出包含 "QPS" 或 "频率" 的错误信息，UI 层应该：

```typescript
try {
  await offlineService.createTask(url, folder);
} catch (error) {
  if (error.message.includes('QPS') || error.message.includes('频率')) {
    toast.warning('请求过于频繁，请稍后再试');
  } else {
    toast.error('操作失败');
  }
}
```

### Q6: FileSelector 组件如何调用文件列表 API？

**A**: FileSelector 应该通过 props 接收数据，由父组件调用服务：

```typescript
// 父组件
const ParentView = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  
  const loadFiles = async (path: string) => {
    const data = await fileService.listFiles(path);
    setFiles(data);
  };
  
  return <FileSelector files={files} onNavigate={loadFiles} />;
};
```

---

## 迁移指南

### 从直接 fetch 迁移到服务层

如果您的组件当前直接调用 fetch，请按以下步骤迁移：

#### 步骤 1: 识别所有 fetch 调用

```typescript
// 搜索您的组件文件
const res = await fetch('/api/...');
```

#### 步骤 2: 查找对应的服务函数

参考本文档的 [后端 API 映射表](#后端-api-映射表)，找到对应的服务函数。

#### 步骤 3: 替换调用

**之前**:
```typescript
const res = await fetch('/api/config/load');
const data = await res.json();
if (data.code !== 0) {
  throw new Error(data.msg);
}
return data.data;
```

**之后**:
```typescript
import { loadGlobalConfig } from '@/services/config';

const config = await loadGlobalConfig();
return config;
```

#### 步骤 4: 更新导入

确保在文件顶部导入所需服务：

```typescript
import { fileService, offlineService } from '@/services';
```

#### 步骤 5: 测试

确保迁移后功能正常，错误处理得当。

---

## 附录

### A. 完整的服务文件列表

- `frontend/src/services/auth.ts` - 认证服务
- `frontend/src/services/config.ts` - 配置服务
- `frontend/src/services/task.ts` - 任务服务
- `frontend/src/services/file.ts` - 文件服务
- `frontend/src/services/offline.ts` - 离线下载服务
- `frontend/src/services/tmdb.ts` - TMDB 服务
- `frontend/src/services/emby.ts` - Emby 服务
- `frontend/src/services/health.ts` - 健康检查服务
- `frontend/src/services/api.ts` - 通用 API 工具
- `frontend/src/services/mockConfig.ts` - 本地配置后备
- `frontend/src/services/index.ts` - 统一导出

### B. TypeScript 类型定义

所有服务的类型定义请参考：
- `frontend/src/types.ts` - 全局类型定义
- 各服务文件内的 `export interface` 定义

### C. 相关文档

- [API 审计报告](./API_AUDIT_REPORT.md) - 完整的三层审计结果
- [项目 README](../README.md) - 项目概览和安装指南
- [后端 API 文档](./BACKEND_API.md) - 后端端点详细文档（待创建）

---

**集成指南结束**

如有疑问，请联系项目维护者或查阅 API 审计报告。
