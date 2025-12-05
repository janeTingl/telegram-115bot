# Telegram-115Bot API 快速参考手册

**版本**: 2.1 | **更新**: 2024-12-05

---

## 🚀 快速开始

### 导入服务

```typescript
// 推荐：从 index 导入
import { fileService, offlineService, tmdbService } from '@/services';

// 或者：单独导入
import { login, verify2FA } from '@/services/auth';
import { loadGlobalConfig } from '@/services/config';
```

### 基本使用模式

```typescript
const MyComponent = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await someService.someMethod();
      // 处理结果
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败');
    } finally {
      setLoading(false);
    }
  };
};
```

---

## 📚 服务速查表

### 认证服务 (auth.ts)

```typescript
// 登录
const { success, locked } = await login('admin', 'password');

// 2FA 验证
const verified = await verify2FA('123456');

// 检查状态
const isLoggedIn = checkAuth();
const is2FAVerified = check2FA();

// 登出
logout();
```

### 配置服务 (config.ts)

```typescript
// 加载配置
const config = await loadGlobalConfig();

// 保存配置
await saveGlobalConfig(config);

// 修改密码
await saveAdminPassword('newPassword');

// 代理配置
await saveProxyConfig({ enabled: true, type: 'http', host: '127.0.0.1', port: '7890' });

// 2FA 设置
const { secret, otpauthUrl } = await generate2FASecret();
await verifyAndSave2FA(secret, '123456');
```

### 文件服务 (file.ts)

```typescript
// 列出文件
const files = await fileService.listFiles('0', 200);

// 移动文件
await fileService.moveFile('/path/to/src', '/path/to/dst');

// 重命名
await fileService.renameFile('/path/to/file', 'newName');

// 上传
const result = await fileService.uploadFile(fileObject);

// 通知 Emby
await fileService.notifyEmby('/path/to/media');
```

### 离线下载服务 (offline.ts)

```typescript
// 创建任务
const task = await offlineService.createTask(
  'magnet:?xt=...',
  '/downloads',
  true  // 通知 TG
);

// 查询状态
const status = await offlineService.getTaskStatus(task.local_task_id);
```

### TMDB 服务 (tmdb.ts)

```typescript
// 搜索电影
const movies = await tmdbService.search('阿凡达', 'movie', 2009);

// 搜索电视剧
const shows = await tmdbService.search('权力的游戏', 'tv');

// 获取详情
const details = await tmdbService.getDetails(12345, 'movie');

// AI 识别
const result = await tmdbService.identify('Avatar.2009.1080p.BluRay', 'movie');
console.log('候选:', result.candidates);
console.log('AI 推荐:', result.ai_choice);
```

### Emby 服务 (emby.ts)

```typescript
// 刷新媒体库
await embyService.refresh();

// 刷新并探测特定项目
await embyService.refreshAndProbe('itemId123');
```

### 任务服务 (task.ts)

```typescript
// 启动整理任务
const { status, job_id } = await startOrganizeTask();
```

### 健康检查服务 (health.ts)

```typescript
// 完整报告
const report = await healthService.getReport();
console.log('健康分数:', report.summary.health_score);

// 版本信息
const version = await healthService.getVersion();

// 快速检查
const isHealthy = await healthService.check();
```

---

## 🔌 后端 API 速查表

### 认证

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/api/auth/login` | POST | `password` (FormData) | `{code, msg, data: {token}}` |
| `/api/auth/password` | POST | `new_password` (FormData) | `{code, msg}` |
| `/api/auth/2fa/generate` | GET | - | `{code, data: {secret, otpauth_url}}` |
| `/api/auth/2fa/verify` | POST | `secret, code` (FormData) | `{code, msg}` |
| `/api/2fa/verify` | POST | `code` (FormData) | `{code, msg}` |

### 配置

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/api/config/load` | GET | - | `{code, data: AppConfig}` |
| `/api/config/save_all` | POST | `config` (JSON) | `{code, msg}` |
| `/api/config/proxy` | POST | `ProxyConfig` (JSON) | `{code, msg}` |
| `/api/config` | GET | - | `AppConfig` (直接返回) |
| `/api/config` | POST | `AppConfigModel` (JSON) | `{code, message}` |

### 文件

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/api/file/list` | GET | `path, limit` (query) | `{code, data: FileItem[]}` |
| `/api/file/move` | POST | `src, dst` (FormData) | `{code, data}` |
| `/api/file/rename` | POST | `path, new_name` (FormData) | `{code, data}` |
| `/api/file/notify_emby` | POST | `path` (FormData) | `{code, msg}` |
| `/api/files/upload` | POST | `file` (FormData) | `{code, data: {filename, path}}` |
| `/api/file/organize/start` | POST | `{}` (JSON) | `{code, msg, data: {job_id}}` |

### 离线下载

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/api/offline/create` | POST | `{url, target_folder, notify_tg}` (JSON) | `{code, data: {local_task_id, remote}}` |
| `/api/offline/status` | GET | `task_id` (query) | `{code, data: OfflineStatus}` |

### TMDB

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/api/tmdb/search` | POST | `q, typ, year` (FormData) | `{code, data: TMDBSearchResult[]}` |
| `/api/tmdb/details` | POST | `tmdb_id, typ` (FormData) | `{code, data: TMDBDetails}` |
| `/api/tmdb/identify` | POST | `name, typ` (FormData) | `{code, data: {candidates, ai_choice}}` |

### Emby

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/api/emby/refresh_and_probe` | POST | `item_id` (FormData, 可选) | `{code, msg}` |

### 健康检查

| 端点 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/healthz` | GET | - | `"ok"` (纯文本) |
| `/api/status` | GET | - | `{code, data: {uptime, version}}` |
| `/api/version` | GET | - | `{code, data: {version, name}}` |
| `/api/health/report` | GET | - | `{code, data: HealthReport}` |

---

## 🎨 UI 组件使用

### FileSelector 组件

```typescript
import { FileSelector } from '@/components/FileSelector';

const MyView = () => {
  const [selectorOpen, setSelectorOpen] = useState(false);
  
  const handleSelect = (cid: string, name: string) => {
    console.log('选中:', name, cid);
  };

  return (
    <>
      <button onClick={() => setSelectorOpen(true)}>选择文件夹</button>
      <FileSelector
        isOpen={selectorOpen}
        onClose={() => setSelectorOpen(false)}
        onSelect={handleSelect}
        title="选择目标文件夹"
      />
    </>
  );
};
```

---

## ⚠️ 常见错误处理

### 401 未授权

```typescript
try {
  await fileService.listFiles('0');
} catch (error) {
  if (error.message.includes('115 Cookie')) {
    // 跳转到登录页或提示用户登录
  }
}
```

### 429 限流

```typescript
try {
  await offlineService.createTask(url, folder);
} catch (error) {
  if (error.message.includes('QPS') || error.message.includes('频率')) {
    // 提示用户稍后再试
  }
}
```

### 网络错误

```typescript
try {
  await loadGlobalConfig();
} catch (error) {
  // 使用本地配置作为后备
  const fallbackConfig = loadConfig(); // from mockConfig
}
```

---

## 🔧 开发技巧

### 1. 统一错误提示

```typescript
// 创建通知工具
const notify = {
  success: (msg: string) => console.log('✅', msg),
  error: (msg: string) => console.error('❌', msg),
  warning: (msg: string) => console.warn('⚠️', msg),
};

// 在组件中使用
try {
  await fileService.moveFile(src, dst);
  notify.success('文件移动成功');
} catch (error) {
  notify.error(error.message || '操作失败');
}
```

### 2. Loading 状态管理

```typescript
const useAsyncAction = (action: () => Promise<void>) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async () => {
    setLoading(true);
    setError(null);
    try {
      await action();
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败');
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, execute };
};

// 使用
const { loading, error, execute } = useAsyncAction(async () => {
  await fileService.moveFile(src, dst);
});
```

### 3. 表单验证

```typescript
const validateConfig = (config: AppConfig) => {
  if (!config.cloud115.cookies) {
    throw new Error('115 Cookie 不能为空');
  }
  if (!config.emby.host) {
    throw new Error('Emby 地址不能为空');
  }
  // 更多验证...
};

// 使用
try {
  validateConfig(config);
  await saveGlobalConfig(config);
} catch (error) {
  notify.error(error.message);
}
```

---

## 📝 代码规范

### ✅ 正确示例

```typescript
// UI 层
import { fileService } from '@/services';

const MyComponent = () => {
  const loadFiles = async () => {
    try {
      const files = await fileService.listFiles('0');
      setFiles(files);
    } catch (error) {
      setError(error.message);
    }
  };
};
```

### ❌ 错误示例

```typescript
// ❌ 不要在 UI 层直接调用 fetch
const loadFiles = async () => {
  const res = await fetch('/api/file/list?path=0');
  const data = await res.json();
  setFiles(data.data);
};
```

---

## 🔗 相关资源

- [完整审计报告](./API_AUDIT_REPORT.md) - 65+ 页详细分析
- [集成指南](./INTEGRATION_GUIDE.md) - 20+ 页使用教程
- [审计总结](./AUDIT_SUMMARY.md) - 执行摘要和待办事项
- [项目 README](../README.md) - 项目概览

---

## 🆘 获取帮助

遇到问题？请检查：

1. **错误信息**: 服务层会抛出描述性错误
2. **网络状态**: 确保后端服务正常运行
3. **认证状态**: 某些接口需要登录或 2FA
4. **配置检查**: 确保 115 Cookie、Emby API Key 等已配置
5. **控制台日志**: 查看浏览器控制台的详细错误

---

**快速参考手册结束**

更新时间: 2024-12-05 | 版本: 2.1
