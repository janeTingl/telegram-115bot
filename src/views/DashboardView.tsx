import React, { useEffect, useState } from 'react';
import { 
  Play, HardDrive, Film, Tv, 
  Activity, TrendingUp, AlertCircle, RefreshCw, Server
} from 'lucide-react';
// 假设你已经在 api.ts 或 UserCenterView 里定义了 loadConfig
// 如果没有，请把下面的 loadConfig 辅助函数取消注释
import { loadConfig } from '../services/api'; 

// === 辅助函数 (防止 import 报错) ===
// const loadConfig = () => {
//   try { return JSON.parse(localStorage.getItem('app_config') || '{}'); } catch { return {}; }
// };

interface DashboardStats {
  movieCount: number;
  seriesCount: number;
  episodeCount: number;
  activeSessions: number;
  serverName: string;
  version: string;
}

interface RecentItem {
  id: string;
  name: string;
  type: string;
  date: string;
  seriesName?: string;
}

interface ChartData {
  date: string;
  count: number;
}

export const DashboardView: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // 数据状态
  const [stats, setStats] = useState<DashboardStats>({ 
    movieCount: 0, seriesCount: 0, episodeCount: 0, activeSessions: 0, serverName: 'Emby Server', version: '' 
  });
  const [recentItems, setRecentItems] = useState<RecentItem[]>([]);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [chartMax, setChartMax] = useState(10);

  // 获取数据的核心逻辑
  const fetchData = async () => {
    setLoading(true);
    setError('');
    
    const config = loadConfig();
    // 兼容 config 结构：可能是 config.emby.host 或 config.emby.url
    const embyUrl = config?.emby?.host || config?.emby?.url;
    const apiKey = config?.emby?.apiKey;

    if (!embyUrl || !apiKey) {
      setError('请先在“Emby 设置”或“个人中心”配置 Emby 地址和 API Key');
      setLoading(false);
      return;
    }

    // 处理 URL 末尾斜杠
    const baseUrl = embyUrl.replace(/\/$/, '');
    const headers = { 'X-Emby-Token': apiKey };

    try {
      // 1. 并行请求基础数据
      const [countsRes, sessionsRes, infoRes, recentRes] = await Promise.all([
        fetch(`${baseUrl}/emby/Items/Counts`, { headers }),
        fetch(`${baseUrl}/emby/Sessions`, { headers }),
        fetch(`${baseUrl}/emby/System/Info`, { headers }),
        fetch(`${baseUrl}/emby/Items?SortBy=DateCreated&SortOrder=Descending&Limit=5&Recursive=true&IncludeItemTypes=Movie,Episode`, { headers })
      ]);

      if (!countsRes.ok) throw new Error('连接 Emby 失败，请检查地址和 Key');

      const counts = await countsRes.json();
      const sessions = await sessionsRes.json();
      const info = await infoRes.json();
      const recents = await recentRes.json();

      setStats({
        movieCount: counts.MovieCount || 0,
        seriesCount: counts.SeriesCount || 0,
        episodeCount: counts.EpisodeCount || 0,
        activeSessions: sessions.length || 0,
        serverName: info.ServerName || 'Emby Server',
        version: info.Version || ''
      });

      // 格式化最近添加
      const formattedRecents = recents.Items.map((item: any) => ({
        id: item.Id,
        name: item.Name,
        type: item.Type === 'Episode' ? 'TV' : 'Movie',
        seriesName: item.SeriesName,
        date: new Date(item.DateCreated).toLocaleDateString()
      }));
      setRecentItems(formattedRecents);

      // 2. 尝试请求 Playback Reporting 插件数据 (Level 2)
      // 这是一个非标准 API，可能会失败
      try {
        // 请求最近 7 天的播放统计
        const reportUrl = `${baseUrl}/emby/user_usage_stats/daily_counts?Days=7`;
        const reportRes = await fetch(reportUrl, { headers });
        
        if (reportRes.ok) {
           const reportData = await reportRes.json();
           // reportData 结构通常是: [{ Date: '2023-01-01', Count: 10 }, ...]
           // 注意：不同版本的插件返回结构可能不同，这里做适配
           const chart = reportData.map((d: any) => ({
             date: d.Date ? d.Date.substring(5, 10) : 'N/A', // 取 MM-DD
             count: d.Count || d.TotalDuration || 0 // 可能是次数或时长
           })).reverse(); // API 通常返回倒序
           
           setChartData(chart);
           setChartMax(Math.max(...chart.map((d: any) => d.count), 5));
        } else {
           // 插件未安装或 API 变动，使用空数据占位
           console.warn('Playback Reporting plugin not found or API error');
           setChartData(getMockChartData()); // 降级到模拟数据，或者显示为空
        }
      } catch (e) {
        console.warn('Playback Reporting fetch failed', e);
        setChartData(getMockChartData()); // 降级
      }

    } catch (err: any) {
      console.error(err);
      setError(err.message || '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 生成占位图表数据 (降级方案)
  const getMockChartData = () => {
      const dates = [];
      for (let i = 6; i >= 0; i--) {
          const d = new Date();
          d.setDate(d.getDate() - i);
          dates.push({ date: `${d.getMonth()+1}-${d.getDate()}`, count: 0 });
      }
      return dates;
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
      return (
          <div className="flex h-[50vh] items-center justify-center text-slate-500 animate-pulse gap-2">
              <RefreshCw className="animate-spin" /> 正在连接 Emby...
          </div>
      );
  }

  if (error) {
      return (
          <div className="flex flex-col h-[50vh] items-center justify-center text-slate-500 gap-4">
              <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-xl flex items-center gap-3 text-red-600 dark:text-red-400">
                  <AlertCircle />
                  <span>{error}</span>
              </div>
              <button onClick={fetchData} className="px-4 py-2 bg-slate-200 dark:bg-slate-700 rounded-lg hover:bg-slate-300 transition">重试</button>
          </div>
      );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      
      {/* 1. 顶部欢迎栏 */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white tracking-tight">仪表盘</h2>
          <div className="flex items-center gap-2 mt-1">
             <span className="flex w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
             <p className="text-slate-500 dark:text-slate-400 text-sm">
                已连接至 {stats.serverName} (v{stats.version})
             </p>
          </div>
        </div>
        <button onClick={fetchData} className="flex items-center gap-2 text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition px-3 py-1.5 rounded-full text-slate-600 dark:text-slate-300">
          <RefreshCw size={14} />
          <span>刷新数据</span>
        </button>
      </div>

      {/* 2. 核心指标卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          icon={<Film size={20} />} 
          label="电影收藏" 
          value={stats.movieCount.toLocaleString()} 
          trend="Movies" 
          color="bg-blue-500" 
        />
        <StatCard 
          icon={<Tv size={20} />} 
          label="剧集总数" 
          value={stats.seriesCount.toLocaleString()} 
          trend={`${stats.episodeCount} Episodes`} 
          color="bg-purple-500" 
        />
        <StatCard 
          icon={<Play size={20} />} 
          label="正在播放" 
          value={stats.activeSessions.toString()} 
          trend="Active Sessions" 
          color={stats.activeSessions > 0 ? "bg-green-500" : "bg-slate-400"} 
          animate={stats.activeSessions > 0}
        />
        <StatCard 
          icon={<Server size={20} />} 
          label="服务器状态" 
          value="Online" 
          trend={stats.version} 
          color="bg-orange-500" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* 3. 观影趋势图表 (Playback Reporting 数据) */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 rounded-lg">
                <Activity size={20} />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-white">
                 近7天播放趋势
              </h3>
            </div>
             <div className="text-xs text-slate-400">
                {chartData.every(d => d.count === 0) ? '(需安装 Playback Reporting 插件)' : '来源: Playback Reporting'}
             </div>
          </div>
          
          {/* CSS 柱状图 */}
          <div className="h-64 flex items-end justify-between gap-2 md:gap-4 px-2">
            {chartData.map((item, index) => {
              // 简单的归一化计算，防止除以0
              const max = chartMax || 1; 
              const heightPercent = Math.max((item.count / max) * 100, 5); // 最小高度5%
              
              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-2 group cursor-pointer">
                  <div className="relative w-full bg-slate-100 dark:bg-slate-700/50 rounded-t-xl overflow-hidden h-full flex items-end">
                    <div 
                      className="w-full bg-gradient-to-t from-indigo-600 to-blue-500 opacity-80 group-hover:opacity-100 transition-all duration-500 ease-out rounded-t-lg relative"
                      style={{ height: `${heightPercent}%` }}
                    >
                      {/* Tooltip */}
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                        {item.count} 次播放
                      </div>
                    </div>
                  </div>
                  <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{item.date}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* 4. 最近入库列表 (Real Data) */}
        <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm flex flex-col">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-pink-100 dark:bg-pink-500/20 text-pink-600 dark:text-pink-400 rounded-lg">
              <TrendingUp size={20} />
            </div>
            <h3 className="font-bold text-slate-800 dark:text-white">最近入库</h3>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1 custom-scrollbar">
            {recentItems.length === 0 ? (
                <div className="text-center text-slate-400 py-10 text-sm">暂无数据</div>
            ) : recentItems.map((media, idx) => (
              <div key={idx} className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors border border-transparent hover:border-slate-100 dark:hover:border-slate-700">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${media.type === 'Movie' ? 'bg-blue-100 text-blue-600' : 'bg-purple-100 text-purple-600'}`}>
                  {media.type === 'Movie' ? <Film size={18} /> : <Tv size={18} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-sm text-slate-800 dark:text-slate-200 truncate">{media.seriesName || media.name}</div>
                  {media.seriesName && <div className="text-xs text-slate-500 truncate">{media.name}</div>}
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    {media.date}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// 统计卡片组件
const StatCard = ({ icon, label, value, trend, color, animate }: any) => (
  <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group">
    <div className="flex items-start justify-between mb-4">
      <div className={`p-3 rounded-xl text-white shadow-lg shadow-slate-200 dark:shadow-none ${color} group-hover:scale-110 transition-transform duration-300 ${animate ? 'animate-pulse' : ''}`}>
        {icon}
      </div>
      <span className="text-xs font-bold text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-900/50 px-2 py-1 rounded-full">{trend}</span>
    </div>
    <div>
      <div className="text-2xl font-bold text-slate-800 dark:text-white mb-1">{value}</div>
      <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">{label}</div>
    </div>
  </div>
);
