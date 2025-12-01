import { AppConfig } from '../types';
import { api } from './api';

const STORAGE_KEY = '115_BOT_CONFIG';

// --- 默认预设规则 (UI需要用到这些常量) ---
export const DEFAULT_MOVIE_RULES = [
  { id: 'm_anim', name: '动画电影', targetCid: '', conditions: { genre_ids: '16' } },
  { id: 'm_cn', name: '华语电影', targetCid: '', conditions: { origin_country: 'CN,TW,HK' } },
  { id: 'm_foreign', name: '外语电影', targetCid: '', conditions: { origin_country: '!CN,TW,HK' } },
];

export const DEFAULT_TV_RULES = [
  { id: 't_cn', name: '华语剧集', targetCid: '', conditions: { origin_country: 'CN,TW,HK' } },
  { id: 't_western', name: '欧美剧集', targetCid: '', conditions: { origin_country: '!CN,TW,HK,JP,KR' } },
  { id: 't_asia', name: '日韩剧集', targetCid: '', conditions: { origin_country: 'JP,KR' } },
  { id: 't_cn_anim', name: '国漫', targetCid: '', conditions: { genre_ids: '16', origin_country: 'CN,TW,HK' } },
  { id: 't_jp_anim', name: '日番', targetCid: '', conditions: { genre_ids: '16', origin_country: 'JP' } },
  { id: 't_doc', name: '纪录片', targetCid: '', conditions: { genre_ids: '99' } },
  { id: 't_show', name: '综艺', targetCid: '', conditions: { genre_ids: '10764,10767' } },
  { id: 't_kids', name: '儿童', targetCid: '', conditions: { genre_ids: '10762' } },
];

// --- 默认空配置 ---
const DEFAULT_CONFIG: AppConfig = {
  telegram: { botToken: '', adminUserId: '', whitelistMode: true, notificationChannelId: '' },
  cloud115: { loginMethod: 'cookie', loginApp: 'web', cookies: '', appId: '', userAgent: '', downloadPath: '0', downloadDirName: '根目录', autoDeleteMsg: true, qps: 0.8 },
  cloud123: { enabled: false, clientId: '', clientSecret: '', qps: 1.0 },
  openList: { enabled: false, url: '', mountPath: '/d', username: '', password: '' },
  proxy: { enabled: false, type: 'http', host: '127.0.0.1', port: '7890' },
  tmdb: { apiKey: '', language: 'zh-CN', includeAdult: false },
  emby: { enabled: false, serverUrl: '', apiKey: '', refreshAfterOrganize: true, notifications: { enabled: true, forwardToTelegram: true, includePosters: true, playbackReportingFreq: 'weekly' }, posterGeneration: { enabled: false, template: 'modern_grid', overlayDirName: true, sortOrder: 'added_date', cronSchedule: '0 0 * * *' } },
  strm: { enabled: false, outputDir: '/data/strm', sourceCid115: '0', urlPrefix115: 'http://localhost:12808/dav/115', sourceDir123: '/', urlPrefix123: 'http://localhost:12808/dav/123', sourcePathOpenList: '/', urlPrefixOpenList: 'http://localhost:12808/dav/openlist', webdav: { enabled: true, port: '5244', username: 'admin', password: 'password', readOnly: true } },
  organize: { enabled: false, sourceCid: '0', sourceDirName: '', targetCid: '0', targetDirName: '', ai: { enabled: false, provider: 'openai', baseUrl: 'https://api.openai.com/v1', apiKey: '', model: 'gpt-3.5-turbo' }, rename: { enabled: true, movieTemplate: '{title} ({year})', seriesTemplate: '{title} - S{season}E{episode}', addTmdbIdToFolder: true }, movieRules: DEFAULT_MOVIE_RULES, tvRules: DEFAULT_TV_RULES },
  twoFactorSecret: ''
};

// --- 核心逻辑 ---

// 1. 加载配置 (同步方法，用于 React State 初始化)
// 策略: 优先读 LocalStorage 缓存以便秒开，随后通过 useEffect 在后台同步后端数据
export const loadConfig = (): AppConfig => {
  // 尝试从 LocalStorage 读取
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      // 深度合并默认值，防止缺少新字段
      return deepMerge(DEFAULT_CONFIG, parsed);
    } catch (e) { console.error(e); }
  }
  
  // 如果没有缓存，先尝试同步获取一次后端 (通常 React 初始化时不建议 await，所以这里先返默认，靠组件 sync)
  // 为了更好的体验，我们在组件挂载时调用 syncRemoteConfig
  return DEFAULT_CONFIG;
};

// 2. 保存配置 (异步，同时写入 LocalStorage 和 后端)
export const saveConfig = async (config: AppConfig): Promise<void> => {
  // 本地缓存
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  // 推送给后端 API
  await api.post('/api/config', config);
};

// 3. 从后端拉取最新配置 (供 App.tsx 或 Views 初始化时调用)
export const syncRemoteConfig = async (): Promise<AppConfig | null> => {
  const remote = await api.get('/api/config');
  if (remote && Object.keys(remote).length > 0) {
    const merged = deepMerge(DEFAULT_CONFIG, remote);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    return merged;
  }
  return null;
};

// 简单的深度合并工具
function deepMerge(target: any, source: any): any {
  const output = { ...target };
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target)) Object.assign(output, { [key]: source[key] });
        else output[key] = deepMerge(target[key], source[key]);
      } else {
        Object.assign(output, { [key]: source[key] });
      }
    });
  }
  return output;
}

function isObject(item: any) {
  return (item && typeof item === 'object' && !Array.isArray(item));
}
