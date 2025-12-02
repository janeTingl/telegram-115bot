import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, FileText, Filter, Clock, AlertTriangle, Info, X, Check, Search, Trash2
} from 'lucide-react';

interface LogEntry {
  id: number;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG';
  timestamp: string;
  message: string;
}

export const LogsView: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filterLevel, setFilterLevel] = useState<'ALL' | 'ERROR' | 'WARNING'>('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  // 模拟日志数据（实际应从后端获取）
  const mockLogs: LogEntry[] = [
    { id: 1, level: 'INFO', timestamp: '11-30 10:00:00', message: 'Bot 进程启动成功，正在连接 Telegram API...' },
    { id: 2, level: 'WARNING', timestamp: '11-30 10:05:30', message: 'TMDB API Key 长度不足，将使用备用背景图。' },
    { id: 3, level: 'ERROR', timestamp: '11-30 10:08:15', message: 'Database connection failed: FileNotFoundError: secrets.db' },
    { id: 4, level: 'INFO', timestamp: '11-30 10:15:00', message: '配置管理器初始化完毕，安全层已就绪。' },
    { id: 5, level: 'ERROR', timestamp: '11-30 10:22:10', message: 'IndentationError: expected an indented block after if statement...' },
    // ... 更多日志
  ];

  // 实际的数据获取函数 (需要后端实现 /api/logs 接口)
  const fetchLogs = async () => {
    setIsLoading(true);
    // 假设后端接口返回的是 JSON 格式的日志列表
    await new Promise(r => setTimeout(r, 800)); // 模拟网络延迟
    
    // TODO: 替换为实际的 fetch 调用，例如：
    // const res = await fetch('/api/logs');
    // const data = await res.json();
    // setLogs(data);

    setLogs(mockLogs.slice().reverse()); // 演示用，倒序显示最新日志
    setIsLoading(false);
  };

  useEffect(() => {
    fetchLogs();
    // 自动刷新
    const interval = setInterval(fetchLogs, 60000);
    return () => clearInterval(interval);
  }, []);
  
  // 过滤和搜索逻辑
  const filteredLogs = logs
    .filter(log => filterLevel === 'ALL' || log.level === filterLevel)
    .filter(log => log.message.toLowerCase().includes(searchTerm.toLowerCase()));

  // 渲染日志等级图标
  const LogIcon = ({ level }: { level: LogEntry['level'] }) => {
    const classes = {
      'INFO': 'bg-blue-100 text-blue-600',
      'WARNING': 'bg-yellow-100 text-yellow-600',
      'ERROR': 'bg-red-100 text-red-600',
      'DEBUG': 'bg-slate-100 text-slate-500',
    };
    const Icon = {
      'INFO': Info, 'WARNING': AlertTriangle, 'ERROR': XCircle, 'DEBUG': Check
    }[level];
    
    return (
      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${classes[level]} flex items-center gap-1.5`}>
        <Icon size={14} />
        {level}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      
      {/* 顶部标题栏 */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200/50 dark:border-slate-700/50 pb-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white tracking-tight">运行日志</h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">查看 Bot 程序的运行时状态与错误信息。</p>
        </div>
        <button
          onClick={fetchLogs}
          disabled={isLoading}
          className="group px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-white rounded-xl font-medium flex items-center gap-2 shadow-sm transition-all active:scale-95 disabled:opacity-70"
        >
          {isLoading ? <RefreshCw className="animate-spin" size={16} /> : <RefreshCw size={16} />}
          {isLoading ? '刷新中...' : '刷新日志'}
        </button>
      </div>

      {/* 筛选与搜索区域 */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* 筛选按钮 */}
        <div className="flex gap-2 shrink-0">
          {['ALL', 'ERROR', 'WARNING'].map(level => (
            <button 
              key={level}
              onClick={() => setFilterLevel(level as 'ALL' | 'ERROR' | 'WARNING')}
              className={`px-4 py-2 text-sm rounded-lg font-medium transition-all ${filterLevel === level 
                ? 'bg-blue-600 text-white shadow-md' 
                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'}`}
            >
              {level === 'ALL' ? '全部' : level}
            </button>
          ))}
        </div>
        
        {/* 搜索框 */}
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-3 text-slate-400" />
          <input 
            type="text" 
            placeholder="搜索关键词..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-blue-500 outline-none text-sm"
          />
        </div>
        
        {/* 清理按钮 */}
        <button 
          onClick={() => setLogs([])}
          className="px-4 py-2 text-sm rounded-xl font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all flex items-center gap-2"
        >
          <Trash2 size={16} />
          清空显示
        </button>
      </div>

      {/* 日志内容区域 */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-lg overflow-hidden flex-1 min-h-[50vh]">
        <div className="h-full max-h-[70vh] overflow-y-auto font-mono text-sm">
          {filteredLogs.length === 0 ? (
            <div className="text-center text-slate-400 py-10">暂无日志或筛选结果为空</div>
          ) : (
            filteredLogs.map((log) => (
              <div 
                key={log.id} 
                className="flex gap-4 p-4 border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors text-xs"
              >
                <div className="w-24 shrink-0 text-slate-500 dark:text-slate-400 font-medium">
                  {log.timestamp}
                </div>
                <div className="w-24 shrink-0">
                  <LogIcon level={log.level} />
                </div>
                <div className="flex-1 whitespace-pre-wrap text-slate-700 dark:text-slate-300">
                  {log.message}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
